import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, dashboard, matters, predict, review, search
from app.graph.client import graph
from app.graph.schema import ensure_schema
from app.retrieval.embeddings import embedding_dims
from app.tracker import scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("casegraph")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if graph.verify():
        ensure_schema(graph, embedding_dims())
        scheduler.start()
        log.info("schema ensured, scheduler started")
    else:
        log.warning("Neo4j not reachable at startup; admin/health will report it")
    yield
    scheduler.stop()
    graph.close()


app = FastAPI(title="CaseGraph API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(dashboard.router)
app.include_router(matters.router)
app.include_router(matters.alerts_router)
app.include_router(search.router)
app.include_router(review.router)
app.include_router(predict.router)


@app.get("/")
def root():
    return {"name": "CaseGraph API", "docs": "/docs"}
