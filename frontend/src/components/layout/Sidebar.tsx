import { ChevronsUpDown, FolderOpen, LayoutDashboard, Settings, X, Zap } from 'lucide-react'
import { Link, NavLink } from 'react-router-dom'
import { brand } from '../../data/brand'
import { usage } from '../../data/dashboard'
import { modules } from '../../data/modules'
import Logo from './Logo'

type Props = { open: boolean; onClose: () => void }

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-3 rounded-lg border px-3 py-2.5 text-sm font-medium transition-colors ${
    isActive
      ? 'border-gold-400/20 bg-gold-400/10 text-gold-300'
      : 'border-transparent text-cream-300 hover:bg-ink-800 hover:text-cream-100'
  }`

export default function Sidebar({ open, onClose }: Props) {
  const creditPct = Math.round((usage.credits.used / usage.credits.limit) * 100)
  return (
    <>
      {open && <div className="fixed inset-0 z-30 bg-black/70 lg:hidden" onClick={onClose} />}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r hairline bg-ink-950 transition-transform lg:static lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between px-5 py-5">
          <Logo to="/app" />
          <button className="text-cream-500 hover:text-cream-100 lg:hidden" onClick={onClose} aria-label="Close menu">
            <X size={18} />
          </button>
        </div>

        <button className="mx-3 mb-4 flex items-center justify-between rounded-lg border hairline bg-ink-900 px-3 py-2.5 text-left hover:border-gold-400/30">
          <span>
            <span className="block text-sm font-semibold text-cream-100">{brand.workspace}</span>
            <span className="block text-[11px] text-cream-500">{brand.plan} plan</span>
          </span>
          <ChevronsUpDown size={15} className="text-cream-500" />
        </button>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3">
          <NavLink to="/app" end className={linkClass} onClick={onClose}>
            <LayoutDashboard size={17} />
            Dashboard
          </NavLink>
          <NavLink to="/app/matters" className={linkClass} onClick={onClose}>
            <FolderOpen size={17} />
            Matters
          </NavLink>
          <p className="px-3 pb-1 pt-5 text-[10px] font-semibold uppercase tracking-[0.18em] text-cream-500">Products</p>
          {modules.map((m) => (
            <NavLink key={m.path} to={m.path} className={linkClass} onClick={onClose}>
              <m.icon size={17} />
              {m.name}
            </NavLink>
          ))}
        </nav>

        <div className="m-3 rounded-xl border hairline bg-ink-900 p-4">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-cream-100">AI credits</span>
            <span className="text-cream-500">
              {usage.credits.used.toLocaleString('en-IN')} / {usage.credits.limit.toLocaleString('en-IN')}
            </span>
          </div>
          <div className="mt-2 h-1.5 rounded-full bg-ink-700">
            <div className="h-full rounded-full bg-gold-400" style={{ width: `${creditPct}%` }} />
          </div>
          <Link
            to="/#pricing"
            className="mt-3 flex items-center justify-center gap-1.5 rounded-lg border border-gold-400/30 py-2 text-xs font-semibold text-gold-300 hover:bg-gold-400/5"
          >
            <Zap size={13} />
            Upgrade to Chamber
          </Link>
        </div>

        <div className="px-3 pb-4">
          <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-cream-300 hover:bg-ink-800 hover:text-cream-100">
            <Settings size={17} />
            Settings
          </button>
        </div>
      </aside>
    </>
  )
}
