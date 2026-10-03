import { ArrowRight } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import Logo from '../components/layout/Logo'
import Button from '../components/ui/Button'
import { brand } from '../data/brand'

type Props = { mode: 'login' | 'signup' }

const inputClass =
  'w-full rounded-lg border hairline bg-ink-900 px-3.5 py-2.5 text-sm text-cream-100 placeholder:text-cream-500 focus:border-gold-400/50 focus:outline-none'

export default function Auth({ mode }: Props) {
  const navigate = useNavigate()
  const signup = mode === 'signup'
  return (
    <div className="grid min-h-screen bg-ink-950 text-cream-100 lg:grid-cols-[1fr_1fr]">
      <div className="relative hidden overflow-hidden border-r hairline bg-ink-900 lg:block">
        <div className="grid-bg absolute inset-0" />
        <div className="absolute -left-32 bottom-0 h-96 w-96 rounded-full bg-gold-400/10 blur-3xl" />
        <div className="relative flex h-full flex-col justify-between p-12">
          <Logo />
          <div>
            <p className="font-display text-4xl font-medium leading-tight">
              Know how long. <br />
              Know what is good law. <br />
              <span className="gold-text">Know who is eligible.</span>
            </p>
            <p className="mt-6 max-w-md text-sm leading-relaxed text-cream-300">
              {brand.tagline}. Grounded in the eCourts and Indian Kanoon knowledge graph, reviewed by people before anything is filed.
            </p>
          </div>
          <p className="text-xs text-cream-500">Data stays in India. DPDP Act compliant.</p>
        </div>
      </div>

      <div className="flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-sm">
          <div className="lg:hidden">
            <Logo />
          </div>
          <h1 className="mt-8 font-display text-3xl font-medium">{signup ? 'Create your workspace' : 'Welcome back'}</h1>
          <p className="mt-2 text-sm text-cream-300">
            {signup ? 'Start a 14-day trial. No card required.' : `Sign in to your ${brand.name} workspace.`}
          </p>

          <form
            className="mt-8 space-y-4"
            onSubmit={(e) => {
              e.preventDefault()
              navigate('/app')
            }}
          >
            {signup && (
              <div>
                <label className="mb-1.5 block text-xs font-medium text-cream-300">Full name</label>
                <input className={inputClass} placeholder="Adv. Kushagra Srivastava" />
              </div>
            )}
            <div>
              <label className="mb-1.5 block text-xs font-medium text-cream-300">Work email</label>
              <input className={inputClass} type="email" placeholder="you@chambers.in" />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-cream-300">Password</label>
              <input className={inputClass} type="password" placeholder="At least 8 characters" />
            </div>
            {signup && (
              <div>
                <label className="mb-1.5 block text-xs font-medium text-cream-300">Bar Council enrolment number (optional)</label>
                <input className={inputClass} placeholder="D/1234/2019" />
              </div>
            )}
            <Button type="submit" className="w-full py-3">
              {signup ? 'Create workspace' : 'Sign in'} <ArrowRight size={16} />
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-cream-500">
            {signup ? 'Already have an account? ' : 'New here? '}
            <Link to={signup ? '/login' : '/signup'} className="font-semibold text-gold-300 hover:text-gold-200">
              {signup ? 'Sign in' : 'Start free trial'}
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
