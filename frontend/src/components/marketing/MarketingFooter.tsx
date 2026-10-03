import { Link } from 'react-router-dom'
import { brand } from '../../data/brand'
import { modules } from '../../data/modules'
import Logo from '../layout/Logo'

const columns = [
  { title: 'Products', links: modules.map((m) => ({ label: m.name, to: m.path })) },
  {
    title: 'Company',
    links: [
      { label: 'About', to: '#' },
      { label: 'Careers', to: '#' },
      { label: 'Contact', to: '#' },
    ],
  },
  {
    title: 'Resources',
    links: [
      { label: 'Documentation', to: '#' },
      { label: 'Model accuracy reports', to: '#' },
      { label: 'Data sources', to: '#' },
    ],
  },
  {
    title: 'Legal',
    links: [
      { label: 'Privacy', to: '#' },
      { label: 'Terms', to: '#' },
      { label: 'DPDP compliance', to: '#' },
    ],
  },
]

export default function MarketingFooter() {
  return (
    <footer className="border-t hairline bg-ink-950">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-14 md:grid-cols-[1.4fr_repeat(4,1fr)] md:px-8">
        <div>
          <Logo />
          <p className="mt-4 max-w-xs text-sm leading-relaxed text-cream-500">{brand.tagline}. Built on public court data, reviewed by people.</p>
        </div>
        {columns.map((c) => (
          <div key={c.title}>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-400">{c.title}</p>
            <ul className="mt-4 space-y-2.5">
              {c.links.map((l) => (
                <li key={l.label}>
                  <Link to={l.to} className="text-sm text-cream-300 hover:text-cream-100">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t hairline">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-6 text-xs text-cream-500 md:px-8">
          <span>2026 {brand.name}. Not legal advice.</span>
          <span>Made in India</span>
        </div>
      </div>
    </footer>
  )
}
