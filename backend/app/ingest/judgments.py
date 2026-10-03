import logging
import re
from pathlib import Path

import httpx
import pandas as pd
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

from app.config import settings
from app.graph.client import graph
from app.retrieval.embeddings import embed_texts
from app.verify.citations import extract_citations, normalise_citation
from app.verify.statutes import parse_section_refs

log = logging.getLogger("casegraph.judgments")

HF_DATASET = "therajasekhar/sc-judgments-indic-v1"
AWS_META = "https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/metadata/parquet/year={year}/metadata.parquet"

UPSERT_JUDGMENTS = """
UNWIND $rows AS r
MERGE (j:Judgment {id: r.id})
SET j.title = r.title, j.date = r.date, j.year = r.year, j.court = 'Supreme Court of India',
    j.citation = r.citation, j.citation_norm = r.citation_norm, j.alt_citations_norm = r.alt_citations_norm,
    j.case_id = r.case_id, j.petitioner = r.petitioner, j.respondent = r.respondent,
    j.judges = r.judges, j.author_judge = r.author_judge, j.disposal = r.disposal,
    j.headnote = r.headnote, j.text_path = r.text_path, j.char_len = r.char_len, j.source = 'sc-judgments-indic-v1 + AWS eSCR metadata (CC BY 4.0)'
"""

SET_EMBEDDINGS = """
UNWIND $rows AS r
MATCH (j:Judgment {id: r.id}) SET j.embedding = r.embedding
"""

LINK_SECTIONS = """
UNWIND $rows AS r
MATCH (j:Judgment {id: r.id})
UNWIND r.keys AS key
MERGE (s:Section {key: key})
MERGE (j)-[:INTERPRETS]->(s)
"""

LINK_CITATIONS = """
UNWIND $rows AS r
MATCH (j:Judgment {id: r.id})
UNWIND r.norms AS norm
MATCH (cited:Judgment)
WHERE cited.citation_norm = norm OR norm IN coalesce(cited.alt_citations_norm, [])
MERGE (j)-[c:CITES]->(cited) SET c.raw = norm
"""


def texts_dir() -> Path:
    d = settings.raw_dir / "judgments"
    d.mkdir(parents=True, exist_ok=True)
    return d


def fetch_metadata(years: range) -> pd.DataFrame:
    frames = []
    cache = settings.raw_dir / "sc_metadata"
    cache.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=60) as client:
        for year in years:
            path = cache / f"{year}.parquet"
            if not path.exists():
                r = client.get(AWS_META.format(year=year))
                if r.status_code != 200:
                    log.warning("no metadata for %s (%s)", year, r.status_code)
                    continue
                path.write_bytes(r.content)
            frames.append(pd.read_parquet(path))
    if not frames:
        return pd.DataFrame()
    meta = pd.concat(frames, ignore_index=True)
    meta["join_key"] = meta["path"].astype(str) + "_EN"
    return meta.drop_duplicates("join_key")


def parse_date(raw: str | None) -> tuple[str | None, int | None]:
    if not raw:
        return None, None
    m = re.match(r"(\d{2})-(\d{2})-(\d{4})", str(raw))
    if not m:
        return None, None
    d, mth, y = m.groups()
    return f"{y}-{mth}-{d}", int(y)


def headnote_of(text: str, limit: int = 1500) -> str:
    body = re.sub(r"\s+", " ", text).strip()
    return body[:limit]


def judgments_parquet() -> Path:
    return Path(hf_hub_download(HF_DATASET, "data/en/en-00000.parquet", repo_type="dataset"))


def iter_judgment_rows(wanted: set[str], sample_rows: int, seed: int = 7):
    pf = pq.ParquetFile(judgments_parquet())
    keys: list[tuple[int, int, str]] = []
    for rg in range(pf.num_row_groups):
        col = pf.read_row_group(rg, columns=["cnr"]).column("cnr").to_pylist()
        keys.extend((rg, i, str(k)) for i, k in enumerate(col) if not wanted or str(k) in wanted)
    if len(keys) > sample_rows:
        import random

        random.Random(seed).shuffle(keys)
        keys = keys[:sample_rows]
    by_group: dict[int, set[int]] = {}
    for rg, i, _ in keys:
        by_group.setdefault(rg, set()).add(i)
    for rg, idxs in sorted(by_group.items()):
        table = pf.read_row_group(rg, columns=["cnr", "title", "text_en", "char_len", "garbled"])
        for i in sorted(idxs):
            yield {c: table.column(c)[i].as_py() for c in table.column_names}


def load_judgments(sample_rows: int | None = None, year_from: int = 1950, year_to: int = 2025, embed: bool = True) -> dict:
    sample_rows = sample_rows or settings.judgments_sample_rows
    meta = fetch_metadata(range(year_from, year_to + 1))
    wanted = set(meta["join_key"]) if not meta.empty else set()
    meta_by_key = meta.set_index("join_key").to_dict("index") if not meta.empty else {}

    rows: list[dict] = []
    section_rows: list[dict] = []
    citation_rows: list[dict] = []
    for item in iter_judgment_rows(wanted, sample_rows):
        key = str(item.get("cnr") or item.get("title"))
        if item.get("garbled"):
            continue
        text = item["text_en"] or ""
        m = meta_by_key.get(key, {})
        date, year = parse_date(m.get("decision_date"))
        citation = (m.get("citation") or "").strip() or None
        alt = [normalise_citation(m["case_id"])] if m.get("case_id") else []
        judgment_id = key
        (texts_dir() / f"{judgment_id}.txt").write_text(text, encoding="utf-8")
        rows.append(
            {
                "id": judgment_id,
                "title": (m.get("title") or item.get("title") or key).strip(),
                "date": date,
                "year": year,
                "citation": citation,
                "citation_norm": normalise_citation(citation) if citation else None,
                "alt_citations_norm": alt,
                "case_id": m.get("case_id"),
                "petitioner": m.get("petitioner"),
                "respondent": m.get("respondent"),
                "judges": m.get("judge"),
                "author_judge": m.get("author_judge"),
                "disposal": m.get("disposal_nature"),
                "headnote": headnote_of(text),
                "text_path": str(texts_dir() / f"{judgment_id}.txt"),
                "char_len": int(item.get("char_len") or len(text)),
            }
        )
        keys = parse_section_refs(text[:20000])
        if keys:
            section_rows.append({"id": judgment_id, "keys": keys})
        norms = sorted({normalise_citation(raw) for raw, kind in extract_citations(text) if kind == "reporter"})
        if norms:
            citation_rows.append({"id": judgment_id, "norms": norms})
        if len(rows) >= sample_rows:
            break

    graph.write_batches(UPSERT_JUDGMENTS, rows, batch_size=500)
    graph.write_batches(LINK_SECTIONS, section_rows, batch_size=500)
    graph.write_batches(LINK_CITATIONS, citation_rows, batch_size=200)

    embedded = 0
    if embed:
        embedded = embed_judgments([r["id"] for r in rows])

    stats = graph.run_one("MATCH (j:Judgment) OPTIONAL MATCH (j)-[c:CITES]->() RETURN count(DISTINCT j) AS judgments, count(c) AS cites")
    return {"loaded": len(rows), "with_sections": len(section_rows), "with_citations": len(citation_rows), "embedded": embedded, **(stats or {})}


def embed_judgments(ids: list[str] | None = None, batch_size: int = 16) -> int:
    rows = graph.run(
        """
        MATCH (j:Judgment) WHERE j.embedding IS NULL AND ($ids IS NULL OR j.id IN $ids)
        RETURN j.id AS id, j.title AS title, j.headnote AS headnote
        """,
        ids=ids,
    )
    done = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        vectors = embed_texts([f"{r['title']}\n{r['headnote']}" for r in batch])
        graph.write_batches(SET_EMBEDDINGS, [{"id": r["id"], "embedding": v} for r, v in zip(batch, vectors)])
        done += len(batch)
        if done % 160 == 0:
            log.info("embedded %d / %d", done, len(rows))
    return done
