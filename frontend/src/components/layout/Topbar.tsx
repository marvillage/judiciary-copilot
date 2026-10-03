import { Bell, Menu, Plus, Search } from 'lucide-react'
import { DEMO_MODE } from '../../lib/api'
import Badge from '../ui/Badge'
import Button from '../ui/Button'

type Props = { onMenu: () => void }

export default function Topbar({ onMenu }: Props) {
  return (
    <header className="sticky top-0 z-20 flex items-center gap-3 border-b hairline bg-ink-950/85 px-4 py-3 backdrop-blur md:px-8">
      <button className="text-cream-300 hover:text-cream-100 lg:hidden" onClick={onMenu} aria-label="Open menu">
        <Menu size={20} />
      </button>

      <label className="hidden flex-1 items-center gap-2 rounded-lg border hairline bg-ink-900 px-3 py-2 text-sm text-cream-500 md:flex md:max-w-xl">
        <Search size={15} />
        <input
          className="w-full bg-transparent text-cream-100 placeholder:text-cream-500 focus:outline-none"
          placeholder="Search matters, judgments, sections or parties"
        />
        <kbd className="whitespace-nowrap rounded border border-ink-500 px-1.5 py-0.5 text-[10px] text-cream-500">Ctrl K</kbd>
      </label>

      <div className="ml-auto flex items-center gap-3">
        <Badge tone="gold">
          <span className="pulse-dot inline-block h-1.5 w-1.5 rounded-full bg-gold-400" />
          {DEMO_MODE ? 'Demo · sample data' : 'Sample data'}
        </Badge>
        <Button className="hidden px-3 py-2 sm:inline-flex">
          <Plus size={15} />
          New matter
        </Button>
        <button className="relative text-cream-300 hover:text-cream-100" aria-label="Notifications">
          <Bell size={18} />
          <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-gold-400" />
        </button>
        <span className="grid h-8 w-8 place-items-center rounded-full border border-gold-400/40 bg-ink-800 text-xs font-semibold text-gold-300">
          KS
        </span>
      </div>
    </header>
  )
}
