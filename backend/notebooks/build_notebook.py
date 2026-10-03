from pathlib import Path

import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []


def md(text: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(text.strip()))


def code(text: str) -> None:
    cells.append(nbf.v4.new_code_cell(text.strip()))


md("""
# CaseGraph - Feature 9: time to disposal (XGBoost)

Predict how many days a case will take from filing to disposal, with an 80% confidence range.

What this notebook does, top to bottom:

1. Pull disposed cases from Neo4j
2. Clean them and look at the target
3. Build features that are known at filing time (no leakage)
4. Train three XGBoost models: median, 10th percentile, 90th percentile
5. Evaluate against a naive baseline
6. Save the model where the API expects it, then predict a pending case

Run every cell in order (Run > Run All Cells). Set `ROWS` smaller for a quick run.
""")

code("""
import os, sys, json, time
from pathlib import Path

root = Path.cwd()
while not (root / "pyproject.toml").exists() and root != root.parent:
    root = root.parent
os.chdir(root)
sys.path.insert(0, str(root))
print("working dir:", root)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, median_absolute_error, r2_score

from app.ml.pendency.data import fetch_training_frame, fetch_case
from app.ml.pendency.features import build_matrix, clean_training_frame, fit_encoders, log_target, unlog
from app.ml.pendency.predict import PendencyModel

ROWS = int(os.environ.get("PENDENCY_ROWS", 200_000))
ROUNDS = int(os.environ.get("PENDENCY_ROUNDS", 3000))
DEVICE = os.environ.get("PENDENCY_DEVICE", "cuda")
OUT = Path("models/pendency")
GOLD, INK, MUTED = "#c99a12", "#1d1d1d", "#8f887b"
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25})
print(f"ROWS={ROWS} ROUNDS={ROUNDS} DEVICE={DEVICE} xgboost={xgb.__version__}")
""")

md("## 1. Pull disposed cases from the graph")

code("""
t = time.time()
raw = fetch_training_frame(ROWS)
print(f"{len(raw):,} disposed cases pulled in {time.time()-t:.1f}s")
raw.head()
""")

md("""
## 2. Clean and look at the target

The target is `days` = decision date minus filing date. We drop negative values (bad data) and anything above 6000 days.
""")

code("""
df = clean_training_frame(raw)
print(f"kept {len(df):,} of {len(raw):,}")
df["days"].describe().round(0)
""")

code("""
fig, ax = plt.subplots(figsize=(8, 3.2))
ax.hist(df["days"], bins=80, color=GOLD, edgecolor="white", linewidth=0.4)
ax.set_xlabel("days from filing to disposal"); ax.set_ylabel("cases")
ax.set_title("Most cases close within two years; a long tail runs past ten")
plt.show()
""")

md("""
Which states and case types take longest? This is the intuition the model has to learn.
""")

code("""
by_state = df.groupby("state")["days"].median().sort_values(ascending=False).head(12)
fig, ax = plt.subplots(figsize=(8, 3.6))
ax.barh(by_state.index[::-1], by_state.values[::-1], color=GOLD, height=0.6)
ax.set_xlabel("median days to disposal"); ax.set_title("Median disposal time by state (top 12)")
plt.show()

df.groupby("case_type")["days"].agg(n="size", median_days="median").query("n >= 200").sort_values("median_days", ascending=False).head(10)
""")

md("""
## 3. Features known at filing time

Anything that only becomes known later (current stage, disposition, last or next hearing) is excluded on purpose. Using it would make the model look great in a notebook and useless in production.

- Categorical: state, district, court, case type, judge position (XGBoost handles these natively)
- Numeric: filing year, month, weekday, gap to first hearing, criminal flag, number of sections, IPC and CrPC flags, advocate present on each side, whether the state or a public body is a party, bailable IPC flag, number of IPC sections
- Indicators for the 40 most common sections
""")

code("""
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
enc = fit_encoders(train_df, top_k_sections=40)
X_train, X_test = build_matrix(train_df, enc), build_matrix(test_df, enc)
y_train, y_test = log_target(train_df["days"]), log_target(test_df["days"])
print(f"train {X_train.shape}  test {X_test.shape}")
print("top sections:", enc.top_sections[:10])
X_train.head()
""")

md("""
## 4. Train

We predict `log(1 + days)` because the target is heavy-tailed. Three boosters:

- `median`: squared error on the log target
- `low`: quantile regression at alpha 0.08
- `high`: quantile regression at alpha 0.92 (slightly wider than 0.1/0.9 because the first run covered only 76%)

Early stopping on a 10% validation slice picks the number of trees.
""")

code("""
X_fit, X_val, y_fit, y_val = train_test_split(X_train, y_train, test_size=0.1, random_state=42)
dfit = xgb.DMatrix(X_fit, label=y_fit, enable_categorical=True)
dval = xgb.DMatrix(X_val, label=y_val, enable_categorical=True)
dtest = xgb.DMatrix(X_test, enable_categorical=True)

params = dict(tree_method="hist", device=DEVICE, max_depth=8, learning_rate=0.05, subsample=0.85,
              colsample_bytree=0.8, min_child_weight=5, reg_lambda=2.0, max_cat_to_onehot=1, max_bin=256, seed=42)

try:
    xgb.train({**params, "objective": "reg:squarederror"}, dfit, num_boost_round=1)
except xgb.core.XGBoostError as exc:
    print("GPU not usable, using CPU:", str(exc).splitlines()[0]); params["device"] = "cpu"

def fit(objective, **extra):
    return xgb.train({**params, "objective": objective, **extra}, dfit, num_boost_round=ROUNDS,
                     evals=[(dval, "valid")], early_stopping_rounds=100, verbose_eval=200)

t = time.time()
median_model = fit("reg:squarederror")
low_model = fit("reg:quantileerror", quantile_alpha=0.08)
high_model = fit("reg:quantileerror", quantile_alpha=0.92)
print(f"trained in {time.time()-t:.0f}s; best iterations: {median_model.best_iteration}, {low_model.best_iteration}, {high_model.best_iteration}")
""")

md("""
## 5. Evaluate

The baseline is "always predict the overall median". A useful model must beat it clearly. Coverage of the 80% range should sit near 80%.
""")

code("""
def predict(model, d):
    return unlog(model.predict(d, iteration_range=(0, model.best_iteration + 1)))

y_days = test_df["days"].to_numpy(dtype=float)
pred = predict(median_model, dtest)
low = np.minimum(predict(low_model, dtest), pred)
high = np.maximum(predict(high_model, dtest), pred)

metrics = {
    "mae_days": mean_absolute_error(y_days, pred),
    "median_ae_days": median_absolute_error(y_days, pred),
    "baseline_mae_days_global_median": mean_absolute_error(y_days, np.full_like(y_days, np.median(y_days))),
    "r2_log": r2_score(np.log1p(y_days), np.log1p(pred)),
    "within_90_days_pct": np.mean(np.abs(y_days - pred) <= 90) * 100,
    "within_180_days_pct": np.mean(np.abs(y_days - pred) <= 180) * 100,
    "interval_80_coverage_pct": np.mean((y_days >= low) & (y_days <= high)) * 100,
    "interval_80_mean_width_days": np.mean(high - low),
}
pd.Series(metrics).round(1).to_frame("value")
""")

code("""
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].hexbin(y_days, pred, gridsize=45, cmap="YlOrBr", bins="log", mincnt=1)
lim = [0, 4000]; axes[0].plot(lim, lim, color=INK, linewidth=1)
axes[0].set_xlim(lim); axes[0].set_ylim(lim); axes[0].set_xlabel("actual days"); axes[0].set_ylabel("predicted days"); axes[0].set_title("Actual vs predicted")

order = np.argsort(pred)[:: max(1, len(pred) // 400)]
axes[1].fill_between(range(len(order)), low[order], high[order], color=GOLD, alpha=0.25, label="80% range")
axes[1].plot(pred[order], color=GOLD, linewidth=1.5, label="predicted")
axes[1].scatter(range(len(order)), y_days[order], s=6, color=INK, alpha=0.5, label="actual")
axes[1].set_xlabel("test cases sorted by prediction"); axes[1].set_ylabel("days"); axes[1].set_title("Does the range cover reality?"); axes[1].legend(frameon=False)
plt.tight_layout(); plt.show()
""")

md("## 6. What did the model use?")

code("""
gain = pd.Series(median_model.get_score(importance_type="gain")).sort_values(ascending=False).head(20)
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(gain.index[::-1], gain.values[::-1], color=GOLD, height=0.6)
ax.set_xlabel("gain"); ax.set_title("Top 20 features by gain")
plt.show()
""")

md("""
## 7. Save for the API

Same files the training script writes, so `GET /predict/disposal/{cnr}` works after the API restarts.
""")

code("""
import joblib
from dataclasses import asdict
OUT.mkdir(parents=True, exist_ok=True)
median_model.save_model(OUT / "median.ubj"); low_model.save_model(OUT / "low.ubj"); high_model.save_model(OUT / "high.ubj")
joblib.dump(asdict(enc), OUT / "encoders.joblib")
metrics_out = {k: float(v) for k, v in metrics.items()}
metrics_out.update(n_train=int(len(train_df)), n_test=int(len(test_df)), device=params["device"], trained_at=time.strftime("%Y-%m-%dT%H:%M:%S"), xgboost=xgb.__version__, source="notebook")
(OUT / "metrics.json").write_text(json.dumps(metrics_out, indent=2))
(OUT / "feature_importance.json").write_text(json.dumps(gain.round(2).to_dict(), indent=2))
print("saved to", OUT.resolve()); sorted(p.name for p in OUT.iterdir())
""")

md("## 8. Predict a pending case")

code("""
model = PendencyModel(OUT)
case = fetch_case("MHNB030003102010")
result = model.predict_case(case)
print(json.dumps({k: v for k, v in result.items() if k not in ("features",)}, indent=2, default=str))
""")

md("""
## Try next

- Increase `ROWS` after loading more cases (`POST /admin/load/ecourts?rows=300000`).
- Change `max_depth`, `learning_rate` or `top_k_sections` and watch `mae_days` and coverage.
- Order 14 in the build plan adds SHAP explanations on top of this exact model.
""")

nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}}
out = Path(__file__).with_name("pendency_training.ipynb")
nbf.write(nb, out)
print("wrote", out)
