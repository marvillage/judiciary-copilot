import logging
import re
import zipfile
from pathlib import Path

import httpx
import pandas as pd
import pyreadstat

from app.config import settings
from app.graph.client import graph
from app.ingest.sources import UPSERT_CASE

log = logging.getLogger("casegraph.ecourts")

DATAVERSE = "https://dataverse.harvard.edu/api/access/datafile/{id}"
KEY_FILES = {"type_name_key.tab": 10794659, "purpose_name_key.tab": 10794661, "disp_name_key.tab": 10794671}
CASES_FILES = {2010: ("cases_clean_2010.zip", 10794667), 2013: ("cases_clean_2013.zip", 10794665), 2015: ("cases_clean_2015.zip", 10794660)}

SOURCE = "DDL eCourts replication data, Harvard Dataverse doi:10.7910/DVN/GHLGSW (CC0)"

COLUMNS = [
    "ddl_case_id", "state_code", "state_name", "district_code", "district_name", "court_no", "court_name", "cino",
    "act", "section", "date_of_filing", "date_of_decision", "date_first_list", "date_last_list", "date_next_list",
    "purpose_name", "type_name", "disp_name", "criminal", "bailable_ipc", "number_sections_ipc", "year",
    "pet_name", "def_name", "pet_adv", "def_adv", "judge_position",
]

STATE_PARTY = re.compile(
    r"\b(?:state|govt|government|union of india|police|s\.?h\.?o|p\.?s\.?i|inspector|collector|municipal|corporation|"
    r"nagar|panchayat|tehsildar|commissioner|railway|bank of|insurance|electricity|board|authority|department)\b",
    re.IGNORECASE,
)


def is_state_party(name: str) -> bool:
    return bool(name) and bool(STATE_PARTY.search(name))

ACT_PATTERNS = [
    ("IPC", re.compile(r"\b(?:ipc|i\.?\s?p\.?\s?c|indian\s+penal\s+code|penal\s+code)\b", re.IGNORECASE)),
    ("CrPC", re.compile(r"\b(?:crpc|cr\.?\s?p\.?\s?c|code\s+of\s+criminal\s+procedure|criminal\s+procedure)\b", re.IGNORECASE)),
    ("IEA", re.compile(r"\b(?:evidence\s+act)\b", re.IGNORECASE)),
]
SECTION_NUMS = re.compile(r"\b(\d{1,3})(?:[\(\-]?([A-Za-z])(?![A-Za-z/]))?\)?")


def ddl_dir() -> Path:
    d = settings.raw_dir / "ddl"
    d.mkdir(parents=True, exist_ok=True)
    return d


def ensure_file(name: str, file_id: int) -> Path:
    path = ddl_dir() / name
    if path.exists() and path.stat().st_size > 0:
        return path
    log.info("downloading %s", name)
    with httpx.stream("GET", DATAVERSE.format(id=file_id), follow_redirects=True, timeout=None) as r:
        r.raise_for_status()
        with path.open("wb") as f:
            for chunk in r.iter_bytes(1 << 20):
                f.write(chunk)
    return path


def ensure_dta(year: int) -> Path:
    name, file_id = CASES_FILES[year]
    dta = ddl_dir() / name.replace(".zip", ".dta")
    if dta.exists() and dta.stat().st_size > 0:
        return dta
    zip_path = ensure_file(name, file_id)
    with zipfile.ZipFile(zip_path) as zf:
        member = next(n for n in zf.namelist() if n.endswith(".dta"))
        log.info("extracting %s", member)
        zf.extract(member, ddl_dir())
        extracted = ddl_dir() / member
        if extracted != dta:
            extracted.rename(dta)
    return dta


def read_key(name: str) -> pd.DataFrame:
    df = pd.read_csv(ensure_file(name, KEY_FILES[name]), sep="\t", dtype=str, keep_default_na=False)
    return df.map(lambda v: v.strip().strip('"') if isinstance(v, str) else v)


def lookup(name: str, year: str, id_col: str, name_col: str) -> dict[str, str]:
    df = read_key(name)
    sub = df[df["year"] == year]
    return {r[id_col]: r[name_col] for _, r in sub.iterrows() if r[id_col]}


def cell(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        return "" if pd.isna(v) else str(int(v)) if v.is_integer() else str(v)
    return str(v).strip()


def to_date(v) -> str | None:
    s = cell(v)
    if not s or s.lower() in {"nan", "nat"}:
        return None
    try:
        return pd.to_datetime(s[:10], format="%Y-%m-%d").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def section_keys_from(act_text: str, section_text: str) -> list[str]:
    if not act_text or not section_text:
        return []
    act = next((code for code, pat in ACT_PATTERNS if pat.search(act_text)), None)
    if not act:
        return []
    return sorted({f"{act}-{num}{(letter or '').upper()}" for num, letter in SECTION_NUMS.findall(section_text)})


def stripe_offsets(total: int, rows: int, stripes: int) -> list[tuple[int, int]]:
    per = max(1, rows // stripes)
    step = max(per, total // stripes)
    return [(min(i * step, max(0, total - per)), per) for i in range(stripes)]


def load_ecourts(rows: int | None = None, year: int = 2010, stripes: int = 40) -> dict:
    rows = rows or settings.ecourts_sample_rows
    y = str(year)
    types = lookup("type_name_key.tab", y, "type_name", "type_name_s")
    purposes = lookup("purpose_name_key.tab", y, "purpose_name", "purpose_name_s")
    disps = lookup("disp_name_key.tab", y, "disp_name", "disp_name_s")

    dta = ensure_dta(year)
    _, meta = pyreadstat.read_dta(str(dta), metadataonly=True)
    total = meta.number_rows or 0
    log.info("%s has %d rows; sampling %d in %d stripes", dta.name, total, rows, stripes)

    written = skipped = 0
    for offset, limit in stripe_offsets(total, rows, stripes):
        df, _ = pyreadstat.read_dta(str(dta), usecols=COLUMNS, row_offset=offset, row_limit=limit)
        batch: list[dict] = []
        for r in df.to_dict("records"):
            cnr = cell(r.get("cino"))
            if len(cnr) < 10:
                skipped += 1
                continue
            state, dist, court_no = cell(r.get("state_code")), cell(r.get("district_code")), cell(r.get("court_no"))
            decision = to_date(r.get("date_of_decision"))
            court_name = cell(r.get("court_name")) or f"Court {court_no}"
            district = cell(r.get("district_name")) or dist
            state_name = cell(r.get("state_name")) or state
            batch.append(
                {
                    "cnr": cnr,
                    "ddl_case_id": cell(r.get("ddl_case_id")),
                    "filing_date": to_date(r.get("date_of_filing")),
                    "decision_date": decision,
                    "status": "disposed" if decision else "pending",
                    "purpose": purposes.get(cell(r.get("purpose_name"))),
                    "disposition": disps.get(cell(r.get("disp_name"))),
                    "year": int(cell(r.get("year")) or year),
                    "first_hearing": to_date(r.get("date_first_list")),
                    "last_hearing": to_date(r.get("date_last_list")),
                    "next_hearing": to_date(r.get("date_next_list")),
                    "criminal": cell(r.get("criminal")) == "1",
                    "act_text": cell(r.get("act")) or None,
                    "section_text": cell(r.get("section")) or None,
                    "pet_adv_present": bool(cell(r.get("pet_adv"))),
                    "def_adv_present": bool(cell(r.get("def_adv"))),
                    "pet_state_party": is_state_party(cell(r.get("pet_name"))),
                    "def_state_party": is_state_party(cell(r.get("def_name"))),
                    "bailable_ipc": (lambda v: None if v == "" else v == "1")(cell(r.get("bailable_ipc"))),
                    "number_sections_ipc": (lambda v: int(float(v)) if v not in ("", "nan") else None)(cell(r.get("number_sections_ipc"))),
                    "judge_position": cell(r.get("judge_position")) or None,
                    "source": SOURCE,
                    "court_id": f"{state}-{dist}-{court_no}",
                    "court_name": f"{court_name}, {district}",
                    "district_id": f"{state}-{dist}",
                    "district_name": district,
                    "state_id": state,
                    "state_name": state_name,
                    "type_id": cell(r.get("type_name")) or None,
                    "type_name": types.get(cell(r.get("type_name"))) or cell(r.get("type_name")) or None,
                    "section_keys": section_keys_from(cell(r.get("act")), cell(r.get("section"))),
                }
            )
        graph.write_batches(UPSERT_CASE_EXT, batch, batch_size=1000)
        written += len(batch)
        log.info("ecourts: %d cases written (offset %d)", written, offset)

    stats = graph.run_one(
        """
        MATCH (c:Case)
        RETURN count(c) AS cases,
               sum(CASE WHEN c.status='pending' THEN 1 ELSE 0 END) AS pending,
               sum(CASE WHEN c.status='disposed' THEN 1 ELSE 0 END) AS disposed,
               count(DISTINCT c.state_id) AS states
        """
    )
    states = graph.run_one("MATCH (s:State) RETURN count(s) AS states")
    return {"written": written, "skipped": skipped, "year": year, "file_rows": total, **(stats or {}), **(states or {})}


UPSERT_CASE_EXT = UPSERT_CASE.replace(
    "c.year = r.year, c.source = r.source,",
    "c.year = r.year, c.source = r.source, c.ddl_case_id = r.ddl_case_id, c.first_hearing = r.first_hearing, "
    "c.last_hearing = r.last_hearing, c.next_hearing = r.next_hearing, c.criminal = r.criminal, "
    "c.act_text = r.act_text, c.section_text = r.section_text, "
    "c.pet_adv_present = r.pet_adv_present, c.def_adv_present = r.def_adv_present, "
    "c.pet_state_party = r.pet_state_party, c.def_state_party = r.def_state_party, "
    "c.bailable_ipc = r.bailable_ipc, c.number_sections_ipc = r.number_sections_ipc, c.judge_position = r.judge_position,",
)
