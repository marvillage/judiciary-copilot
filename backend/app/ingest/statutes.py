import csv
from pathlib import Path

from app.config import settings
from app.graph.client import graph

ACT_CODES = {"ipc": "IPC", "bns": "BNS", "crpc": "CrPC", "bnss": "BNSS", "iea": "IEA", "bsa": "BSA"}

ACT_NAMES = {
    "IPC": ("Indian Penal Code", 1860),
    "BNS": ("Bharatiya Nyaya Sanhita", 2023),
    "CrPC": ("Code of Criminal Procedure", 1973),
    "BNSS": ("Bharatiya Nagarik Suraksha Sanhita", 2023),
    "IEA": ("Indian Evidence Act", 1872),
    "BSA": ("Bharatiya Sakshya Adhiniyam", 2023),
}

UPSERT_ACTS = """
UNWIND $rows AS r
MERGE (a:Act {id: r.id}) SET a.name = r.name, a.year = r.year
"""

UPSERT_SECTIONS = """
UNWIND $rows AS r
MERGE (s:Section {key: r.key})
SET s.act = r.act, s.number = r.number, s.title = coalesce(r.title, s.title)
WITH s, r
MATCH (a:Act {id: r.act})
MERGE (a)-[:HAS_SECTION]->(s)
"""

UPSERT_MAPPINGS = """
UNWIND $rows AS r
MATCH (old:Section {key: r.from_key}), (new:Section {key: r.to_key})
MERGE (old)-[m:REPLACED_BY]->(new)
SET m.relation = r.relation, m.score = r.score, m.source = r.source
"""

UPSERT_PUNISHMENTS = """
UNWIND $rows AS r
MATCH (s:Section {key: r.key})
SET s.max_punishment_years = r.max_years, s.punishment = r.punishment, s.bailable = r.bailable, s.cognizable = r.cognizable
"""


def statutes_dir() -> Path:
    return settings.data_dir / "statutes"


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mapping_rows(path: Path, source: str) -> list[dict]:
    rows = []
    for r in read_csv(path):
        from_act, to_act = ACT_CODES.get(r["from_act"].lower()), ACT_CODES.get(r["to_act"].lower())
        if not from_act or not to_act:
            continue
        rows.append(
            {
                "from_act": from_act,
                "from_num": r["from_num"].strip().upper(),
                "from_title": (r.get("from_heading") or "").strip() or None,
                "to_act": to_act,
                "to_num": r["to_num"].strip().upper(),
                "to_title": (r.get("to_heading") or "").strip() or None,
                "relation": (r.get("relation") or "mapped").strip(),
                "score": float(r["score"]) if r.get("score") else None,
                "source": r.get("source") or source,
            }
        )
    return rows


def load_statutes() -> dict:
    base = mapping_rows(statutes_dir() / "indiacode_mapping.csv", "IndiaCode by eCourtsIndia (CC BY 4.0, computed)")
    overrides = mapping_rows(statutes_dir() / "overrides.csv", "BPRD comparison table")

    keyed = {(r["from_act"], r["from_num"]): r for r in base}
    for r in overrides:
        keyed[(r["from_act"], r["from_num"])] = r
    mappings = list(keyed.values())

    sections: dict[str, dict] = {}
    for r in mappings:
        for act, num, title in ((r["from_act"], r["from_num"], r["from_title"]), (r["to_act"], r["to_num"], r["to_title"])):
            key = f"{act}-{num}"
            sections.setdefault(key, {"key": key, "act": act, "number": num, "title": title})
            if title and not sections[key]["title"]:
                sections[key]["title"] = title

    punishments = []
    for r in read_csv(statutes_dir() / "punishments.csv"):
        act = ACT_CODES[r["act"].lower()]
        key = f"{act}-{r['num'].strip().upper()}"
        sections.setdefault(key, {"key": key, "act": act, "number": r["num"].strip().upper(), "title": None})
        max_years = 20.0 if r["max_punishment_years"] == "life" else float(r["max_punishment_years"])
        punishments.append(
            {"key": key, "max_years": max_years, "punishment": r["punishment"], "bailable": r["bailable"] == "yes", "cognizable": r["cognizable"] == "yes"}
        )

    graph.write_batches(UPSERT_ACTS, [{"id": code, "name": name, "year": year} for code, (name, year) in ACT_NAMES.items()])
    graph.write_batches(UPSERT_SECTIONS, list(sections.values()))
    graph.write_batches(
        UPSERT_MAPPINGS,
        [
            {"from_key": f"{r['from_act']}-{r['from_num']}", "to_key": f"{r['to_act']}-{r['to_num']}", "relation": r["relation"], "score": r["score"], "source": r["source"]}
            for r in mappings
        ],
    )
    graph.write_batches(UPSERT_PUNISHMENTS, punishments)
    return {"acts": len(ACT_NAMES), "sections": len(sections), "mappings": len(mappings), "overrides": len(overrides), "punishments": len(punishments)}
