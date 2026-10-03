import type { LucideIcon } from 'lucide-react'
import { BookOpen, Clock, Landmark, Network, ShoppingBag } from 'lucide-react'

export type Module = {
  path: string
  name: string
  tagline: string
  description: string
  icon: LucideIcon
  features: string[]
  stack: string[]
}

export const modules: Module[] = [
  {
    path: '/app/pendency',
    name: 'Pendency Predictor',
    tagline: 'How long will this case take, and why?',
    description:
      'Predicts time to disposal, the stage most likely to stall, and adjournment risk for the next hearing, then explains the delay drivers in plain language.',
    icon: Clock,
    features: [
      'Time-to-disposal prediction with a confidence range',
      'Stage-wise stall and adjournment likelihood',
      'Delay driver explanation in plain language',
      'Benchmark against similar cases in the same court',
      'Matter tracker with alerts on new orders',
    ],
    stack: ['Gradient boosting', 'Sequence model', 'Neo4j', 'LangGraph'],
  },
  {
    path: '/app/research',
    name: 'Legal Research',
    tagline: 'Precedents you can trust, with the citation graph to prove it.',
    description:
      'Semantic search from a plain-language brief, treatment status for every judgment, conflicting bench detection and research memos with verified citations only.',
    icon: BookOpen,
    features: [
      'Brief-to-precedent semantic search',
      'Is this still good law: followed, distinguished, overruled',
      'Conflicting bench detection across High Courts',
      'Memo drafting with a citation verifier gate',
      'Old-to-new code cross reference (IPC to BNS)',
    ],
    stack: ['Embeddings', 'GraphRAG', 'Neo4j', 'LangChain'],
  },
  {
    path: '/app/bail',
    name: 'Bail & Undertrial',
    tagline: 'Find who is eligible for release and draft the application.',
    description:
      'Reads scanned remand orders with a vision model, computes custody served against BNSS Section 479 thresholds, and drafts bail applications for a lawyer to review.',
    icon: Landmark,
    features: [
      'Eligibility under BNSS Section 479',
      'Custody period from vision-extracted remand orders',
      'Bail precedent finder for similar facts',
      'Legal aid queue prioritised by custody time',
      'Mandatory human review before any draft is released',
    ],
    stack: ['Vision model', 'Statute graph', 'LangGraph', 'GenAI'],
  },
  {
    path: '/app/consumer',
    name: 'Consumer Complaint',
    tagline: 'From a photo of the bill to a filed complaint.',
    description:
      'Extracts facts from bills, warranty cards and chat screenshots, finds the right forum, checks limitation, and drafts the complaint in the prescribed format.',
    icon: ShoppingBag,
    features: [
      'Evidence intake from photos and screenshots',
      'Forum and jurisdiction finder by claim value',
      'Limitation period check with reminders',
      'Complaint drafting with relief computation',
      'Outcome estimate from past NCDRC orders',
    ],
    stack: ['Vision model', 'Classifier', 'Neo4j', 'GenAI'],
  },
  {
    path: '/app/graph',
    name: 'Knowledge Graph',
    tagline: 'Cases, judges, statutes and citations as one connected graph.',
    description:
      'Explore how judgments cite each other, which sections they interpret and where courts disagree. Every answer on the platform links back to nodes here.',
    icon: Network,
    features: [
      'Interactive citation graph for any judgment',
      'Statute-centric timeline of interpreting judgments',
      'Entity resolution across eCourts and Indian Kanoon',
      'Cypher query console',
    ],
    stack: ['Neo4j', 'Cypher', 'Entity resolution'],
  },
]
