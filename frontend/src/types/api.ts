/**
 * Backend API'sinin döndürdüğü verilerin TypeScript tipleri.
 * backend/app/schemas/prediction.py dosyasındaki Pydantic modelleriyle birebir eşleşir.
 */

/** Geri dönüştürülebilir 4 atık sınıfı */
export type WasteClass = 'plastic' | 'paper' | 'metal' | 'glass'

/** Modelin tahmin edebildiği tüm sınıflar ("other" = 4 sınıfın dışındaki nesneler) */
export type ModelClass = WasteClass | 'other'

/** ok: güvenilir sonuç · not_recyclable: atık gibi görünmüyor · low_confidence: model emin değil */
export type PredictionReason = 'ok' | 'not_recyclable' | 'low_confidence'

export interface PredictionResponse {
  predicted_class: ModelClass
  predicted_class_tr: string
  confidence: number
  probabilities: Record<ModelClass, number>
  is_valid_prediction: boolean
  reason: PredictionReason
  message: string
  bin_name: string | null
  bin_color: string | null
  bin_color_hex: string | null
  recycling_advice: string[]
  region_note: string
  threshold: number
}

export interface ClassInfo {
  id: WasteClass
  name_tr: string
  bin_name: string
  bin_color: string
  bin_color_hex: string
  advice: string[]
}

export interface ClassesResponse {
  classes: ClassInfo[]
  region: string
  disclaimer: string
}

export interface HealthResponse {
  status: 'ok'
  model_loaded: boolean
  model_arch: string
  model_file: string
  model_sha256: string
  device: string
  confidence_threshold: number
  test_accuracy: number
}
