import { ChevronDown } from 'lucide-react'
import { useState } from 'react'
import { faqs } from '../../data/pricing'
import SectionHeading from '../ui/SectionHeading'

export default function FaqSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0)
  return (
    <section id="faq" className="mx-auto grid max-w-7xl gap-10 px-4 py-24 md:px-8 lg:grid-cols-[1fr_1.4fr]">
      <SectionHeading eyebrow="FAQ" title="Questions lawyers ask us first." />
      <div className="divide-y divide-gold-400/10 rounded-2xl border hairline bg-ink-900/60">
        {faqs.map((f, i) => {
          const open = openIndex === i
          return (
            <div key={f.q}>
              <button
                className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left"
                onClick={() => setOpenIndex(open ? null : i)}
              >
                <span className="text-sm font-semibold text-cream-100 md:text-base">{f.q}</span>
                <ChevronDown size={18} className={`shrink-0 text-gold-400 transition-transform ${open ? 'rotate-180' : ''}`} />
              </button>
              {open && <p className="px-6 pb-5 text-sm leading-relaxed text-cream-300">{f.a}</p>}
            </div>
          )
        })}
      </div>
    </section>
  )
}
