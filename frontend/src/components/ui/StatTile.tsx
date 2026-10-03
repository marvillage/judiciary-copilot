import { ArrowDownRight, ArrowUpRight } from 'lucide-react'

type Props = { label: string; value: string; delta?: string; up?: boolean }

export default function StatTile({ label, value, delta, up = true }: Props) {
  return (
    <div className="rounded-xl border hairline bg-ink-900/70 p-5">
      <p className="text-xs font-medium uppercase tracking-[0.14em] text-cream-500">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-cream-100">{value}</p>
      {delta && (
        <p className={`mt-2 flex items-center gap-1 text-xs ${up ? 'text-good' : 'text-cream-300'}`}>
          {up ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
          {delta}
        </p>
      )}
    </div>
  )
}
