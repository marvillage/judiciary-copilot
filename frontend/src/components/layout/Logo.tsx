import { Scale } from 'lucide-react'
import { Link } from 'react-router-dom'
import { brand } from '../../data/brand'

type Props = { to?: string; compact?: boolean }

export default function Logo({ to = '/', compact = false }: Props) {
  return (
    <Link to={to} className="flex items-center gap-2.5">
      <span className="grid h-9 w-9 place-items-center rounded-lg bg-gold-400 text-ink-950">
        <Scale size={18} strokeWidth={2.2} />
      </span>
      {!compact && (
        <span className="font-display text-xl font-semibold tracking-tight text-cream-100">
          Case<span className="text-gold-400">Graph</span>
        </span>
      )}
      <span className="sr-only">{brand.name}</span>
    </Link>
  )
}
