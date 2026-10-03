import { useEffect, useState } from 'react'
import { api, DEMO_MODE } from './api'

type State<T> = { data: T | null; error: string | null; loading: boolean }

export function useApi<T>(path: string | null, deps: unknown[] = []): State<T> & { reload: () => void } {
  // Demo mode never fetches: data stays null, so pages render their sample data immediately.
  const [state, setState] = useState<State<T>>({ data: null, error: null, loading: !!path && !DEMO_MODE })
  const [tick, setTick] = useState(0)

  useEffect(() => {
    if (!path || DEMO_MODE) return
    let cancelled = false
    setState((s) => ({ ...s, loading: true }))
    api<T>(path)
      .then((data) => !cancelled && setState({ data, error: null, loading: false }))
      .catch((e: Error) => !cancelled && setState({ data: null, error: e.message || 'Request failed', loading: false }))
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path, tick, ...deps])

  return { ...state, reload: () => setTick((t) => t + 1) }
}
