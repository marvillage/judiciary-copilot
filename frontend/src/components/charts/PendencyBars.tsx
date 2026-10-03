import { useState } from 'react'
import { pendencyByAge as sampleBands } from '../../data/home'

export type Band = { band: string; share: number; count?: number }

type Props = { data?: Band[] | null; live?: boolean }

export default function PendencyBars({ data, live = false }: Props) {
  const bands: Band[] = data && data.length ? data : sampleBands
  const highlightIndex = bands.length - 1
  const [hover, setHover] = useState<number | null>(null)
  const max = Math.max(...bands.map((d) => d.share))
  const oldest = bands[highlightIndex]

  return (
    <div>
      <div className="flex items-baseline justify-between">
        <p className="text-sm font-semibold text-cream-100">Pending cases by age</p>
        <p className="text-xs text-cream-500">{live ? 'Live from the graph' : 'Share of all pending cases'}</p>
      </div>
      <ul className="mt-4 space-y-2.5">
        {bands.map((d, i) => {
          const isHighlight = i === highlightIndex
          const isHover = hover === i
          return (
            <li
              key={d.band}
              className="group grid grid-cols-[7rem_1fr_3rem] items-center gap-3 rounded-md py-1"
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
            >
              <span className={`text-xs ${isHighlight ? 'text-cream-100' : 'text-cream-300'}`}>{d.band}</span>
              <div className="relative h-3 rounded-r-[4px] bg-ink-800">
                <div
                  className={`h-full rounded-r-[4px] transition-colors ${
                    isHighlight ? 'bg-gold-400' : isHover ? 'bg-gold-600' : 'bg-gold-700'
                  }`}
                  style={{ width: `${(d.share / max) * 100}%` }}
                />
                {isHover && (
                  <div className="absolute -top-9 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-md border hairline bg-ink-700 px-2.5 py-1 text-xs text-cream-100 shadow-lg">
                    {d.band}: {d.share}% of pending cases{d.count != null ? ` (${d.count.toLocaleString('en-IN')})` : ''}
                  </div>
                )}
              </div>
              <span className={`text-right text-xs tabular-nums ${isHighlight ? 'font-semibold text-gold-300' : 'text-cream-500'}`}>
                {isHighlight || isHover ? `${d.share}%` : ''}
              </span>
            </li>
          )
        })}
      </ul>
      <p className="mt-4 text-xs leading-relaxed text-cream-500">
        {oldest.share}% of pending cases are in the oldest band. The pendency model targets these first.
      </p>
    </div>
  )
}
