# CaseGraph build status

Feature ids refer to `CaseGraph-Features.pdf` / `FEATURES.md`.

## Milestone 1 - Foundation (done 2026-09-13)

| Order | # | Feature | Where | Notes |
|---|---|---|---|---|
| 1 | 1 | eCourts case ingestion, scheduled refresh | `backend/app/ingest/ecourts.py`, `app/tracker/scheduler.py` | Source: DDL replication data on Harvard Dataverse (CC0), 2010 file, striped 50K-case sample across 18 states. Hourly APScheduler refresh of tracked matters. Live CNR lookup is a stub behind `CaseSource` until a later feature. |
| 2 | 2 | Judgment ingestion with metadata | `app/ingest/judgments.py` | Hugging Face `therajasekhar/sc-judgments-indic-v1` (text) joined to AWS Open Data eSCR metadata (both CC BY 4.0). 2,150 judgments loaded, 1950-2025 sample. |
| 3 | 4 | Statute graph with old-to-new mapping | `app/ingest/statutes.py`, `data/statutes/*.csv` | IndiaCode by eCourtsIndia mapping (CC BY 4.0) plus 34 hand-checked overrides from the BPRD tables and 41 punishment rows. 2,232 sections, 1,241 REPLACED_BY edges. |
| 4 | 14 | Pendency dashboard | `app/api/dashboard.py` | `/dashboard/summary`, `/pendency-by-age`, `/pendency?group_by=state|district|court|case_type|year`, `/stages`. Wired into the frontend dashboard. |
| 5 | 17 | Matter tracker with alerts | `app/tracker/matters.py`, `app/api/matters.py` | Snapshot hash per matter; changes raise typed alerts (status, stage, disposal). `/matters`, `/matters/refresh`, `/alerts`. |
| 6 | 7 | Hybrid retrieval | `app/retrieval/hybrid.py` | bge-m3 embeddings via Ollama in a Neo4j vector index, Lucene fulltext, section-filter Cypher, fused with reciprocal rank fusion. `/search`. |
| 7 | 25 | Citation verifier | `app/verify/citations.py` | Reporter citations (AIR, SCC, SCR, SCC OnLine, INSC) resolved exactly; case names resolved by fulltext plus fuzzy match. `/verify/citations`. |
| 8 | 29 | Old-to-new code cross reference | `app/verify/statutes.py` | `/statutes/map?act=CrPC&section=436A` -> BNSS 479. Search expands section filters across aliases. |
| 9 | 39 | Human review gate | `app/agents/review_gate.py`, `app/api/review.py` | LangGraph: draft (Ollama) -> verify citations -> interrupt -> approve/reject -> release/discard. Review items persisted in Neo4j. |

Verified end to end on 2026-09-13: statute mapping, 50K case load (20 s), 2,000 judgment load with embeddings (143 s), search, verifier, matter create, review draft -> approve.

## Known limits after Milestone 1

- Case data is the 2010 filing cohort only; pendency "as of" defaults to the latest decision or hearing date in the data.
- Only 87 citation edges because most cited judgments are outside the 2,150 sample. Loading more judgments raises this quickly.
- Stage names are raw eCourts strings with spelling variants; normalisation is a Milestone 2 task.
- Chat model is llama3.2:3b; drafts are rough and always stop at the review gate.
- DDL public bulk data (Dropbox) is CC BY-NC-SA; the Dataverse replication files used here are CC0.

## Milestone 2 - Pendency predictor (in progress)

| Order | # | Feature | Where | Notes |
|---|---|---|---|---|
| 10 | 9 | Time-to-disposal prediction with confidence range | `backend/app/ml/pendency/` (`data.py`, `features.py`, `train.py`, `predict.py`), `app/api/predict.py` | Script built 2026-09-13, smoke-tested on 4K rows (GPU). XGBoost 3.4: one squared-error model on log(days) for the median plus two quantile models (alpha 0.1 and 0.9) for an 80% range. Features known at filing: state, district, court, case type (native categoricals), filing year/month/weekday, first-hearing gap, criminal flag, section count, IPC/CrPC flags, top-40 section indicators. Leaky fields (current stage, disposition, last/next hearing) excluded. Artifacts in `backend/models/pendency/` (gitignored). Endpoints: `GET /predict/disposal/{cnr}`, `GET /predict/disposal?status=pending&limit=20`, `GET /predict/model`. Each prediction also returns a same-court benchmark (median, p10, p90) for the explanation feature later. |

Train it with:

```
cd backend
uv run python -m app.ml.pendency.train              # defaults: up to 200K disposed cases, GPU, early stopping
uv run python -m app.ml.pendency.predict --cnr MHNB030003102010
```

Load more cases first for a stronger model (each 50K takes ~20 s): `POST /admin/load/ecourts?rows=300000`.

Training runs so far (test set never seen in training):

| Run | Data | Features | MAE days | Median AE | Within 180 d | 80% range coverage | Range width |
|---|---|---|---|---|---|---|---|
| v1, 2026-09-13 | 2010 cohort, 160K train | 8 numeric + 4 categorical + 40 sections, quantiles 0.10/0.90 | 320 | 193 | 48% | 76% | 917 d |
| v2, 2026-09-13 | 2010+2013+2015, 478K train | + advocate present, state party, bailable IPC, IPC section count, judge position; quantiles 0.08/0.92 | 247 | 126 | 58% | 82% | 809 d |
| v2 on 2010 cases only | same model | same | 332 | 199 | 47% | 82% | |

Read v2 carefully: the headline gain comes mostly from the 2013 and 2015 cohorts, whose disposed cases were observed for at most 3 to 5 years, so they are shorter by construction. On the 2010 cohort alone v2 is no better than v1 except for the range calibration, which the wider quantiles fixed. The new features rank mid-table (state as defendant, state as petitioner) and did not move the error much.

Consequence: mixing cohorts without handling right-censoring teaches the model "recent filing means fast disposal", which is an artefact. Next step for this feature is a censoring-aware objective: XGBoost `survival:aft` with pending cases entering as right-censored observations (lower bound = days elapsed to the snapshot date). That uses all 1.1M cases instead of only disposed ones and removes the bias.

Neo4j memory was raised in `docker-compose.yml` (heap 3G, page cache 1G, transaction max 2G) and training data is fetched per state to stay under the transaction limit.

Remaining in Milestone 2: order 11 (adjournment likelihood), 12 (similar-case benchmark), 13 (hearing gap anomaly), 14 (SHAP + LLM explanation), 15 (stage-wise stall).
