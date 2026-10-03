import { Check } from 'lucide-react'
import Badge from '../components/ui/Badge'
import type { Module } from '../data/modules'

export default function ModulePlaceholder({ module }: { module: Module }) {
  const Icon = module.icon
  return (
    <div className="px-4 py-10 md:px-8">
      <div className="max-w-3xl">
        <span className="grid h-12 w-12 place-items-center rounded-xl border border-gold-400/25 bg-gold-400/10 text-gold-300">
          <Icon size={22} />
        </span>
        <div className="mt-6 flex flex-wrap items-center gap-3">
          <h1 className="font-display text-4xl font-medium text-cream-100">{module.name}</h1>
          <Badge tone="warn">UI in progress</Badge>
        </div>
        <p className="mt-2 text-lg text-gold-300/90">{module.tagline}</p>
        <p className="mt-4 text-base leading-relaxed text-cream-300">{module.description}</p>

        <div className="mt-10 rounded-2xl border hairline bg-ink-900/70 p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-400">Planned features</p>
          <ul className="mt-4 space-y-3">
            {module.features.map((f) => (
              <li key={f} className="flex items-start gap-3 text-sm text-cream-100">
                <Check size={16} className="mt-0.5 shrink-0 text-gold-400" />
                {f}
              </li>
            ))}
          </ul>
          <div className="mt-6 flex flex-wrap gap-1.5">
            {module.stack.map((s) => (
              <Badge key={s}>{s}</Badge>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
