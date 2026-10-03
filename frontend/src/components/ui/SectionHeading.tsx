type Props = { eyebrow: string; title: string; description?: string }

export default function SectionHeading({ eyebrow, title, description }: Props) {
  return (
    <div className="max-w-2xl">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gold-400">{eyebrow}</p>
      <h2 className="mt-2 font-display text-3xl font-medium leading-tight text-cream-100 md:text-4xl">{title}</h2>
      {description && <p className="mt-3 text-sm leading-relaxed text-cream-300 md:text-base">{description}</p>}
    </div>
  )
}
