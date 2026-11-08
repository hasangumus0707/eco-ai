import { useCallback, useEffect, useState } from 'react'
import { api, errorMessage } from '../services/api'
import type { HealthResponse } from '../types/api'

type HealthState =
  | { status: 'checking' }
  | { status: 'online'; data: HealthResponse }
  | { status: 'offline'; error: string }

/** Backend'in ve modelin çalışıp çalışmadığını kontrol eder. */
export function useBackendHealth(): HealthState & { retry: () => void } {
  const [state, setState] = useState<HealthState>({ status: 'checking' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let cancelled = false // bileşen kapandıysa state güncelleme
    api
      .health()
      .then((data) => !cancelled && setState({ status: 'online', data }))
      .catch((err: unknown) => !cancelled && setState({ status: 'offline', error: errorMessage(err) }))
    return () => {
      cancelled = true
    }
  }, [attempt])

  const retry = useCallback(() => {
    setState({ status: 'checking' })
    setAttempt((a) => a + 1)
  }, [])

  return { ...state, retry }
}
