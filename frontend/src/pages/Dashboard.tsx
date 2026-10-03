import { ArrowRight, BookOpen, Clock, Landmark, RefreshCw, ShoppingBag } from 'lucide-react'
import { Link } from 'react-router-dom'
import PendencyBars from '../components/charts/PendencyBars'
import AgentTrace from '../components/ui/AgentTrace'
import Badge from '../components/ui/Badge'
import RiskBadge from '../components/ui/RiskBadge'
import StatTile from '../components/ui/StatTile'
import { brand } from '../data/brand'
import { alerts as sampleAlerts, dashboardStats, matters as sampleMatters, usage } from '../data/dashboard'
import { api, DEMO_MODE, type AgeBand, type AlertRow, type MatterRow, type Summary } from '../lib/api'
import { useApi } from '../lib/useApi'

const quickActions = [
  { label: 'Predict disposal', to: '/app/pendency', icon: Clock },
  { label: 'Research a brief', to: '/app/research', icon: BookOpen },
  { label: 'Check bail eligibility', to: '/app/bail', icon: Landmark },
  { label: 'Draft a complaint', to: '/app/consumer', icon: ShoppingBag },
]

function UsageRow({ label, used, limit }: { label: string; used: number; limit: number }) {
  const pct = Math.min(100, Math.round((used / limit) * 100))
  return (
    <div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-cream-300">{label}</span>
        <span className="tabular-nums text-cream-500">
          {used.toLocaleString('en-IN')} / {limit.toLocaleString('en-IN')}
        </span>
      </div>
      <div className="mt-1.5 h-1.5 rounded-full bg-ink-700">
        <div className={`h-full rounded-full ${pct > 85 ? 'bg-warn' : 'bg-gold-400'}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

function compact(n: number | null | undefined): string {
  if (n == null) return '–'
  if (n >= 1_00_00_000) return `${(n / 1_00_00_000).toFixed(1)} Cr`
  if (n >= 1_00_000) return `${(n / 1_00_000).toFixed(1)} L`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toLocaleString('en-IN')
}

function years(days: number | null | undefined): string {
  return days == null ? '–' : `${(days / 365.25).toFixed(1)} yrs`
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const h = Math.floor(diff / 36e5)
  if (h < 1) return 'just now'
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

export default function Dashboard() {
  const summary = useApi<Summary>('/dashboard/summary')
  const bands = useApi<AgeBand[]>('/dashboard/pendency-by-age')
  const matters = useApi<MatterRow[]>('/matters')
  const alerts = useApi<AlertRow[]>('/alerts?unread_only=true')
  const live = !summary.error && summary.data != null

  const refresh = async () => {
    await api('/matters/refresh', { method: 'POST' })
    matters.reload()
    alerts.reload()
  }

  const stats = live
    ? [
        { label: 'Cases in graph', value: compact(summary.data!.total), delta: `${compact(summary.data!.pending)} pending`, up: true },
        { label: 'Median time to disposal', value: years(summary.data!.median_days_to_disposal), delta: 'Disposed cases in graph', up: false },
        { label: 'Judgments indexed', value: compact(summary.data!.judgments), delta: `${compact(summary.data!.cites)} citation edges`, up: true },
        { label: 'Drafts awaiting review', value: String(summary.data!.pending_reviews), delta: `${summary.data!.matters} matters tracked`, up: summary.data!.pending_reviews === 0 },
      ]
    : dashboardStats

  return (
    <div className="px-4 py-8 md:px-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-400">{brand.workspace}</p>
          <h1 className="mt-1 font-display text-3xl font-medium">Good morning, Kushagra</h1>
          <p className="mt-1 text-sm text-cream-300">
            {live
              ? 'Connected to the CaseGraph API.'
              : DEMO_MODE
                ? 'Demo workspace. Every number here is sample data.'
                : 'API offline, showing sample data.'}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {quickActions.map((a) => (
            <Link
              key={a.to}
              to={a.to}
              className="inline-flex items-center gap-2 rounded-lg border hairline bg-ink-900 px-3 py-2 text-xs font-medium text-cream-300 hover:border-gold-400/40 hover:text-gold-300"
            >
              <a.icon size={14} />
              {a.label}
            </Link>
          ))}
        </div>
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((s) => (
          <StatTile key={s.label} {...s} />
        ))}
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-[1.6fr_1fr]">
        <div className="rounded-2xl border hairline bg-ink-900/70">
          <div className="flex items-center justify-between px-6 py-4">
            <p className="font-semibold text-cream-100">{live ? 'Tracked matters' : 'Upcoming hearings'}</p>
            <div className="flex items-center gap-3">
              {live && (
                <button onClick={refresh} className="inline-flex items-center gap-1 text-xs font-semibold text-cream-300 hover:text-gold-300">
                  <RefreshCw size={13} /> Refresh now
                </button>
              )}
              <Link to="/app/matters" className="inline-flex items-center gap-1 text-xs font-semibold text-gold-300 hover:text-gold-200">
                All matters <ArrowRight size={13} />
              </Link>
            </div>
          </div>
          <div className="overflow-x-auto">
            {live ? (
              <table className="w-full min-w-[40rem] text-left text-sm">
                <thead className="border-y hairline text-xs text-cream-500">
                  <tr>
                    <th className="px-6 py-2.5 font-medium">Matter</th>
                    <th className="px-3 py-2.5 font-medium">Court</th>
                    <th className="px-3 py-2.5 font-medium">Stage</th>
                    <th className="px-3 py-2.5 font-medium">Filed</th>
                    <th className="px-3 py-2.5 font-medium">Status</th>
                    <th className="px-6 py-2.5 font-medium">Alerts</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gold-400/10">
                  {(matters.data ?? []).map((m) => (
                    <tr key={m.matter.id} className="hover:bg-ink-800/60">
                      <td className="px-6 py-3">
                        <p className="font-medium text-cream-100">{m.matter.title}</p>
                        <p className="text-[11px] text-cream-500">{m.matter.cnr}</p>
                      </td>
                      <td className="px-3 py-3 text-cream-300">{m.court ?? '–'}</td>
                      <td className="px-3 py-3 text-cream-300">{m.case?.purpose ?? '–'}</td>
                      <td className="px-3 py-3 tabular-nums text-cream-300">{m.case?.filing_date ?? '–'}</td>
                      <td className="px-3 py-3">
                        <RiskBadge risk={m.case?.status === 'disposed' ? 'Low' : 'Medium'} label={m.case?.status ?? 'unknown'} />
                      </td>
                      <td className="px-6 py-3 tabular-nums text-cream-300">{m.unread_alerts}</td>
                    </tr>
                  ))}
                  {matters.data?.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-sm text-cream-500">
                        No matters tracked yet. Add one with a CNR from the graph.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            ) : (
              <table className="w-full min-w-[40rem] text-left text-sm">
                <thead className="border-y hairline text-xs text-cream-500">
                  <tr>
                    <th className="px-6 py-2.5 font-medium">Matter</th>
                    <th className="px-3 py-2.5 font-medium">Court</th>
                    <th className="px-3 py-2.5 font-medium">Stage</th>
                    <th className="px-3 py-2.5 font-medium">Next hearing</th>
                    <th className="px-3 py-2.5 font-medium">Predicted disposal</th>
                    <th className="px-6 py-2.5 font-medium">Stall risk</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gold-400/10">
                  {sampleMatters.map((m) => (
                    <tr key={m.cnr} className="hover:bg-ink-800/60">
                      <td className="px-6 py-3">
                        <p className="font-medium text-cream-100">{m.title}</p>
                        <p className="text-[11px] text-cream-500">{m.cnr}</p>
                      </td>
                      <td className="px-3 py-3 text-cream-300">{m.court}</td>
                      <td className="px-3 py-3 text-cream-300">{m.stage}</td>
                      <td className="px-3 py-3 tabular-nums text-cream-300">{m.next}</td>
                      <td className="px-3 py-3 tabular-nums text-cream-300">{m.disposal}</td>
                      <td className="px-6 py-3">
                        <RiskBadge risk={m.risk} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-2xl border hairline bg-ink-900/70 p-6">
            <div className="flex items-center justify-between">
              <p className="font-semibold text-cream-100">Alerts</p>
              <Badge tone="gold">{live ? alerts.data?.length ?? 0 : sampleAlerts.length} new</Badge>
            </div>
            <ul className="mt-4 space-y-4">
              {live
                ? (alerts.data ?? []).slice(0, 6).map((a) => (
                    <li key={a.alert.id} className="flex gap-3">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-gold-400" />
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-cream-500">
                          {a.alert.kind} <span className="font-normal normal-case tracking-normal">· {timeAgo(a.alert.created_at)} · {a.matter.title}</span>
                        </p>
                        <p className="mt-0.5 text-sm leading-relaxed text-cream-100">{a.alert.text}</p>
                      </div>
                    </li>
                  ))
                : sampleAlerts.map((a) => (
                    <li key={a.text} className="flex gap-3">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-gold-400" />
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-cream-500">
                          {a.kind} <span className="font-normal normal-case tracking-normal">· {a.time}</span>
                        </p>
                        <p className="mt-0.5 text-sm leading-relaxed text-cream-100">{a.text}</p>
                      </div>
                    </li>
                  ))}
              {live && alerts.data?.length === 0 && <li className="text-sm text-cream-500">No unread alerts. The tracker checks every hour.</li>}
            </ul>
          </div>

          <div className="rounded-2xl border hairline bg-ink-900/70 p-6">
            <div className="flex items-center justify-between">
              <p className="font-semibold text-cream-100">Plan usage</p>
              <Badge>{brand.plan}</Badge>
            </div>
            <div className="mt-4 space-y-4">
              <UsageRow label="Matters" used={live ? summary.data!.matters : usage.matters.used} limit={usage.matters.limit} />
              <UsageRow label="AI credits" used={usage.credits.used} limit={usage.credits.limit} />
              <UsageRow label="Seats" used={usage.seats.used} limit={usage.seats.limit} />
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-[1fr_1.2fr]">
        <div className="rounded-2xl border hairline bg-ink-900/70 p-6">
          <PendencyBars data={live ? bands.data : null} live={live && !!bands.data?.length} />
        </div>
        <AgentTrace />
      </div>
    </div>
  )
}
