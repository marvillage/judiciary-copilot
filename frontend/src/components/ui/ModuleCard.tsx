import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { Module } from '../../data/modules'
import Badge from './Badge'

export default function ModuleCard({ module }: { module: Module }) {
  const Icon = module.icon
  return (
    <Link
      to={module.path}
      className="group relative flex flex-col rounded-2xl border hairline bg-ink-900/70 p-6 transition-all hover:-translate-y-0.5 hover:border-gold-400/40 hover:bg-ink-900"
    >
      <div className="flex items-start justify-between">
        <span className="grid h-11 w-11 place-items-center rounded-xl border border-gold-400/25 bg-gold-400/10 text-gold-300">
          <Icon size={20} />
        </span>
        <ArrowRight size={18} className="text-cream-500 transition-all group-hover:translate-x-0.5 group-hover:text-gold-300" />
      </div>
      <h3 className="mt-5 font-display text-xl font-medium text-cream-100">{module.name}</h3>
      <p className="mt-1 text-sm text-gold-300/90">{module.tagline}</p>
      <p className="mt-3 flex-1 text-sm leading-relaxed text-cream-300">{module.description}</p>
      <div className="mt-5 flex flex-wrap gap-1.5">
        {module.stack.map((s) => (
          <Badge key={s}>{s}</Badge>
        ))}
      </div>
    </Link>
  )
}
