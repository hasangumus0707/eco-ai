import { useMemo, useSyncExternalStore } from 'react'
import { CLASS_ORDER } from '../data/categories'
import { historyStore, type HistoryEntry } from '../services/historyStore'
import type { ModelClass } from '../types/api'

/** Analiz geçmişini okur; geçmiş değiştiğinde bileşen otomatik yeniden çizilir. */
export function useHistory(): HistoryEntry[] {
  return useSyncExternalStore(historyStore.subscribe, historyStore.getSnapshot)
}

export interface HistoryStats {
  total: number
  today: number
  valid: number
  /** Yalnızca güvenilir (geçerli) sonuçların kategori dağılımı */
  byClass: Record<ModelClass, number>
  uncertain: number
}

function isToday(iso: string): boolean {
  const d = new Date(iso)
  const now = new Date()
  return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate()
}

/** Geçmişten istatistik hesaplar (günlük sayaç, kategori dağılımı) */
export function useHistoryStats(): HistoryStats {
  const history = useHistory()
  return useMemo(() => {
    const byClass = Object.fromEntries(CLASS_ORDER.map((c) => [c, 0])) as Record<ModelClass, number>
    let valid = 0
    let today = 0
    for (const e of history) {
      if (e.isValid) {
        valid++
        byClass[e.predictedClass]++
      }
      if (isToday(e.createdAt)) today++
    }
    return { total: history.length, today, valid, byClass, uncertain: history.length - valid }
  }, [history])
}
