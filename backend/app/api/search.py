from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.graph.client import graph
from app.retrieval.hybrid import SearchFilters, hybrid_search
from app.verify.citations import verify_text
from app.verify.statutes import map_section, parse_section_refs

router = APIRouter(tags=["search"])


@router.get("/search")
def search(
    q: str = Query(..., min_length=3),
    court: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    sections: str | None = Query(None, description="Comma-separated section keys such as IPC-302,BNS-103"),
    k: int = 10,
):
    keys = [s.strip() for s in sections.split(",") if s.strip()] if sections else parse_section_refs(q)
    return hybrid_search(q, SearchFilters(court=court, year_from=year_from, year_to=year_to, sections=keys), k=k)


@router.get("/judgments/{judgment_id}")
def judgment(judgment_id: str):
    row = graph.run_one(
        """
        MATCH (j:Judgment {id: $id})
        OPTIONAL MATCH (j)-[:CITES]->(cited:Judgment)
        OPTIONAL MATCH (citing:Judgment)-[:CITES]->(j)
        OPTIONAL MATCH (j)-[:INTERPRETS]->(s:Section)
        RETURN j {.id, .title, .date, .year, .court, .citation, .case_id, .petitioner, .respondent, .judges, .author_judge, .disposal, .headnote, .text_path} AS judgment,
               collect(DISTINCT cited {.id, .title, .citation}) AS cites,
               collect(DISTINCT citing {.id, .title, .citation}) AS cited_by,
               collect(DISTINCT s {.key, .act, .number, .title}) AS sections
        """,
        id=judgment_id,
    )
    if not row:
        raise HTTPException(404, "judgment not found")
    return row


class VerifyBody(BaseModel):
    text: str
    min_confidence: float = 0.8


@router.post("/verify/citations")
def verify(body: VerifyBody):
    return verify_text(body.text, body.min_confidence)


@router.get("/statutes/map")
def statute_map(act: str, section: str):
    return map_section(act, section)


@router.get("/statutes/parse")
def statute_parse(text: str):
    keys = parse_section_refs(text)
    return {"keys": keys, "mapped": [map_section(*k.split("-", 1)) for k in keys]}


@router.get("/statutes/{act}")
def statute_sections(act: str, q: str | None = None, limit: int = 100):
    return graph.run(
        """
        MATCH (a:Act {id: $act})-[:HAS_SECTION]->(s:Section)
        WHERE $q IS NULL OR toLower(s.title) CONTAINS toLower($q) OR s.number STARTS WITH $q
        OPTIONAL MATCH (s)-[:REPLACED_BY]->(n:Section)
        RETURN s {.key, .number, .title, .max_punishment_years, .punishment} AS section, collect(n {.key, .number, .title}) AS replaced_by
        ORDER BY toInteger(apoc.text.regexGroups(s.number, '^(\\d+)')[0][1]), s.number LIMIT $limit
        """,
        act=act.upper() if act.lower() in {"ipc", "bns", "iea", "bsa"} else {"crpc": "CrPC", "bnss": "BNSS"}.get(act.lower(), act),
        q=q,
        limit=limit,
    )
