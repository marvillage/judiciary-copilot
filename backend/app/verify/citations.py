import re
from dataclasses import asdict, dataclass

from rapidfuzz import fuzz

from app.graph.client import graph

REPORTER_PATTERNS = [
    re.compile(r"\bA\.?\s?I\.?\s?R\.?\s+(\d{4})\s+S\.?\s?C\.?\s+(\d+)\b"),
    re.compile(r"\((\d{4})\)\s*(\d+)\s+S\.?\s?C\.?\s?C\.?\s+(\d+)\b"),
    re.compile(r"\[(\d{4})\]\s*(\d+)\s+S\.?\s?C\.?\s?R\.?\s+(\d+)\b"),
    re.compile(r"\((\d{4})\)\s*(\d+)\s+S\.?\s?C\.?\s?R\.?\s+(\d+)\b"),
    re.compile(r"\b(\d{4})\s+SCC\s+OnLine\s+SC\s+(\d+)\b", re.IGNORECASE),
    re.compile(r"\b(\d{4})\s+INSC\s+(\d+)\b"),
    re.compile(r"\bA\.?\s?I\.?\s?R\.?\s+(\d{4})\s+([A-Z][a-z]+\.?)\s+(\d+)\b"),
]

PARTY = r"[A-Z][A-Za-z\.\-&'@]*(?:\s+(?:[A-Z][A-Za-z\.\-&'@]*|of|the|and|&|@|through|ors\.?|anr\.?)){0,9}"
CASE_NAME = re.compile(rf"\b({PARTY})\s+(?:v(?:s)?\.?|versus)\s+({PARTY})")


@dataclass
class CitationCheck:
    raw: str
    kind: str
    status: str
    judgment_id: str | None = None
    matched_title: str | None = None
    matched_citation: str | None = None
    confidence: float = 0.0


def extract_citations(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    for pat in REPORTER_PATTERNS:
        for m in pat.finditer(text):
            raw = normalise_ws(m.group(0))
            if raw not in seen:
                seen.add(raw)
                found.append((raw, "reporter"))
    for m in CASE_NAME.finditer(text):
        raw = normalise_ws(m.group(0))
        if len(raw) < 8 or raw in seen:
            continue
        seen.add(raw)
        found.append((raw, "case_name"))
    return found


def normalise_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip(" ,;.")


def normalise_citation(raw: str) -> str:
    return re.sub(r"[\s\.]", "", raw).upper().replace("SCCONLINESC", "SCCONLINESC")


def lookup_reporter(raw: str) -> dict | None:
    return graph.run_one(
        """
        MATCH (j:Judgment)
        WHERE j.citation_norm = $norm OR $norm IN coalesce(j.alt_citations_norm, [])
        RETURN j.id AS id, j.title AS title, j.citation AS citation
        LIMIT 1
        """,
        norm=normalise_citation(raw),
    )


def lookup_case_name(raw: str) -> tuple[dict | None, float]:
    words = [w for w in re.split(r"[^A-Za-z]+", raw) if len(w) > 3 and w.lower() not in {"state", "union", "india", "others", "another"}]
    if not words:
        return None, 0.0
    lucene = " AND ".join(words[:5])
    rows = graph.run(
        """
        CALL db.index.fulltext.queryNodes('judgment_text', $q, {limit: 5})
        YIELD node, score
        RETURN node.id AS id, node.title AS title, node.citation AS citation, score
        """,
        q=lucene,
    )
    best, best_score = None, 0.0
    for r in rows:
        s = fuzz.token_set_ratio(raw.lower(), (r["title"] or "").lower()) / 100.0
        if s > best_score:
            best, best_score = r, s
    return best, best_score


def verify_text(text: str, min_confidence: float = 0.8) -> dict:
    checks: list[CitationCheck] = []
    for raw, kind in extract_citations(text):
        if kind == "reporter":
            hit = lookup_reporter(raw)
            if hit:
                checks.append(CitationCheck(raw, kind, "verified", hit["id"], hit["title"], hit["citation"], 1.0))
            else:
                checks.append(CitationCheck(raw, kind, "not_found"))
        else:
            hit, score = lookup_case_name(raw)
            if hit and score >= min_confidence:
                checks.append(CitationCheck(raw, kind, "verified", hit["id"], hit["title"], hit["citation"], round(score, 3)))
            elif hit:
                checks.append(CitationCheck(raw, kind, "ambiguous", hit["id"], hit["title"], hit["citation"], round(score, 3)))
            else:
                checks.append(CitationCheck(raw, kind, "not_found"))

    unverified = [c for c in checks if c.status != "verified"]
    return {
        "passed": not unverified,
        "total": len(checks),
        "verified": len(checks) - len(unverified),
        "checks": [asdict(c) for c in checks],
    }
