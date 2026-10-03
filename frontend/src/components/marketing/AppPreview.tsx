import { matters } from '../../data/dashboard'
import PendencyBars from '../charts/PendencyBars'
import RiskBadge from '../ui/RiskBadge'

export default function AppPreview() {
  return (
    <div className="glow overflow-hidden rounded-2xl border border-gold-400/25 bg-ink-900">
      <div className="flex items-center gap-2 border-b hairline px-4 py-2.5">
        <span className="h-2.5 w-2.5 rounded-full bg-ink-500" />
        <span className="h-2.5 w-2.5 rounded-full bg-ink-500" />
        <span className="h-2.5 w-2.5 rounded-full bg-gold-400/70" />
        <span className="ml-3 rounded-md bg-ink-800 px-3 py-1 text-[11px] text-cream-500">app.casegraph.in/dashboard</span>
      </div>
      <div className="grid gap-4 p-4 lg:grid-cols-[1.4fr_1fr]">
        <div className="rounded-xl border hairline bg-ink-950/60 p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-cream-100">Matters at risk</p>
            <span className="text-xs text-cream-500">Next 30 days</span>
          </div>
          <table className="mt-3 w-full text-left text-xs">
            <thead className="text-cream-500">
              <tr>
                <th className="pb-2 font-medium">Matter</th>
                <th className="pb-2 font-medium">Stage</th>
                <th className="pb-2 font-medium">Disposal</th>
                <th className="pb-2 font-medium">Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gold-400/10">
              {matters.slice(0, 4).map((m) => (
                <tr key={m.cnr}>
                  <td className="py-2 text-cream-100">{m.title}</td>
                  <td className="py-2 text-cream-300">{m.stage}</td>
                  <td className="py-2 tabular-nums text-cream-300">{m.disposal}</td>
                  <td className="py-2">
                    <RiskBadge risk={m.risk} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="rounded-xl border hairline bg-ink-950/60 p-4">
          <PendencyBars />
        </div>
      </div>
    </div>
  )
}
