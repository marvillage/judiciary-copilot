from dataclasses import dataclass, field
from typing import Any

from app.graph.client import graph
from app.retrieval.embeddings import embed_query
from app.verify.statutes import expand_section_aliases

VECTOR_QUERY = """
CALL db.index.vector.queryNodes('judgment_embedding', $k, $vec)
YIELD node, score
WHERE ($court IS NULL OR node.court = $court)
  AND ($year_from IS NULL OR node.year >= $year_from)
  AND ($year_to IS NULL OR node.year <= $year_to)
RETURN node.id AS id, node.title AS title, node.citation AS citation, node.date AS date,
       node.court AS court, node.headnote AS headnote, score
"""

FULLTEXT_QUERY = """
CALL db.index.fulltext.queryNodes('judgment_text', $q, {limit: $k})
YIELD node, score
WHERE ($court IS NULL OR node.court = $court)
  AND ($year_from IS NULL OR node.year >= $year_from)
  AND ($year_to IS NULL OR node.year <= $year_to)
RETURN node.id AS id, node.title AS title, node.citation AS citation, node.date AS date,
       node.court AS court, node.headnote AS headnote, score
"""

SECTION_QUERY = """
UNWIND $keys AS key
MATCH (s:Section {key: key})<-[:INTERPRETS]-(j:Judgment)
WHERE ($court IS NULL OR j.court = $court)
  AND ($year_from IS NULL OR j.year >= $year_from)
  AND ($year_to IS NULL OR j.year <= $year_to)
RETURN j.id AS id, j.title AS title, j.citation AS citation, j.date AS date,
       j.court AS court, j.headnote AS headnote, 1.0 AS score, collect(DISTINCT key) AS matched_sections
LIMIT $k
"""


@dataclass
class SearchFilters:
    court: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    sections: list[str] = field(default_factory=list)


def rrf(rankings: list[list[dict[str, Any]]], k: int = 60) -> list[dict[str, Any]]:
    fused: dict[str, dict[str, Any]] = {}
    for ranking in rankings:
        for rank, row in enumerate(ranking, start=1):
            entry = fused.setdefault(row["id"], {**row, "rrf": 0.0, "sources": []})
            entry["rrf"] += 1.0 / (k + rank)
            entry["sources"].append(row.get("source", "?"))
            if "matched_sections" in row:
                entry["matched_sections"] = row["matched_sections"]
    return sorted(fused.values(), key=lambda r: r["rrf"], reverse=True)


def hybrid_search(query: str, filters: SearchFilters | None = None, k: int = 10) -> dict[str, Any]:
    filters = filters or SearchFilters()
    params = {"k": k * 3, "court": filters.court, "year_from": filters.year_from, "year_to": filters.year_to}

    vector_hits = graph.run(VECTOR_QUERY, vec=embed_query(query), **params)
    for h in vector_hits:
        h["source"] = "vector"

    fulltext_hits = graph.run(FULLTEXT_QUERY, q=lucene_escape(query), **params)
    for h in fulltext_hits:
        h["source"] = "fulltext"

    rankings = [vector_hits, fulltext_hits]
    expanded_sections: list[str] = []
    if filters.sections:
        expanded_sections = expand_section_aliases(filters.sections)
        section_hits = graph.run(SECTION_QUERY, keys=expanded_sections, **params)
        for h in section_hits:
            h["source"] = "section"
        rankings.append(section_hits)

    results = rrf(rankings)[:k]
    return {
        "query": query,
        "filters": {**filters.__dict__, "expanded_sections": expanded_sections},
        "counts": {"vector": len(vector_hits), "fulltext": len(fulltext_hits)},
        "results": results,
    }


def lucene_escape(text: str) -> str:
    specials = '+-&|!(){}[]^"~*?:\\/'
    out = []
    for ch in text:
        out.append(f"\\{ch}" if ch in specials else ch)
    return "".join(out)
