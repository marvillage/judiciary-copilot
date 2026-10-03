import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { brand } from '../../data/brand'
import Sidebar from './Sidebar'
import Topbar from './Topbar'

export default function Layout() {
  const [open, setOpen] = useState(false)
  return (
    <div className="flex min-h-screen bg-ink-950 text-cream-100">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar onMenu={() => setOpen(true)} />
        <main className="flex-1">
          <Outlet />
        </main>
        <footer className="border-t hairline px-4 py-6 text-xs text-cream-500 md:px-8">
          {brand.name}. Built on public eCourts, NJDG and Indian Kanoon data. Not legal advice. Drafts are released only after human review.
        </footer>
      </div>
    </div>
  )
}
