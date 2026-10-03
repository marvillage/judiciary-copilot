from contextlib import contextmanager
from typing import Any

from neo4j import GraphDatabase, Session

from app.config import settings


class Graph:
    def __init__(self) -> None:
        self.driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))

    def close(self) -> None:
        self.driver.close()

    def verify(self) -> bool:
        try:
            self.driver.verify_connectivity()
            return True
        except Exception:
            return False

    @contextmanager
    def session(self):
        session: Session = self.driver.session()
        try:
            yield session
        finally:
            session.close()

    def run(self, cypher: str, **params: Any) -> list[dict[str, Any]]:
        with self.session() as s:
            return [r.data() for r in s.run(cypher, **params)]

    def run_one(self, cypher: str, **params: Any) -> dict[str, Any] | None:
        rows = self.run(cypher, **params)
        return rows[0] if rows else None

    def write_batches(self, cypher: str, rows: list[dict[str, Any]], batch_size: int = 2000) -> int:
        written = 0
        with self.session() as s:
            for i in range(0, len(rows), batch_size):
                batch = rows[i : i + batch_size]
                s.execute_write(lambda tx: tx.run(cypher, rows=batch).consume())
                written += len(batch)
        return written


graph = Graph()
