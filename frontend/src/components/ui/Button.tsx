import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'ghost' | 'outline'
  children: ReactNode
}

const variants = {
  primary: 'bg-gold-400 text-ink-950 hover:bg-gold-300 shadow-[0_8px_30px_-10px_rgba(245,197,24,0.6)]',
  ghost: 'text-cream-300 hover:text-cream-100 hover:bg-ink-800',
  outline: 'border border-gold-400/30 text-gold-300 hover:border-gold-400/60 hover:bg-gold-400/5',
}

export default function Button({ variant = 'primary', className = '', children, ...rest }: Props) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors ${variants[variant]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  )
}
