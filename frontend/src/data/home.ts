export const stats = [
  { label: 'Judgments in graph', value: '2.4M', delta: '+38K this week', up: true },
  { label: 'Citation edges', value: '18.7M', delta: '+412K this week', up: true },
  { label: 'Undertrials flagged eligible', value: '1,284', delta: '+96 this week', up: true },
  { label: 'Median predicted disposal', value: '3.2 yrs', delta: '-0.1 vs last quarter', up: false },
]

export const pendencyByAge = [
  { band: 'Under 1 year', share: 38 },
  { band: '1 to 3 years', share: 27 },
  { band: '3 to 5 years', share: 14 },
  { band: '5 to 10 years', share: 13 },
  { band: 'Over 10 years', share: 8 },
]

export const quickPrompts = [
  'How long will my case take?',
  'Is Arnesh Kumar v. State of Bihar still good law?',
  'Check bail eligibility under BNSS 479',
  'Draft a consumer complaint for a defective phone',
]

export const pipeline = [
  { step: 'Ingest', detail: 'eCourts, NJDG, Indian Kanoon and scanned orders read by a vision model' },
  { step: 'Graph', detail: 'Cases, judges, statutes and citations resolved into Neo4j' },
  { step: 'Predict', detail: 'Disposal time, stall stage and eligibility from trained models' },
  { step: 'Draft', detail: 'Memos, bail applications and complaints with verified citations' },
  { step: 'Review', detail: 'A human gate before anything is filed or released' },
]

export type TraceState = 'done' | 'running' | 'pending'

export const agentTrace: { node: string; label: string; result: string; state: TraceState }[] = [
  { node: 'classify_intent', label: 'Classify intent', result: 'bail_eligibility', state: 'done' },
  { node: 'extract_remand_orders', label: 'Read remand orders (vision)', result: '3 orders, 412 days in custody', state: 'done' },
  { node: 'query_statute_graph', label: 'Query statute graph', result: 'BNS 303(2), maximum 7 years', state: 'done' },
  { node: 'compute_eligibility', label: 'Compute BNSS 479 threshold', result: 'One-third threshold at 852 days, not yet reached', state: 'done' },
  { node: 'find_precedents', label: 'Find bail precedents', result: '6 matches, 4 verified in graph', state: 'running' },
  { node: 'human_review', label: 'Human review gate', result: 'Awaiting legal aid lawyer', state: 'pending' },
]
