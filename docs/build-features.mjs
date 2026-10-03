import { writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

const sections = [
  {
    module: 'A. Data ingestion and knowledge graph',
    rows: [
      ['eCourts and NJDG case status ingestion by CNR, scheduled refresh', 'Scraper + scheduler (no model)', 'Engineering', 1],
      ['Judgment ingestion from Indian Kanoon, SC and HC sites with metadata', 'Scraper + regex/NER metadata parser', 'Engineering', 1],
      ['Scanned document OCR for orders, FIRs, charge sheets, remand slips', 'OCR (PaddleOCR or Tesseract) + vision LLM for layout and fields', 'Vision', 2],
      ['Statute graph: IPC/BNS, CrPC/BNSS, Evidence/BSA, CPA 2019 with old-to-new mapping', 'Rule-based section parser + Neo4j schema + mapping table', 'Graph', 1],
      ['Citation graph with typed edges: cites, follows, distinguishes, overrules, interprets', 'Citation regex + relation classifier (fine-tuned LegalBERT / InLegalBERT)', 'Deep model', 2],
      ['Entity resolution for judges, courts, advocates, parties', 'String similarity features + logistic regression or XGBoost match classifier', 'Basic ML', 2],
      ['Hybrid retrieval: vector embeddings + Cypher', 'Sentence embedding model (bge-m3 or e5) + vector index + Cypher templates', 'Deep model', 1],
      ['Document deduplication and versioning', 'MinHash / SimHash near-duplicate detection', 'Basic ML', 2],
    ],
  },
  {
    module: 'B. Case pendency and delay predictor',
    rows: [
      ['Time-to-disposal prediction with confidence range', 'Gradient boosting regression (LightGBM) or survival model (Cox / random survival forest)', 'Basic ML', 1],
      ['Stage-wise stall prediction', 'Multiclass GBM, or sequence model (LSTM / Transformer) over hearing history', 'Deep model', 2],
      ['Adjournment likelihood for next hearing', 'Binary classifier (logistic regression baseline, then GBM)', 'Basic ML', 1],
      ['Delay driver explanation in plain language', 'SHAP feature attributions + LLM narrative', 'GenAI', 2],
      ['Benchmark against similar cases in same court', 'kNN on case feature vectors + Cypher filters', 'Basic ML', 2],
      ['Pendency dashboard by state, district, court, case type', 'Aggregation queries (no model)', 'Engineering', 1],
      ['Hearing gap anomaly detection', 'Isolation forest or z-score on inter-hearing gaps', 'Basic ML', 2],
      ['Next hearing outcome: adjourn, progress, dispose', 'Sequence model (GRU / small Transformer) on hearing event sequence', 'Deep model', 3],
      ['Matter tracker with alerts on new orders', 'Scheduled diff + notifications (no model)', 'Engineering', 1],
      ['Alternative route suggestion: Lok Adalat, mediation, fast-track', 'Rule engine + eligibility classifier', 'Basic ML', 3],
    ],
  },
  {
    module: 'C. Legal research assistant',
    rows: [
      ['Brief-to-precedent semantic search', 'Embedding retriever + cross-encoder reranker', 'Deep model', 1],
      ['Interactive citation graph view for any judgment', 'Neo4j traversal + graph visualisation (no model)', 'Graph', 2],
      ['Treatment status: followed, distinguished, overruled', 'Relation classifier on citing sentences (fine-tuned LegalBERT)', 'Deep model', 2],
      ['Conflicting bench detection across High Courts', 'NLI / contradiction model on holdings + graph queries', 'Deep model', 3],
      ['Statute-centric timeline of interpreting judgments', 'Cypher query over interprets edges (no model)', 'Graph', 2],
      ['Research memo drafting with verified citations only', 'LLM in LangGraph with retrieval and verifier node', 'GenAI', 2],
      ['Citation verifier: every cited case must exist in graph', 'Deterministic regex + graph lookup (no model)', 'Graph', 1],
      ['Judgment summariser: facts, issues, holding, ratio', 'LLM structured extraction; optional fine-tuned seq2seq (Flan-T5 / mT5)', 'GenAI', 2],
      ['Headnote and issue generation', 'LLM generation with few-shot examples', 'GenAI', 3],
      ['Argument builder: authorities for and against', 'LLM + retrieval + stance classifier', 'GenAI', 3],
      ['Old-to-new code cross reference in search and drafts', 'Mapping table + Cypher (no model)', 'Graph', 1],
      ['Saved research workspaces with DOCX and PDF export', 'Application feature (no model)', 'Engineering', 3],
    ],
  },
  {
    module: 'D. Bail and undertrial monitoring',
    rows: [
      ['Eligibility computation under BNSS Section 479', 'Rule engine over statute graph (no model)', 'Engineering', 1],
      ['Custody period from remand and production orders', 'Vision LLM or OCR + date/entity extraction', 'Vision', 2],
      ['Offence severity and maximum sentence lookup', 'Statute graph query (no model)', 'Graph', 1],
      ['Bail application draft generator, court-specific format', 'LLM with templates in LangGraph', 'GenAI', 2],
      ['Bail precedent finder for similar offence and facts', 'Embedding similarity on fact patterns + filters', 'Deep model', 2],
      ['Legal aid queue prioritised by eligibility and custody time', 'Ranking model (GBM) or weighted score', 'Basic ML', 3],
      ['Prison-wise and district-wise undertrial dashboard', 'Aggregation queries (no model)', 'Engineering', 2],
      ['Hearing reminder and bail condition compliance tracker', 'Scheduler + notifications (no model)', 'Engineering', 3],
      ['Mandatory human review gate before draft release', 'LangGraph interrupt / approval node (no model)', 'Engineering', 1],
    ],
  },
  {
    module: 'E. Consumer court complaint helper',
    rows: [
      ['Evidence intake from photos of bills, warranty cards, chat screenshots', 'Document type classifier (small CNN / ViT) + vision LLM field extraction', 'Vision', 2],
      ['Forum and jurisdiction finder by claim value and location', 'Rule engine on pecuniary limits (no model)', 'Engineering', 1],
      ['Limitation period check with reminders', 'Rule engine + date extraction (no model)', 'Engineering', 1],
      ['Complaint drafting in prescribed format with relief computation', 'LLM with templates', 'GenAI', 2],
      ['Similar order retrieval from NCDRC and State Commissions', 'Embedding retriever over orders', 'Deep model', 2],
      ['Outcome and compensation estimate from past orders', 'Outcome classifier + compensation regression (GBM)', 'Basic ML', 3],
      ['e-Daakhil filing checklist and fee calculator', 'Rule engine (no model)', 'Engineering', 3],
      ['Post-filing case timeline tracker', 'Scheduler + eCourts sync (no model)', 'Engineering', 3],
    ],
  },
  {
    module: 'F. Cross-cutting',
    rows: [
      ['Multilingual question answering and drafting (Hindi, regional)', 'Multilingual LLM + IndicTrans2 translation model', 'GenAI', 3],
      ['Role-based access: litigant, lawyer, legal aid, researcher', 'Application feature (no model)', 'Engineering', 2],
      ['Agent audit trail and feedback loop to retrain classifiers', 'LangGraph tracing (LangSmith) + retraining pipeline (MLflow)', 'Engineering', 2],
    ],
  },
]

const typeColors = {
  'Basic ML': '#2f6fdb',
  'Deep model': '#7b3fd1',
  Vision: '#d1487b',
  GenAI: '#b8860b',
  Graph: '#1f8a5b',
  Engineering: '#6b6b6b',
}

const milestones = [
  {
    name: 'Milestone 1 - Foundation: data in, graph up, guardrails on',
    goal: 'No ML yet. Get real court data flowing into Neo4j and build the two safety pieces every later feature depends on.',
    features: [1, 2, 4, 14, 17, 7, 25, 29, 39],
  },
  {
    name: 'Milestone 2 - First models: pendency predictor',
    goal: 'Your first basic ML, first explanation with an LLM, and first deep model, all on the same hearing data.',
    features: [9, 11, 13, 15, 12, 10],
  },
  {
    name: 'Milestone 3 - Legal research: embeddings and citation graph',
    goal: 'Deep models and GenAI on judgment text. The citation graph becomes useful here.',
    features: [19, 26, 5, 21, 20, 23, 24, 6, 8],
  },
  {
    name: 'Milestone 4 - Bail and undertrial: vision enters',
    goal: 'Rule engine first, then the vision model reads scanned remand orders, then drafting behind the review gate.',
    features: [31, 33, 3, 32, 35, 34, 37],
  },
  {
    name: 'Milestone 5 - Consumer complaints',
    goal: 'Reuse vision and drafting from Milestone 4 on a simpler, high-volume workflow.',
    features: [41, 42, 40, 43, 44, 45],
  },
  {
    name: 'Milestone 6 - Platform hardening and later features',
    goal: 'Multi-user SaaS plumbing, retraining loop, then every Phase 3 feature.',
    features: [49, 50, 16, 22, 27, 28, 36, 18, 38, 46, 47, 30, 48],
  },
]

const orderOf = {}
const milestoneOf = {}
let order = 0
for (const m of milestones) for (const f of m.features) {
  orderOf[f] = ++order
  milestoneOf[f] = m
}

let n = 0
const flat = sections.flatMap((s) =>
  s.rows.map((r) => ({ n: ++n, module: s.module, feature: r[0], model: r[1], type: r[2], phase: r[3], order: orderOf[n] })),
)

const missing = flat.filter((f) => !f.order).map((f) => f.n)
if (missing.length || order !== flat.length) throw new Error(`build order incomplete: missing ${missing.join(',')}, ordered ${order} of ${flat.length}`)

const byN = Object.fromEntries(flat.map((f) => [f.n, f]))

const counts = Object.fromEntries(Object.keys(typeColors).map((t) => [t, flat.filter((f) => f.type === t).length]))

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>CaseGraph feature and model map</title>
<style>
  @page { size: A4 landscape; margin: 14mm 12mm; }
  * { box-sizing: border-box; }
  body { font-family: "Segoe UI", Inter, Arial, sans-serif; color: #111; margin: 0; font-size: 10.5px; }
  header { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 3px solid #f5c518; padding-bottom: 8px; margin-bottom: 12px; }
  h1 { font-family: Georgia, "Times New Roman", serif; font-size: 22px; margin: 0; }
  h1 span { color: #b8860b; }
  .sub { color: #555; margin-top: 4px; font-size: 11px; }
  .legend { display: flex; gap: 8px; flex-wrap: wrap; font-size: 10px; }
  .chip { border-radius: 999px; padding: 2px 8px; color: #fff; font-weight: 600; white-space: nowrap; }
  table { width: 100%; border-collapse: collapse; }
  thead th { text-align: left; background: #111; color: #f5c518; padding: 6px 8px; font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em; }
  tbody td { padding: 5px 8px; border-bottom: 1px solid #e6e6e6; vertical-align: top; }
  tbody tr:nth-child(even) td { background: #fafafa; }
  tr.section td { background: #fff7d6 !important; font-weight: 700; color: #6f5708; border-top: 2px solid #f5c518; font-size: 11px; }
  td.n { color: #888; width: 28px; }
  td.order { width: 40px; font-weight: 800; color: #111; font-size: 12px; text-align: center; background: #fff7d6 !important; border-right: 2px solid #f5c518; }
  td.feature { width: 32%; font-weight: 600; }
  td.model { width: 38%; color: #333; }
  td.phase { text-align: center; width: 48px; font-weight: 700; }
  .p1 { color: #1f8a5b; } .p2 { color: #b8860b; } .p3 { color: #888; }
  tr.milestone td { background: #111 !important; color: #f5c518; font-weight: 700; font-size: 11.5px; padding: 8px; }
  tr.milestone td span { display: block; color: #ddd; font-weight: 400; font-size: 10px; margin-top: 2px; }
  thead { display: table-header-group; }
  tr { page-break-inside: avoid; }
  .break { page-break-before: always; }
  h2 { font-family: Georgia, "Times New Roman", serif; font-size: 17px; margin: 0 0 6px; }
  .howto { background: #fff7d6; border-left: 4px solid #f5c518; padding: 8px 12px; margin: 0 0 12px; font-size: 10.5px; line-height: 1.45; }
  .howto b { color: #6f5708; }
  footer { margin-top: 10px; font-size: 9.5px; color: #666; display: flex; justify-content: space-between; }
</style>
</head>
<body>
<header>
  <div>
    <h1>Case<span>Graph</span> build order and model map</h1>
    <div class="sub">50 features across four judiciary products, in the order to build them. Work one row at a time, top to bottom.</div>
  </div>
  <div class="legend">
    ${Object.entries(typeColors)
      .map(([t, c]) => `<span class="chip" style="background:${c}">${t} · ${counts[t]}</span>`)
      .join('')}
  </div>
</header>

<h2>Part 1. What to build, in order</h2>
<div class="howto">
  <b>How to read this:</b> the gold <b>Order</b> column is your to-do list. Start at 1 and do not skip ahead; each milestone only needs what came before it.
  <b>#</b> is the feature's fixed id, used in Part 2 and in the code. Six milestones: foundation, pendency models, legal research, bail with vision, consumer complaints, platform hardening.
</div>
<table>
  <thead><tr><th>Order</th><th>#</th><th>Feature</th><th>Model or technique needed</th><th>Type</th><th>Phase</th></tr></thead>
  <tbody>
  ${milestones
    .map(
      (m) =>
        `<tr class="milestone"><td colspan="6">${esc(m.name)}<span>${esc(m.goal)}</span></td></tr>` +
        m.features
          .map((id) => byN[id])
          .map(
            (f) => `<tr>
      <td class="order">${f.order}</td>
      <td class="n">${f.n}</td>
      <td class="feature">${esc(f.feature)}</td>
      <td class="model">${esc(f.model)}</td>
      <td><span class="chip" style="background:${typeColors[f.type]}">${f.type}</span></td>
      <td class="phase p${f.phase}">${f.phase}</td>
    </tr>`,
          )
          .join(''),
    )
    .join('')}
  </tbody>
</table>

<div class="break"></div>
<h2>Part 2. The same 50 features grouped by product</h2>
<div class="howto">Reference view. The <b>Order</b> column repeats the build position from Part 1 so you can see where each product's features fall in the sequence.</div>
<table>
  <thead><tr><th>Order</th><th>#</th><th>Feature</th><th>Model or technique needed</th><th>Type</th><th>Phase</th></tr></thead>
  <tbody>
  ${sections
    .map((s) => {
      const rows = flat.filter((f) => f.module === s.module)
      return `<tr class="section"><td colspan="6">${esc(s.module)}</td></tr>` +
        rows
          .map(
            (f) => `<tr>
      <td class="order">${f.order}</td>
      <td class="n">${f.n}</td>
      <td class="feature">${esc(f.feature)}</td>
      <td class="model">${esc(f.model)}</td>
      <td><span class="chip" style="background:${typeColors[f.type]}">${f.type}</span></td>
      <td class="phase p${f.phase}">${f.phase}</td>
    </tr>`,
          )
          .join('')
    })
    .join('')}
  </tbody>
</table>
<footer>
  <span>Sources: eCourts, NJDG, Indian Kanoon, SC/HC websites, NCDRC orders. Stack: Neo4j, LangChain, LangGraph, scikit-learn/LightGBM, PyTorch, vision LLM.</span>
  <span>Generated ${new Date().toISOString().slice(0, 10)}</span>
</footer>
</body>
</html>`

const md = `# CaseGraph - Build order and model map (50)

Four products in one platform: case pendency prediction, legal research, undertrial/bail monitoring, consumer complaint help.

Work the Order column top to bottom, one feature at a time. # is the fixed feature id. Phase 1 = foundation, 2 = core product, 3 = later.

## Part 1. Build order

${milestones
  .map(
    (m) =>
      `### ${m.name}\n\n${m.goal}\n\n| Order | # | Feature | Model or technique needed | Type | Phase |\n|---|---|---|---|---|---|\n` +
      m.features
        .map((id) => byN[id])
        .map((f) => `| ${f.order} | ${f.n} | ${f.feature} | ${f.model} | ${f.type} | ${f.phase} |`)
        .join('\n'),
  )
  .join('\n\n')}

## Part 2. Grouped by product

| Order | # | Feature | Model or technique needed | Type | Phase |
|---|---|---|---|---|---|
${sections
  .map((s) => `| | | **${s.module}** | | | |\n` + flat.filter((f) => f.module === s.module).map((f) => `| ${f.order} | ${f.n} | ${f.feature} | ${f.model} | ${f.type} | ${f.phase} |`).join('\n'))
  .join('\n')}

Counts: ${Object.entries(counts)
  .map(([t, c]) => `${t} ${c}`)
  .join(', ')}.
`

writeFileSync(join(here, 'features-table.html'), html)
writeFileSync(join(here, 'FEATURES.md'), md)
console.log(`wrote ${flat.length} rows`)
