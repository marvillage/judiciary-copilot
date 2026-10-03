import { ArrowRight, Database, FileText, Lock, ScanEye, ShieldCheck, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'
import AppPreview from '../components/marketing/AppPreview'
import FaqSection from '../components/marketing/FaqSection'
import MarketingFooter from '../components/marketing/MarketingFooter'
import MarketingNav from '../components/marketing/MarketingNav'
import PricingSection from '../components/marketing/PricingSection'
import AgentTrace from '../components/ui/AgentTrace'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import ModuleCard from '../components/ui/ModuleCard'
import SectionHeading from '../components/ui/SectionHeading'
import StatTile from '../components/ui/StatTile'
import { pipeline, stats } from '../data/home'
import { modules } from '../data/modules'
import { audiences, securityPoints } from '../data/pricing'

const pipelineIcons = [Database, ShieldCheck, Sparkles, FileText, ScanEye]

export default function Landing() {
  return (
    <div className="bg-ink-950 text-cream-100">
      <MarketingNav />

      <section className="relative overflow-hidden">
        <div className="grid-bg absolute inset-0" />
        <div className="absolute left-1/2 top-0 h-[32rem] w-[48rem] -translate-x-1/2 rounded-full bg-gold-400/10 blur-3xl" />
        <div className="relative mx-auto max-w-7xl px-4 pb-16 pt-20 text-center md:px-8 md:pt-28">
          <Badge tone="gold">Built on eCourts, NJDG and Indian Kanoon data</Badge>
          <h1 className="mx-auto mt-6 max-w-4xl font-display text-4xl font-medium leading-[1.05] md:text-7xl">
            Litigation intelligence <span className="gold-text">for Indian courts.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-cream-300 md:text-lg">
            Predict how long a case will take, verify whether a precedent is still good law, find undertrials eligible for
            bail and draft consumer complaints. One workspace, one knowledge graph, human review on every filing.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link to="/signup">
              <Button className="px-6 py-3 text-base">
                Start free trial <ArrowRight size={16} />
              </Button>
            </Link>
            <Link to="/app">
              <Button variant="outline" className="px-6 py-3 text-base">
                View live demo
              </Button>
            </Link>
          </div>
          <p className="mt-4 text-xs text-cream-500">14-day trial on paid plans. No card required.</p>

          <div className="mt-16">
            <AppPreview />
          </div>
        </div>
      </section>

      <section className="border-y hairline bg-ink-900/40">
        <div className="mx-auto max-w-7xl px-4 py-8 md:px-8">
          <p className="text-center text-xs font-semibold uppercase tracking-[0.18em] text-cream-500">Built for</p>
          <div className="mt-5 flex flex-wrap items-center justify-center gap-x-10 gap-y-3">
            {audiences.map((a) => (
              <span key={a} className="font-display text-lg text-cream-300">
                {a}
              </span>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-24 md:px-8">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {stats.map((s) => (
            <StatTile key={s.label} {...s} />
          ))}
        </div>
      </section>

      <section id="products" className="mx-auto max-w-7xl px-4 pb-24 md:px-8">
        <div className="flex flex-wrap items-end justify-between gap-6">
          <SectionHeading
            eyebrow="Products"
            title="Four products, one graph."
            description="Every product runs on the same knowledge graph, so a bail check can cite the same judgment your research found and your matter tracker already knows the court."
          />
          <Link to="/app/graph" className="inline-flex items-center gap-2 text-sm font-semibold text-gold-300 hover:text-gold-200">
            Explore the graph <ArrowRight size={16} />
          </Link>
        </div>
        <div className="mt-10 grid gap-4 md:grid-cols-2">
          {modules.slice(0, 4).map((m) => (
            <ModuleCard key={m.path} module={m} />
          ))}
        </div>
      </section>

      <section id="how" className="border-y hairline bg-ink-900/40">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 py-24 md:px-8 lg:grid-cols-[1fr_1.1fr]">
          <div>
            <SectionHeading
              eyebrow="How it works"
              title="From scanned order to reviewed draft."
              description="The pipeline is the same for every product. Only the models and the templates change."
            />
            <ol className="mt-8 space-y-3">
              {pipeline.map((p, i) => {
                const Icon = pipelineIcons[i]
                return (
                  <li key={p.step} className="flex gap-4 rounded-xl border hairline bg-ink-950/60 p-4">
                    <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-gold-400/10 text-gold-300">
                      <Icon size={18} />
                    </span>
                    <div>
                      <p className="flex items-center gap-2 text-sm font-semibold text-cream-100">
                        <span className="text-gold-400">0{i + 1}</span> {p.step}
                      </p>
                      <p className="mt-1 text-sm leading-relaxed text-cream-300">{p.detail}</p>
                    </div>
                  </li>
                )
              })}
            </ol>
          </div>
          <AgentTrace />
        </div>
      </section>

      <PricingSection />

      <section id="security" className="border-y hairline bg-ink-900/40">
        <div className="mx-auto max-w-7xl px-4 py-24 md:px-8">
          <SectionHeading
            eyebrow="Security and compliance"
            title="Nothing is filed without a person signing off."
            description="Legal work needs trust more than speed. These are the guarantees built into the product, not the terms of service."
          />
          <div className="mt-10 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {securityPoints.map((s) => (
              <div key={s.title} className="rounded-2xl border hairline bg-ink-950/60 p-6">
                <Lock size={18} className="text-gold-400" />
                <p className="mt-4 font-semibold text-cream-100">{s.title}</p>
                <p className="mt-2 text-sm leading-relaxed text-cream-300">{s.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <FaqSection />

      <section className="mx-auto max-w-7xl px-4 pb-24 md:px-8">
        <div className="overflow-hidden rounded-3xl border border-gold-400/30 bg-gradient-to-br from-gold-400/20 via-ink-900 to-ink-950 p-8 text-center md:p-16">
          <h2 className="font-display text-3xl font-medium leading-tight md:text-5xl">Bring your first matter in today.</h2>
          <p className="mx-auto mt-4 max-w-xl text-sm text-cream-300 md:text-base">
            Enter a CNR number and get a disposal estimate, the stall risk and every relevant precedent in under a minute.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link to="/signup">
              <Button className="px-6 py-3 text-base">Start free trial</Button>
            </Link>
            <a href="#pricing">
              <Button variant="outline" className="px-6 py-3 text-base">
                Compare plans
              </Button>
            </a>
          </div>
        </div>
      </section>

      <MarketingFooter />
    </div>
  )
}
