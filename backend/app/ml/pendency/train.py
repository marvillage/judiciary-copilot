import argparse
import json
import logging
import time
from dataclasses import asdict
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, median_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from app.ml.pendency.data import fetch_training_frame
from app.ml.pendency.features import Encoders, build_matrix, clean_training_frame, fit_encoders, log_target, unlog

log = logging.getLogger("casegraph.pendency.train")

MODEL_DIR = Path("models/pendency")
QUANTILES = {"low": 0.08, "high": 0.92}


def base_params(device: str, seed: int) -> dict:
    return {
        "tree_method": "hist",
        "device": device,
        "max_depth": 8,
        "learning_rate": 0.05,
        "subsample": 0.85,
        "colsample_bytree": 0.8,
        "min_child_weight": 5,
        "reg_lambda": 2.0,
        "max_cat_to_onehot": 1,
        "max_bin": 256,
        "seed": seed,
    }


def fit_booster(params: dict, dtrain: xgb.DMatrix, dvalid: xgb.DMatrix, rounds: int, early_stop: int) -> xgb.Booster:
    return xgb.train(
        params,
        dtrain,
        num_boost_round=rounds,
        evals=[(dvalid, "valid")],
        early_stopping_rounds=early_stop,
        verbose_eval=100,
    )


def evaluate(median_days: np.ndarray, low_days: np.ndarray, high_days: np.ndarray, y_days: np.ndarray) -> dict:
    inside = (y_days >= low_days) & (y_days <= high_days)
    return {
        "n_test": int(len(y_days)),
        "mae_days": float(mean_absolute_error(y_days, median_days)),
        "median_ae_days": float(median_absolute_error(y_days, median_days)),
        "r2_log": float(r2_score(np.log1p(y_days), np.log1p(median_days))),
        "within_90_days_pct": float(np.mean(np.abs(y_days - median_days) <= 90) * 100),
        "within_180_days_pct": float(np.mean(np.abs(y_days - median_days) <= 180) * 100),
        "interval_80_coverage_pct": float(inside.mean() * 100),
        "interval_80_mean_width_days": float(np.mean(high_days - low_days)),
        "baseline_mae_days_global_median": float(mean_absolute_error(y_days, np.full_like(y_days, np.median(y_days)))),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the CaseGraph time-to-disposal model (XGBoost, median + 80% interval).")
    parser.add_argument("--rows", type=int, default=200000, help="max disposed cases to pull from Neo4j")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--rounds", type=int, default=3000)
    parser.add_argument("--early-stop", type=int, default=100)
    parser.add_argument("--device", default="cuda", choices=["cuda", "cpu"], help="cuda uses the GPU if XGBoost can see it")
    parser.add_argument("--top-sections", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default=str(MODEL_DIR))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)
    t0 = time.time()

    raw = fetch_training_frame(args.rows)
    log.info("pulled %d disposed cases from the graph", len(raw))
    df = clean_training_frame(raw)
    log.info("kept %d after cleaning (0..6000 days, dated)", len(df))
    if len(df) < 500:
        raise SystemExit("Not enough disposed cases. Load more with POST /admin/load/ecourts?rows=200000 first.")

    train_df, test_df = train_test_split(df, test_size=args.test_size, random_state=args.seed)
    enc = fit_encoders(train_df, args.top_sections)
    x_train, x_test = build_matrix(train_df, enc), build_matrix(test_df, enc)
    y_train, y_test = log_target(train_df["days"]), log_target(test_df["days"])
    log.info("features: %d columns, %d top sections", x_train.shape[1], len(enc.top_sections))

    x_fit, x_val, y_fit, y_val = train_test_split(x_train, y_train, test_size=0.1, random_state=args.seed)
    dfit = xgb.DMatrix(x_fit, label=y_fit, enable_categorical=True)
    dval = xgb.DMatrix(x_val, label=y_val, enable_categorical=True)
    dtest = xgb.DMatrix(x_test, enable_categorical=True)

    device = args.device
    try:
        xgb.train({**base_params(device, args.seed), "objective": "reg:squarederror"}, dfit, num_boost_round=1)
    except xgb.core.XGBoostError as exc:
        log.warning("device %s unavailable (%s); falling back to cpu", device, str(exc).splitlines()[0])
        device = "cpu"

    log.info("training median model on %s", device)
    median_model = fit_booster({**base_params(device, args.seed), "objective": "reg:squarederror"}, dfit, dval, args.rounds, args.early_stop)

    quantile_models: dict[str, xgb.Booster] = {}
    for name, alpha in QUANTILES.items():
        log.info("training %s quantile model (alpha=%.2f)", name, alpha)
        quantile_models[name] = fit_booster(
            {**base_params(device, args.seed), "objective": "reg:quantileerror", "quantile_alpha": alpha},
            dfit,
            dval,
            args.rounds,
            args.early_stop,
        )

    median_days = unlog(median_model.predict(dtest, iteration_range=(0, median_model.best_iteration + 1)))
    low_days = unlog(quantile_models["low"].predict(dtest, iteration_range=(0, quantile_models["low"].best_iteration + 1)))
    high_days = unlog(quantile_models["high"].predict(dtest, iteration_range=(0, quantile_models["high"].best_iteration + 1)))
    low_days, high_days = np.minimum(low_days, median_days), np.maximum(high_days, median_days)
    metrics = evaluate(median_days, low_days, high_days, test_df["days"].to_numpy(dtype="float64"))
    metrics.update(
        {
            "n_train": int(len(train_df)),
            "device": device,
            "best_iterations": {"median": int(median_model.best_iteration), **{k: int(m.best_iteration) for k, m in quantile_models.items()}},
            "trained_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "train_seconds": round(time.time() - t0, 1),
            "xgboost": xgb.__version__,
        }
    )

    importance = median_model.get_score(importance_type="gain")
    top_features = sorted(importance.items(), key=lambda kv: kv[1], reverse=True)[:25]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    median_model.save_model(out / "median.ubj")
    for name, model in quantile_models.items():
        model.save_model(out / f"{name}.ubj")
    joblib.dump(asdict(enc), out / "encoders.joblib")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (out / "feature_importance.json").write_text(json.dumps(top_features, indent=2))
    pd.DataFrame(
        {"cnr": test_df["cnr"].to_numpy(), "actual_days": test_df["days"].to_numpy(), "pred_days": median_days.round(), "low_days": low_days.round(), "high_days": high_days.round()}
    ).to_csv(out / "test_predictions.csv", index=False)

    print("\n=== Time-to-disposal model ===")
    for k in ["n_train", "n_test", "mae_days", "median_ae_days", "baseline_mae_days_global_median", "r2_log", "within_90_days_pct", "within_180_days_pct", "interval_80_coverage_pct", "interval_80_mean_width_days", "device", "train_seconds"]:
        v = metrics[k]
        print(f"{k:34s} {v:.1f}" if isinstance(v, float) else f"{k:34s} {v}")
    print("\nTop features by gain:")
    for name, gain in top_features[:12]:
        print(f"  {name:32s} {gain:,.1f}")
    print(f"\nSaved to {out.resolve()}")


if __name__ == "__main__":
    main()
