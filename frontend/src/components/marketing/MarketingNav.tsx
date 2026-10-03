import { Menu, X } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import Button from '../ui/Button'
import Logo from '../layout/Logo'

const links = [
  { label: 'Products', href: '#products' },
  { label: 'How it works', href: '#how' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'Security', href: '#security' },
  { label: 'FAQ', href: '#faq' },
]

export default function MarketingNav() {
  const [open, setOpen] = useState(false)
  return (
    <header className="sticky top-0 z-30 border-b hairline bg-ink-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 md:px-8">
        <Logo />
        <nav className="hidden items-center gap-8 md:flex">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="text-sm font-medium text-cream-300 hover:text-cream-100">
              {l.label}
            </a>
          ))}
        </nav>
        <div className="hidden items-center gap-2 md:flex">
          <Link to="/login" className="px-3 py-2 text-sm font-medium text-cream-300 hover:text-cream-100">
            Sign in
          </Link>
          <Link to="/signup">
            <Button>Start free trial</Button>
          </Link>
        </div>
        <button className="text-cream-300 md:hidden" onClick={() => setOpen(!open)} aria-label="Toggle menu">
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>
      {open && (
        <div className="border-t hairline px-4 py-4 md:hidden">
          <nav className="flex flex-col gap-1">
            {links.map((l) => (
              <a key={l.href} href={l.href} onClick={() => setOpen(false)} className="rounded-lg px-3 py-2.5 text-sm font-medium text-cream-300 hover:bg-ink-800">
                {l.label}
              </a>
            ))}
          </nav>
          <div className="mt-3 flex gap-2">
            <Link to="/login" className="flex-1">
              <Button variant="outline" className="w-full">
                Sign in
              </Button>
            </Link>
            <Link to="/signup" className="flex-1">
              <Button className="w-full">Start free trial</Button>
            </Link>
          </div>
        </div>
      )}
    </header>
  )
}
