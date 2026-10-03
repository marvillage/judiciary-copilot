export const dashboardStats = [
  { label: 'Active matters', value: '42', delta: '+3 this month', up: true },
  { label: 'Hearings this week', value: '9', delta: '2 tomorrow', up: true },
  { label: 'Drafts awaiting review', value: '5', delta: '2 overdue', up: false },
  { label: 'Precedent alerts', value: '3', delta: 'Since Monday', up: true },
]

export type Risk = 'High' | 'Medium' | 'Low'

export const matters: { cnr: string; title: string; court: string; stage: string; next: string; disposal: string; risk: Risk }[] = [
  { cnr: 'DLST01-004512-2024', title: 'State v. R. Kumar', court: 'Saket District Court', stage: 'Evidence', next: '18 Sep 2026', disposal: '2.1 yrs', risk: 'High' },
  { cnr: 'MHAU01-011893-2025', title: 'Mehta v. Urban Homes LLP', court: 'Aurangabad Consumer Forum', stage: 'Arguments', next: '22 Sep 2026', disposal: '0.6 yrs', risk: 'Low' },
  { cnr: 'KABG01-002271-2023', title: 'Iyer v. State of Karnataka', court: 'Karnataka High Court', stage: 'Bail hearing', next: '15 Sep 2026', disposal: '0.2 yrs', risk: 'Medium' },
  { cnr: 'UPGB01-020034-2022', title: 'Sharma v. Sharma', court: 'Ghaziabad Family Court', stage: 'Mediation', next: '30 Sep 2026', disposal: '1.4 yrs', risk: 'Medium' },
  { cnr: 'TNCH01-007710-2024', title: 'Rao v. Southern Motors', court: 'Chennai Consumer Commission', stage: 'Filing', next: '02 Oct 2026', disposal: '0.9 yrs', risk: 'Low' },
]

export const alerts = [
  { kind: 'Precedent', text: 'A judgment you rely on in Iyer v. State was distinguished by a Kerala HC bench yesterday.', time: '2h ago' },
  { kind: 'Order', text: 'New order uploaded on DLST01-004512-2024. Evidence adjourned to 18 Sep.', time: '5h ago' },
  { kind: 'Review', text: 'Bail application draft for Iyer is waiting for your approval.', time: 'Yesterday' },
  { kind: 'Deadline', text: 'Limitation for Rao v. Southern Motors ends in 41 days.', time: 'Yesterday' },
]

export const usage = {
  matters: { used: 31, limit: 50 },
  credits: { used: 1240, limit: 5000 },
  seats: { used: 1, limit: 1 },
}
