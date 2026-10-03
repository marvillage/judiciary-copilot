export type Plan = {
  name: string
  tagline: string
  monthly: number | null
  yearly: number | null
  features: string[]
  cta: string
  popular?: boolean
}

export const plans: Plan[] = [
  {
    name: 'Litigant',
    tagline: 'Track your own matters',
    monthly: 0,
    yearly: 0,
    features: ['Up to 3 matters', 'Pendency prediction', 'Hearing and order alerts', 'Consumer complaint drafting'],
    cta: 'Start free',
  },
  {
    name: 'Advocate',
    tagline: 'For independent practitioners',
    monthly: 1999,
    yearly: 1599,
    popular: true,
    features: [
      'Up to 50 matters',
      'Legal research with citation graph',
      'Bail eligibility and application drafts',
      '5,000 AI credits a month',
      'Export to DOCX and PDF',
    ],
    cta: 'Start 14-day trial',
  },
  {
    name: 'Chamber',
    tagline: 'For chambers and small firms',
    monthly: 7999,
    yearly: 6399,
    features: ['10 seats included', 'Unlimited matters', 'Shared research workspaces', 'Review queues and approvals', 'Priority support'],
    cta: 'Start 14-day trial',
  },
  {
    name: 'Legal Aid & Enterprise',
    tagline: 'For DLSAs, NGOs and large firms',
    monthly: null,
    yearly: null,
    features: ['Undertrial monitoring dashboards', 'Prison and district rollups', 'SSO and audit logs', 'Data residency in India', 'Dedicated onboarding'],
    cta: 'Talk to sales',
  },
]

export const audiences = ['District bar chambers', 'Legal aid clinics', 'Law firms', 'Consumer forums', 'Law school clinics', 'In-house legal teams']

export const securityPoints = [
  { title: 'Data stays in India', detail: 'All storage and inference run in Indian regions, in line with the DPDP Act.' },
  { title: 'Verified citations only', detail: 'A draft cannot cite a judgment that does not resolve to a node in the graph.' },
  { title: 'Human review on every filing', detail: 'Bail applications and complaints stop at a review queue before release.' },
  { title: 'Full audit trail', detail: 'Every automated step is logged with inputs, outputs and the reviewer who approved it.' },
]

export const faqs = [
  {
    q: 'Is this legal advice?',
    a: 'No. The platform produces predictions, research and drafts for a qualified person to review. Nothing is filed automatically.',
  },
  {
    q: 'Where does the data come from?',
    a: 'Public sources: eCourts, the National Judicial Data Grid, Indian Kanoon, Supreme Court and High Court websites, and NCDRC orders. You can also upload your own scanned orders.',
  },
  {
    q: 'How accurate are the pendency predictions?',
    a: 'Each prediction ships with a confidence range and a benchmark against similar cases in the same court. Accuracy is reported per court and case type inside the app.',
  },
  {
    q: 'Does it work in Hindi and regional languages?',
    a: 'Questions and drafts are supported in Hindi with major regional languages rolling out, starting with Marathi, Tamil and Bengali.',
  },
  {
    q: 'Can I cancel any time?',
    a: 'Yes. Monthly plans cancel at the end of the billing period and you can export all your matters and research before you leave.',
  },
]
