/**
 * Analiz geçmişi deposu (LocalStorage).
 *
 * Yalnızca bu tarayıcıda GERÇEKTEN yapılmış analizler kaydedilir; hiçbir sahte kayıt yoktur.
 * Birden fazla bileşen (Ana Sayfa istatistikleri, Geçmiş sayfası) aynı veriyi kullandığı için
 * basit bir "abone ol / bildir" deposu yazdık; React'in useSyncExternalStore kancası ile bağlanır.
 */

import type { ModelClass, PredictionReason, PredictionResponse } from '../types/api'
import { readJSON, writeJSON } from '../utils/storage'

const STORAGE_KEY = 'eco-ai-history-v1'
const MAX_ENTRIES = 50

export interface HistoryEntry {
  id: string
  createdAt: string // ISO tarih
  thumbnail: string | null // küçük JPEG (data URL)
  predictedClass: ModelClass
  predictedClassTr: string
  confidence: number
  isValid: boolean
  reason: PredictionReason
  probabilities: Record<ModelClass, number>
  binName: string | null
  binColorHex: string | null
}

type Listener = () => void

let entries: HistoryEntry[] = readJSON<HistoryEntry[]>(STORAGE_KEY, [])
const listeners = new Set<Listener>()

function persist(next: HistoryEntry[]): void {
  entries = next
  // Depolama doluysa önce önizlemesiz kaydetmeyi dene, o da olmazsa yalnızca bellekte tut.
  if (!writeJSON(STORAGE_KEY, next)) {
    writeJSON(STORAGE_KEY, next.map((e) => ({ ...e, thumbnail: null })))
  }
  listeners.forEach((l) => l())
}

export const historyStore = {
  subscribe(listener: Listener): () => void {
    listeners.add(listener)
    return () => listeners.delete(listener)
  },

  getSnapshot(): HistoryEntry[] {
    return entries
  },

  add(result: PredictionResponse, thumbnail: string | null): HistoryEntry {
    const entry: HistoryEntry = {
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
      thumbnail,
      predictedClass: result.predicted_class,
      predictedClassTr: result.predicted_class_tr,
      confidence: result.confidence,
      isValid: result.is_valid_prediction,
      reason: result.reason,
      probabilities: result.probabilities,
      binName: result.bin_name,
      binColorHex: result.bin_color_hex,
    }
    persist([entry, ...entries].slice(0, MAX_ENTRIES))
    return entry
  },

  remove(id: string): void {
    persist(entries.filter((e) => e.id !== id))
  },

  clear(): void {
    persist([])
  },
}
