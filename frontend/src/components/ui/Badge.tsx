import type { ReactNode } from 'react'

type Props = { children: ReactNode; tone?: 'gold' | 'muted' | 'good' | 'warn' }

const tones = {
  gold: 'border-gold-400/30 bg-gold-400/10 text-gold-300',
  muted: 'border-ink-500 bg-ink-800 text-cream-300',
  good: 'border-good/30 bg-good/10 text-good',
  warn: 'border-warn/30 bg-warn/10 text-warn',
}

export default function Badge({ children, tone = 'muted' }: Props) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-medium tracking-wide ${tones[tone]}`}
    >
      {children}
    </span>
  )
}
