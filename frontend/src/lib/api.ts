/*
 * API base and demo mode.
 *
 * Demo mode skips every network call and lets pages fall back to the bundled
 * sample data straight away. It is on when:
 *   - VITE_DEMO is "1" / "true"                      (explicit switch, wins over everything)
 *   - VITE_API_BASE is "" or "demo"                  (no API configured)
 *   - VITE_API_BASE is unset in a production build   (never call localhost from visitors' browsers)
 * VITE_DEMO = "0" / "false" forces live mode. Local dev with nothing set keeps
 * using http://localhost:8000 as before.
 */
const rawBase = import.meta.env.VITE_API_BASE as string | undefined
const rawDemo = String(import.meta.env.VITE_DEMO ?? '').trim().toLowerCase()

function resolveDemo(): boolean {
  if (rawDemo === '1' || rawDemo === 'true') return true
  if (rawDemo === '0' || rawDemo === 'false') return false
  if (rawBase !== undefined) {
    const base = rawBase.trim().toLowerCase()
    return base === '' || base === 'demo'
  }
  return import.meta.env.PROD
}

export const DEMO_MODE = resolveDemo()

export const API_BASE = DEMO_MODE ? '' : rawBase?.trim() || 'http://localhost:8000'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  if (DEMO_MODE) throw new ApiError(0, 'Demo mode: the CaseGraph API is not connected')
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })
  if (!res.ok) throw new ApiError(res.status, await res.text())
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

export type Summary = {
  total: number
  pending: number
  disposed: number
  mean_days_to_disposal: number | null
  median_days_to_disposal: number | null
  judgments: number
  cites: number
  sections: number
  matters: number
  pending_reviews: number
}

export type AgeBand = { band: string; count: number; share: number }

export type MatterRow = {
  matter: { id: string; cnr: string; title: string; owner: string; created_at: string; last_checked: string }
  case: { filing_date: string | null; decision_date: string | null; status: string; purpose: string | null; disposition: string | null } | null
  court: string | null
  case_type: string | null
  unread_alerts: number
}

export type AlertRow = {
  alert: { id: string; kind: string; text: string; created_at: string; read: boolean }
  matter: { id: string; cnr: string; title: string }
}

export type PendencyRow = {
  name: string
  id: string
  total: number
  pending: number
  disposed: number
  pending_share: number
  mean_days_to_disposal: number | null
}
