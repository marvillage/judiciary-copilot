import { Check } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { plans } from '../../data/pricing'
import Badge from '../ui/Badge'
import Button from '../ui/Button'
import SectionHeading from '../ui/SectionHeading'

export default function PricingSection() {
  const [yearly, setYearly] = useState(true)
  return (
    <section id="pricing" className="mx-auto max-w-7xl px-4 py-24 md:px-8">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <SectionHeading
          eyebrow="Pricing"
          title="Start free. Scale with your practice."
          description="Every paid plan includes a 14-day trial. Prices in INR, exclusive of GST."
        />
        <div className="flex items-center gap-3 rounded-full border hairline bg-ink-900 p-1 text-sm">
          <button
            onClick={() => setYearly(false)}
            className={`rounded-full px-4 py-1.5 font-medium ${!yearly ? 'bg-gold-400 text-ink-950' : 'text-cream-300'}`}
          >
            Monthly
          </button>
          <button
            onClick={() => setYearly(true)}
            className={`rounded-full px-4 py-1.5 font-medium ${yearly ? 'bg-gold-400 text-ink-950' : 'text-cream-300'}`}
          >
            Yearly <span className={yearly ? 'text-ink-950/70' : 'text-gold-400'}>save 20%</span>
          </button>
        </div>
      </div>

      <div className="mt-12 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {plans.map((p) => {
          const price = yearly ? p.yearly : p.monthly
          return (
            <div
              key={p.name}
              className={`relative flex flex-col rounded-2xl border p-6 ${
                p.popular ? 'border-gold-400/60 bg-ink-900 glow' : 'hairline bg-ink-900/60'
              }`}
            >
              {p.popular && (
                <span className="absolute -top-3 left-6">
                  <Badge tone="gold">Most popular</Badge>
                </span>
              )}
              <p className="font-display text-xl font-medium text-cream-100">{p.name}</p>
              <p className="mt-1 text-sm text-cream-500">{p.tagline}</p>
              <div className="mt-6 flex items-baseline gap-1">
                {price === null ? (
                  <span className="text-3xl font-semibold text-cream-100">Custom</span>
                ) : price === 0 ? (
                  <span className="text-4xl font-semibold text-cream-100">Free</span>
                ) : (
                  <>
                    <span className="text-4xl font-semibold text-cream-100">
                      <span className="text-2xl text-gold-400">₹</span>
                      {price.toLocaleString('en-IN')}
                    </span>
                    <span className="text-sm text-cream-500">/ month</span>
                  </>
                )}
              </div>
              {price !== null && price > 0 && yearly && <p className="mt-1 text-xs text-cream-500">Billed yearly</p>}
              <ul className="mt-6 flex-1 space-y-2.5">
                {p.features.map((f) => (
                  <li key={f} className="flex items-start gap-2.5 text-sm text-cream-300">
                    <Check size={15} className="mt-0.5 shrink-0 text-gold-400" />
                    {f}
                  </li>
                ))}
              </ul>
              <Link to={price === null ? '#' : '/signup'} className="mt-8">
                <Button variant={p.popular ? 'primary' : 'outline'} className="w-full">
                  {p.cta}
                </Button>
              </Link>
            </div>
          )
        })}
      </div>
    </section>
  )
}
