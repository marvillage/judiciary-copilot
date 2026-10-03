from fastapi import APIRouter, BackgroundTasks

from app.config import settings
from app.graph.client import graph
from app.graph.schema import ensure_schema
from app.ingest.ecourts import load_ecourts
from app.ingest.judgments import embed_judgments, load_judgments
from app.ingest.statutes import load_statutes
from app.retrieval.embeddings import embedding_dims

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/health")
def health():
    return {
        "neo4j": graph.verify(),
        "neo4j_uri": settings.neo4j_uri,
        "embed_model": settings.embed_model,
        "chat_model": settings.chat_model,
        "ollama": settings.ollama_base_url,
    }


@router.post("/schema")
def schema():
    ensure_schema(graph, embedding_dims())
    return {"ok": True, "dims": embedding_dims()}


@router.post("/load/statutes")
def statutes():
    return load_statutes()


@router.post("/load/ecourts")
def ecourts(rows: int | None = None):
    return load_ecourts(rows)


@router.post("/load/judgments", status_code=202)
def judgments(background: BackgroundTasks, rows: int | None = None, year_from: int = 1950, year_to: int = 2025, embed: bool = True):
    background.add_task(load_judgments, rows, year_from, year_to, embed)
    return {"started": True, "rows": rows or settings.judgments_sample_rows, "years": [year_from, year_to]}


@router.post("/embed/judgments", status_code=202)
def embed(background: BackgroundTasks):
    background.add_task(embed_judgments, None)
    return {"started": True}


@router.get("/counts")
def counts():
    return graph.run(
        """
        CALL db.labels() YIELD label
        CALL { WITH label MATCH (n) WHERE label IN labels(n) RETURN count(n) AS c }
        RETURN label, c ORDER BY label
        """
    )
