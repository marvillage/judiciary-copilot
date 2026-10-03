from functools import lru_cache

from langchain_ollama import ChatOllama, OllamaEmbeddings

from app.config import settings

EMBED_DIMS = {"bge-m3": 1024, "nomic-embed-text": 768, "mxbai-embed-large": 1024}


@lru_cache
def embedder() -> OllamaEmbeddings:
    return OllamaEmbeddings(model=settings.embed_model, base_url=settings.ollama_base_url)


@lru_cache
def chat_model(temperature: float = 0.2) -> ChatOllama:
    return ChatOllama(model=settings.chat_model, base_url=settings.ollama_base_url, temperature=temperature)


def embedding_dims() -> int:
    return EMBED_DIMS.get(settings.embed_model, 1024)


def embed_texts(texts: list[str]) -> list[list[float]]:
    return embedder().embed_documents(texts)


def embed_query(text: str) -> list[float]:
    return embedder().embed_query(text)
