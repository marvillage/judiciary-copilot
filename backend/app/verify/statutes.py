import re

from app.graph.client import graph

ACT_ALIASES = {
    "ipc": "IPC",
    "indian penal code": "IPC",
    "bns": "BNS",
    "bharatiya nyaya sanhita": "BNS",
    "crpc": "CrPC",
    "cr.p.c": "CrPC",
    "code of criminal procedure": "CrPC",
    "bnss": "BNSS",
    "bharatiya nagarik suraksha sanhita": "BNSS",
    "iea": "IEA",
    "evidence act": "IEA",
    "indian evidence act": "IEA",
    "bsa": "BSA",
    "bharatiya sakshya adhiniyam": "BSA",
}

SECTION_REF = re.compile(
    r"\b(?:section|sec\.?|s\.|u/s\.?|under section)\s*(\d+[A-Z]?(?:\(\d+\))?)\s*(?:of\s+(?:the\s+)?)?([A-Za-z\.\s]{2,40}?)(?=[,;\.\)]|\s+and|\s+read|\s*$)",
    re.IGNORECASE,
)


def normalise_act(raw: str) -> str | None:
    key = raw.strip().lower().rstrip(".").replace("  ", " ")
    for alias, code in ACT_ALIASES.items():
        if key == alias or key.startswith(alias + " ") or key.endswith(" " + alias):
            return code
    return None


def section_key(act: str, number: str) -> str:
    return f"{act}-{number.upper().replace(' ', '')}"


def parse_section_refs(text: str) -> list[str]:
    keys: list[str] = []
    for m in SECTION_REF.finditer(text):
        act = normalise_act(m.group(2))
        if act:
            keys.append(section_key(act, m.group(1)))
    return sorted(set(keys))


def map_section(act: str, number: str) -> dict:
    key = section_key(act, number)
    row = graph.run_one(
        """
        MATCH (s:Section {key: $key})
        OPTIONAL MATCH (s)-[:REPLACED_BY]->(new:Section)
        OPTIONAL MATCH (old:Section)-[:REPLACED_BY]->(s)
        RETURN s {.key, .act, .number, .title, .max_punishment_years, .punishment} AS section,
               collect(DISTINCT new {.key, .act, .number, .title}) AS replaced_by,
               collect(DISTINCT old {.key, .act, .number, .title}) AS replaces
        """,
        key=key,
    )
    if not row:
        return {"section": None, "replaced_by": [], "replaces": [], "found": False}
    return {**row, "found": True}


def expand_section_aliases(keys: list[str]) -> list[str]:
    rows = graph.run(
        """
        UNWIND $keys AS key
        MATCH (s:Section {key: key})
        OPTIONAL MATCH (s)-[:REPLACED_BY*0..1]-(alias:Section)
        RETURN DISTINCT coalesce(alias.key, s.key) AS key
        """,
        keys=keys,
    )
    found = {r["key"] for r in rows}
    return sorted(found | set(keys))
