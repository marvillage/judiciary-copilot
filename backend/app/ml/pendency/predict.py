import argparse
import json
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from app.ml.pendency.data import fetch_case, similar_cases_benchmark
from app.ml.pendency.features import Encoders, build_matrix, unlog

MODEL_DIR = Path("models/pendency")


class PendencyModel:
    def __init__(self, model_dir: Path = MODEL_DIR) -> None:
        self.dir = model_dir
        self.median = xgb.Booster()
        self.median.load_model(model_dir / "median.ubj")
        self.low = xgb.Booster()
        self.low.load_model(model_dir / "low.ubj")
        self.high = xgb.Booster()
        self.high.load_model(model_dir / "high.ubj")
        self.enc = Encoders(**joblib.load(model_dir / "encoders.joblib"))
        self.metrics = json.loads((model_dir / "metrics.json").read_text()) if (model_dir / "metrics.json").exists() else {}

    def predict_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        x = build_matrix(df, self.enc)
        d = xgb.DMatrix(x, enable_categorical=True)
        med = unlog(self.median.predict(d))
        low = np.minimum(unlog(self.low.predict(d)), med)
        high = np.maximum(unlog(self.high.predict(d)), med)
        return pd.DataFrame({"pred_days": med, "low_days": low, "high_days": high}, index=df.index)

    def predict_case(self, case: dict) -> dict:
        df = pd.DataFrame([case])
        pred = self.predict_frame(df).iloc[0]
        elapsed = None
        if case.get("filing_date") and case.get("status") == "pending":
            elapsed = int((pd.Timestamp.today().normalize() - pd.to_datetime(case["filing_date"])).days)
        benchmark = similar_cases_benchmark(case.get("court"), case.get("case_type"))
        return {
            "cnr": case.get("cnr"),
            "status": case.get("status"),
            "court": case.get("court_name") or case.get("court"),
            "case_type": case.get("case_type"),
            "filing_date": case.get("filing_date"),
            "predicted_days": int(round(pred["pred_days"])),
            "predicted_years": round(float(pred["pred_days"]) / 365.25, 2),
            "range_80_days": [int(round(pred["low_days"])), int(round(pred["high_days"]))],
            "range_80_years": [round(float(pred["low_days"]) / 365.25, 2), round(float(pred["high_days"]) / 365.25, 2)],
            "days_elapsed": elapsed,
            "benchmark_same_court": benchmark,
            "features": {
                "sections": case.get("sections") or [],
                "criminal": case.get("criminal"),
                "first_hearing": case.get("first_hearing"),
                "state": case.get("state"),
                "district": case.get("district"),
            },
            "model": {"trained_at": self.metrics.get("trained_at"), "mae_days": self.metrics.get("mae_days"), "interval_80_coverage_pct": self.metrics.get("interval_80_coverage_pct")},
        }


@lru_cache
def load_model() -> PendencyModel:
    return PendencyModel()


def predict_cnr(cnr: str) -> dict | None:
    case = fetch_case(cnr)
    if not case:
        return None
    return load_model().predict_case(case)


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict time to disposal for a case in the graph.")
    parser.add_argument("--cnr", required=True)
    args = parser.parse_args()
    result = predict_cnr(args.cnr)
    if result is None:
        raise SystemExit(f"No case with CNR {args.cnr} in the graph.")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
