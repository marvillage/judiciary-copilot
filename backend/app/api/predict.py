from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.graph.client import graph
from app.ml.pendency.predict import MODEL_DIR, load_model, predict_cnr

router = APIRouter(prefix="/predict", tags=["predict"])


def model_ready() -> bool:
    return (Path(MODEL_DIR) / "median.ubj").exists()


@router.get("/disposal/{cnr}")
def disposal(cnr: str):
    if not model_ready():
        raise HTTPException(503, "Pendency model not trained yet. Run: uv run python -m app.ml.pendency.train")
    result = predict_cnr(cnr)
    if result is None:
        raise HTTPException(404, f"No case with CNR {cnr} in the graph.")
    return result


@router.get("/disposal")
def disposal_batch(status: str = "pending", limit: int = 20):
    if not model_ready():
        raise HTTPException(503, "Pendency model not trained yet. Run: uv run python -m app.ml.pendency.train")
    cnrs = [r["cnr"] for r in graph.run("MATCH (c:Case {status: $status}) WHERE c.filing_date IS NOT NULL RETURN c.cnr AS cnr LIMIT $limit", status=status, limit=limit)]
    return [predict_cnr(c) for c in cnrs]


@router.get("/model")
def model_info():
    if not model_ready():
        return {"trained": False}
    m = load_model()
    return {"trained": True, "metrics": m.metrics, "features": m.enc.feature_names, "top_sections": m.enc.top_sections}
