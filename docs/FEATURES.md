# CaseGraph - Build order and model map (50)

Four products in one platform: case pendency prediction, legal research, undertrial/bail monitoring, consumer complaint help.

Work the Order column top to bottom, one feature at a time. # is the fixed feature id. Phase 1 = foundation, 2 = core product, 3 = later.

## Part 1. Build order

### Milestone 1 - Foundation: data in, graph up, guardrails on

No ML yet. Get real court data flowing into Neo4j and build the two safety pieces every later feature depends on.

| Order | # | Feature | Model or technique needed | Type | Phase |
|---|---|---|---|---|---|
| 1 | 1 | eCourts and NJDG case status ingestion by CNR, scheduled refresh | Scraper + scheduler (no model) | Engineering | 1 |
| 2 | 2 | Judgment ingestion from Indian Kanoon, SC and HC sites with metadata | Scraper + regex/NER metadata parser | Engineering | 1 |
| 3 | 4 | Statute graph: IPC/BNS, CrPC/BNSS, Evidence/BSA, CPA 2019 with old-to-new mapping | Rule-based section parser + Neo4j schema + mapping table | Graph | 1 |
| 4 | 14 | Pendency dashboard by state, district, court, case type | Aggregation queries (no model) | Engineering | 1 |
| 5 | 17 | Matter tracker with alerts on new orders | Scheduled diff + notifications (no model) | Engineering | 1 |
| 6 | 7 | Hybrid retrieval: vector embeddings + Cypher | Sentence embedding model (bge-m3 or e5) + vector index + Cypher templates | Deep model | 1 |
| 7 | 25 | Citation verifier: every cited case must exist in graph | Deterministic regex + graph lookup (no model) | Graph | 1 |
| 8 | 29 | Old-to-new code cross reference in search and drafts | Mapping table + Cypher (no model) | Graph | 1 |
| 9 | 39 | Mandatory human review gate before draft release | LangGraph interrupt / approval node (no model) | Engineering | 1 |

### Milestone 2 - First models: pendency predictor

Your first basic ML, first explanation with an LLM, and first deep model, all on the same hearing data.

| Order | # | Feature | Model or technique needed | Type | Phase |
|---|---|---|---|---|---|
| 10 | 9 | Time-to-disposal prediction with confidence range | Gradient boosting regression (LightGBM) or survival model (Cox / random survival forest) | Basic ML | 1 |
| 11 | 11 | Adjournment likelihood for next hearing | Binary classifier (logistic regression baseline, then GBM) | Basic ML | 1 |
| 12 | 13 | Benchmark against similar cases in same court | kNN on case feature vectors + Cypher filters | Basic ML | 2 |
| 13 | 15 | Hearing gap anomaly detection | Isolation forest or z-score on inter-hearing gaps | Basic ML | 2 |
| 14 | 12 | Delay driver explanation in plain language | SHAP feature attributions + LLM narrative | GenAI | 2 |
| 15 | 10 | Stage-wise stall prediction | Multiclass GBM, or sequence model (LSTM / Transformer) over hearing history | Deep model | 2 |

### Milestone 3 - Legal research: embeddings and citation graph

Deep models and GenAI on judgment text. The citation graph becomes useful here.

| Order | # | Feature | Model or technique needed | Type | Phase |
|---|---|---|---|---|---|
| 16 | 19 | Brief-to-precedent semantic search | Embedding retriever + cross-encoder reranker | Deep model | 1 |
| 17 | 26 | Judgment summariser: facts, issues, holding, ratio | LLM structured extraction; optional fine-tuned seq2seq (Flan-T5 / mT5) | GenAI | 2 |
| 18 | 5 | Citation graph with typed edges: cites, follows, distinguishes, overrules, interprets | Citation regex + relation classifier (fine-tuned LegalBERT / InLegalBERT) | Deep model | 2 |
| 19 | 21 | Treatment status: followed, distinguished, overruled | Relation classifier on citing sentences (fine-tuned LegalBERT) | Deep model | 2 |
| 20 | 20 | Interactive citation graph view for any judgment | Neo4j traversal + graph visualisation (no model) | Graph | 2 |
| 21 | 23 | Statute-centric timeline of interpreting judgments | Cypher query over interprets edges (no model) | Graph | 2 |
| 22 | 24 | Research memo drafting with verified citations only | LLM in LangGraph with retrieval and verifier node | GenAI | 2 |
| 23 | 6 | Entity resolution for judges, courts, advocates, parties | String similarity features + logistic regression or XGBoost match classifier | Basic ML | 2 |
| 24 | 8 | Document deduplication and versioning | MinHash / SimHash near-duplicate detection | Basic ML | 2 |

### Milestone 4 - Bail and undertrial: vision enters

Rule engine first, then the vision model reads scanned remand orders, then drafting behind the review gate.

| Order | # | Feature | Model or technique needed | Type | Phase |
|---|---|---|---|---|---|
| 25 | 31 | Eligibility computation under BNSS Section 479 | Rule engine over statute graph (no model) | Engineering | 1 |
| 26 | 33 | Offence severity and maximum sentence lookup | Statute graph query (no model) | Graph | 1 |
| 27 | 3 | Scanned document OCR for orders, FIRs, charge sheets, remand slips | OCR (PaddleOCR or Tesseract) + vision LLM for layout and fields | Vision | 2 |
| 28 | 32 | Custody period from remand and production orders | Vision LLM or OCR + date/entity extraction | Vision | 2 |
| 29 | 35 | Bail precedent finder for similar offence and facts | Embedding similarity on fact patterns + filters | Deep model | 2 |
| 30 | 34 | Bail application draft generator, court-specific format | LLM with templates in LangGraph | GenAI | 2 |
| 31 | 37 | Prison-wise and district-wise undertrial dashboard | Aggregation queries (no model) | Engineering | 2 |

### Milestone 5 - Consumer complaints

Reuse vision and drafting from Milestone 4 on a simpler, high-volume workflow.

| Order | # | Feature | Model or technique needed | Type | Phase |
|---|---|---|---|---|---|
| 32 | 41 | Forum and jurisdiction finder by claim value and location | Rule engine on pecuniary limits (no model) | Engineering | 1 |
| 33 | 42 | Limitation period check with reminders | Rule engine + date extraction (no model) | Engineering | 1 |
| 34 | 40 | Evidence intake from photos of bills, warranty cards, chat screenshots | Document type classifier (small CNN / ViT) + vision LLM field extraction | Vision | 2 |
| 35 | 43 | Complaint drafting in prescribed format with relief computation | LLM with templates | GenAI | 2 |
| 36 | 44 | Similar order retrieval from NCDRC and State Commissions | Embedding retriever over orders | Deep model | 2 |
| 37 | 45 | Outcome and compensation estimate from past orders | Outcome classifier + compensation regression (GBM) | Basic ML | 3 |

### Milestone 6 - Platform hardening and later features

Multi-user SaaS plumbing, retraining loop, then every Phase 3 feature.

| Order | # | Feature | Model or technique needed | Type | Phase |
|---|---|---|---|---|---|
| 38 | 49 | Role-based access: litigant, lawyer, legal aid, researcher | Application feature (no model) | Engineering | 2 |
| 39 | 50 | Agent audit trail and feedback loop to retrain classifiers | LangGraph tracing (LangSmith) + retraining pipeline (MLflow) | Engineering | 2 |
| 40 | 16 | Next hearing outcome: adjourn, progress, dispose | Sequence model (GRU / small Transformer) on hearing event sequence | Deep model | 3 |
| 41 | 22 | Conflicting bench detection across High Courts | NLI / contradiction model on holdings + graph queries | Deep model | 3 |
| 42 | 27 | Headnote and issue generation | LLM generation with few-shot examples | GenAI | 3 |
| 43 | 28 | Argument builder: authorities for and against | LLM + retrieval + stance classifier | GenAI | 3 |
| 44 | 36 | Legal aid queue prioritised by eligibility and custody time | Ranking model (GBM) or weighted score | Basic ML | 3 |
| 45 | 18 | Alternative route suggestion: Lok Adalat, mediation, fast-track | Rule engine + eligibility classifier | Basic ML | 3 |
| 46 | 38 | Hearing reminder and bail condition compliance tracker | Scheduler + notifications (no model) | Engineering | 3 |
| 47 | 46 | e-Daakhil filing checklist and fee calculator | Rule engine (no model) | Engineering | 3 |
| 48 | 47 | Post-filing case timeline tracker | Scheduler + eCourts sync (no model) | Engineering | 3 |
| 49 | 30 | Saved research workspaces with DOCX and PDF export | Application feature (no model) | Engineering | 3 |
| 50 | 48 | Multilingual question answering and drafting (Hindi, regional) | Multilingual LLM + IndicTrans2 translation model | GenAI | 3 |

## Part 2. Grouped by product

| Order | # | Feature | Model or technique needed | Type | Phase |
|---|---|---|---|---|---|
| | | **A. Data ingestion and knowledge graph** | | | |
| 1 | 1 | eCourts and NJDG case status ingestion by CNR, scheduled refresh | Scraper + scheduler (no model) | Engineering | 1 |
| 2 | 2 | Judgment ingestion from Indian Kanoon, SC and HC sites with metadata | Scraper + regex/NER metadata parser | Engineering | 1 |
| 27 | 3 | Scanned document OCR for orders, FIRs, charge sheets, remand slips | OCR (PaddleOCR or Tesseract) + vision LLM for layout and fields | Vision | 2 |
| 3 | 4 | Statute graph: IPC/BNS, CrPC/BNSS, Evidence/BSA, CPA 2019 with old-to-new mapping | Rule-based section parser + Neo4j schema + mapping table | Graph | 1 |
| 18 | 5 | Citation graph with typed edges: cites, follows, distinguishes, overrules, interprets | Citation regex + relation classifier (fine-tuned LegalBERT / InLegalBERT) | Deep model | 2 |
| 23 | 6 | Entity resolution for judges, courts, advocates, parties | String similarity features + logistic regression or XGBoost match classifier | Basic ML | 2 |
| 6 | 7 | Hybrid retrieval: vector embeddings + Cypher | Sentence embedding model (bge-m3 or e5) + vector index + Cypher templates | Deep model | 1 |
| 24 | 8 | Document deduplication and versioning | MinHash / SimHash near-duplicate detection | Basic ML | 2 |
| | | **B. Case pendency and delay predictor** | | | |
| 10 | 9 | Time-to-disposal prediction with confidence range | Gradient boosting regression (LightGBM) or survival model (Cox / random survival forest) | Basic ML | 1 |
| 15 | 10 | Stage-wise stall prediction | Multiclass GBM, or sequence model (LSTM / Transformer) over hearing history | Deep model | 2 |
| 11 | 11 | Adjournment likelihood for next hearing | Binary classifier (logistic regression baseline, then GBM) | Basic ML | 1 |
| 14 | 12 | Delay driver explanation in plain language | SHAP feature attributions + LLM narrative | GenAI | 2 |
| 12 | 13 | Benchmark against similar cases in same court | kNN on case feature vectors + Cypher filters | Basic ML | 2 |
| 4 | 14 | Pendency dashboard by state, district, court, case type | Aggregation queries (no model) | Engineering | 1 |
| 13 | 15 | Hearing gap anomaly detection | Isolation forest or z-score on inter-hearing gaps | Basic ML | 2 |
| 40 | 16 | Next hearing outcome: adjourn, progress, dispose | Sequence model (GRU / small Transformer) on hearing event sequence | Deep model | 3 |
| 5 | 17 | Matter tracker with alerts on new orders | Scheduled diff + notifications (no model) | Engineering | 1 |
| 45 | 18 | Alternative route suggestion: Lok Adalat, mediation, fast-track | Rule engine + eligibility classifier | Basic ML | 3 |
| | | **C. Legal research assistant** | | | |
| 16 | 19 | Brief-to-precedent semantic search | Embedding retriever + cross-encoder reranker | Deep model | 1 |
| 20 | 20 | Interactive citation graph view for any judgment | Neo4j traversal + graph visualisation (no model) | Graph | 2 |
| 19 | 21 | Treatment status: followed, distinguished, overruled | Relation classifier on citing sentences (fine-tuned LegalBERT) | Deep model | 2 |
| 41 | 22 | Conflicting bench detection across High Courts | NLI / contradiction model on holdings + graph queries | Deep model | 3 |
| 21 | 23 | Statute-centric timeline of interpreting judgments | Cypher query over interprets edges (no model) | Graph | 2 |
| 22 | 24 | Research memo drafting with verified citations only | LLM in LangGraph with retrieval and verifier node | GenAI | 2 |
| 7 | 25 | Citation verifier: every cited case must exist in graph | Deterministic regex + graph lookup (no model) | Graph | 1 |
| 17 | 26 | Judgment summariser: facts, issues, holding, ratio | LLM structured extraction; optional fine-tuned seq2seq (Flan-T5 / mT5) | GenAI | 2 |
| 42 | 27 | Headnote and issue generation | LLM generation with few-shot examples | GenAI | 3 |
| 43 | 28 | Argument builder: authorities for and against | LLM + retrieval + stance classifier | GenAI | 3 |
| 8 | 29 | Old-to-new code cross reference in search and drafts | Mapping table + Cypher (no model) | Graph | 1 |
| 49 | 30 | Saved research workspaces with DOCX and PDF export | Application feature (no model) | Engineering | 3 |
| | | **D. Bail and undertrial monitoring** | | | |
| 25 | 31 | Eligibility computation under BNSS Section 479 | Rule engine over statute graph (no model) | Engineering | 1 |
| 28 | 32 | Custody period from remand and production orders | Vision LLM or OCR + date/entity extraction | Vision | 2 |
| 26 | 33 | Offence severity and maximum sentence lookup | Statute graph query (no model) | Graph | 1 |
| 30 | 34 | Bail application draft generator, court-specific format | LLM with templates in LangGraph | GenAI | 2 |
| 29 | 35 | Bail precedent finder for similar offence and facts | Embedding similarity on fact patterns + filters | Deep model | 2 |
| 44 | 36 | Legal aid queue prioritised by eligibility and custody time | Ranking model (GBM) or weighted score | Basic ML | 3 |
| 31 | 37 | Prison-wise and district-wise undertrial dashboard | Aggregation queries (no model) | Engineering | 2 |
| 46 | 38 | Hearing reminder and bail condition compliance tracker | Scheduler + notifications (no model) | Engineering | 3 |
| 9 | 39 | Mandatory human review gate before draft release | LangGraph interrupt / approval node (no model) | Engineering | 1 |
| | | **E. Consumer court complaint helper** | | | |
| 34 | 40 | Evidence intake from photos of bills, warranty cards, chat screenshots | Document type classifier (small CNN / ViT) + vision LLM field extraction | Vision | 2 |
| 32 | 41 | Forum and jurisdiction finder by claim value and location | Rule engine on pecuniary limits (no model) | Engineering | 1 |
| 33 | 42 | Limitation period check with reminders | Rule engine + date extraction (no model) | Engineering | 1 |
| 35 | 43 | Complaint drafting in prescribed format with relief computation | LLM with templates | GenAI | 2 |
| 36 | 44 | Similar order retrieval from NCDRC and State Commissions | Embedding retriever over orders | Deep model | 2 |
| 37 | 45 | Outcome and compensation estimate from past orders | Outcome classifier + compensation regression (GBM) | Basic ML | 3 |
| 47 | 46 | e-Daakhil filing checklist and fee calculator | Rule engine (no model) | Engineering | 3 |
| 48 | 47 | Post-filing case timeline tracker | Scheduler + eCourts sync (no model) | Engineering | 3 |
| | | **F. Cross-cutting** | | | |
| 50 | 48 | Multilingual question answering and drafting (Hindi, regional) | Multilingual LLM + IndicTrans2 translation model | GenAI | 3 |
| 38 | 49 | Role-based access: litigant, lawyer, legal aid, researcher | Application feature (no model) | Engineering | 2 |
| 39 | 50 | Agent audit trail and feedback loop to retrain classifiers | LangGraph tracing (LangSmith) + retraining pipeline (MLflow) | Engineering | 2 |

Counts: Basic ML 9, Deep model 9, Vision 3, GenAI 8, Graph 6, Engineering 15.
