import { Check, Loader2, UserCheck } from 'lucide-react'
import { agentTrace } from '../../data/home'
import Badge from './Badge'

export default function AgentTrace() {
  return (
    <div className="rounded-2xl border hairline bg-ink-900/70 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-400">Automation run</p>
          <p className="mt-1 font-display text-lg text-cream-100">Bail eligibility check</p>
        </div>
        <Badge tone="warn">
          <span className="pulse-dot inline-block h-1.5 w-1.5 rounded-full bg-warn" />
          Running
        </Badge>
      </div>

      <ol className="mt-6 space-y-0">
        {agentTrace.map((t, i) => {
          const last = i === agentTrace.length - 1
          return (
            <li key={t.node} className="relative flex gap-4 pb-5">
              {!last && <span className="absolute left-[11px] top-6 h-full w-px bg-ink-600" />}
              <span
                className={`relative z-10 mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-full border ${
                  t.state === 'done'
                    ? 'border-gold-400 bg-gold-400 text-ink-950'
                    : t.state === 'running'
                      ? 'border-gold-400/60 bg-ink-900 text-gold-300'
                      : 'border-ink-500 bg-ink-900 text-cream-500'
                }`}
              >
                {t.state === 'done' && <Check size={13} strokeWidth={3} />}
                {t.state === 'running' && <Loader2 size={13} className="animate-spin" />}
                {t.state === 'pending' && <UserCheck size={13} />}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-baseline justify-between gap-x-3">
                  <p className={`text-sm font-medium ${t.state === 'pending' ? 'text-cream-500' : 'text-cream-100'}`}>{t.label}</p>
                  <code className="text-[11px] text-cream-500">{t.node}</code>
                </div>
                <p className={`mt-0.5 text-xs ${t.state === 'pending' ? 'text-cream-500' : 'text-cream-300'}`}>{t.result}</p>
              </div>
            </li>
          )
        })}
      </ol>
    </div>
  )
}
