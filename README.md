# CaseGraph

Litigation intelligence SaaS for Indian courts. Four products on one knowledge graph: case pendency prediction, legal research with a citation graph, undertrial bail monitoring, and consumer complaint drafting.

Stack: Neo4j knowledge graph, LangChain retrieval, LangGraph agents with human review gates, basic ML classifiers and regressors, deep models for embeddings, sequences and vision, and GenAI for drafting. Everything runs locally: Neo4j in Docker, models through Ollama.

## Layout

- `docs/CaseGraph-Features.pdf` - the 50-feature build order with the model each feature needs
- `docs/STATUS.md` - what is built, where it lives, known limits, what is next
- `docs/build-features.mjs` - single source for the feature table; run `node docs/build-features.mjs` then print `docs/features-table.html` to PDF
- `frontend/` - Vite + React + TypeScript + Tailwind v4 UI (black and gold)
- `backend/` - FastAPI + Neo4j + LangGraph API (Python 3.12, managed with uv)
- `docker-compose.yml` - Neo4j 5 Community with APOC

## Run it

1. Neo4j

```
docker compose up -d
```

Browser at http://localhost:7474, user `neo4j`, password `casegraph-dev`.

2. Ollama models (once)

```
ollama pull bge-m3
ollama pull llama3.2:3b
```

3. Backend

```
cd backend
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

Docs at http://localhost:8000/docs. On first run, load data through the admin endpoints or a Python shell:

```
POST /admin/schema
POST /admin/load/statutes
POST /admin/load/ecourts?rows=50000       # downloads ~386 MB from Harvard Dataverse the first time
POST /admin/load/judgments?rows=2000      # downloads ~645 MB from Hugging Face the first time, runs in background
```

4. Frontend

```
cd frontend
npm install
npm run dev
```

Routes: `/` landing, `/login`, `/signup`, `/app` dashboard (live when the API is up, sample data otherwise), `/app/pendency`, `/app/research`, `/app/bail`, `/app/consumer`, `/app/graph`.

### Demo mode and Vercel

The frontend can run on its own with sample data. Demo mode skips every API call. It is on when `VITE_DEMO=1`, when `VITE_API_BASE` is empty or `demo`, or when a production build has no `VITE_API_BASE` at all. `VITE_DEMO=0` forces live mode. `npm run dev` with nothing set still talks to `http://localhost:8000`. To point a production build at a real API, set `VITE_API_BASE=https://your-api`.

To deploy on Vercel, import the repo with Root Directory `frontend`. The Vite preset and `frontend/vercel.json` handle the build (`npm run build`, output `dist`) and the SPA rewrites. Add `VITE_DEMO=1` as an environment variable.

## Data sources and licences

- Case data: DDL eCourts replication files, Harvard Dataverse doi:10.7910/DVN/GHLGSW, CC0.
- Judgments: `therajasekhar/sc-judgments-indic-v1` on Hugging Face plus AWS Open Data Indian Supreme Court judgments metadata, both CC BY 4.0.
- Statute mapping: IndiaCode by eCourtsIndia `mapping.csv`, CC BY 4.0, with hand-checked overrides from the BPRD comparison tables.

Nothing here is legal advice. Drafts are released only after a person approves them in the review queue.
