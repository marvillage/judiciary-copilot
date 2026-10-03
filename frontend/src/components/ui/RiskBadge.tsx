import { AlertTriangle, CheckCircle2, CircleAlert } from 'lucide-react'
import type { Risk } from '../../data/dashboard'

const styles: Record<Risk, { cls: string; Icon: typeof AlertTriangle }> = {
  High: { cls: 'border-bad/30 bg-bad/10 text-bad', Icon: AlertTriangle },
  Medium: { cls: 'border-warn/30 bg-warn/10 text-warn', Icon: CircleAlert },
  Low: { cls: 'border-good/30 bg-good/10 text-good', Icon: CheckCircle2 },
}

export default function RiskBadge({ risk, label }: { risk: Risk; label?: string }) {
  const { cls, Icon } = styles[risk]
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium capitalize ${cls}`}>
      <Icon size={11} />
      {label ?? risk}
    </span>
  )
}
