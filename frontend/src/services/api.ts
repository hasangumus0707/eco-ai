/**
 * Backend ile konuşan tek yer.
 *
 * Bütün HTTP istekleri buradan geçer; böylece hata yönetimi, zaman aşımı ve
 * adres ayarı tek bir dosyada toplanır. Bileşenler fetch() ile doğrudan uğraşmaz.
 */

import type { ClassesResponse, HealthResponse, PredictionResponse } from '../types/api'

/** Backend adresi: .env dosyasında VITE_API_URL ile değiştirilebilir */
export const API_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '')

const DEFAULT_TIMEOUT_MS = 30_000

/** Kullanıcıya gösterilebilecek, anlaşılır mesaj taşıyan hata */
export class ApiError extends Error {
  /** HTTP durum kodu; sunucuya hiç ulaşılamadıysa null */
  readonly status: number | null

  constructor(message: string, status: number | null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

/** FastAPI hata gövdesi: {"detail": "..."} */
function hasStringDetail(body: unknown): body is { detail: string } {
  return typeof body === 'object' && body !== null && typeof (body as { detail?: unknown }).detail === 'string'
}

async function request<T>(path: string, init?: RequestInit, timeoutMs = DEFAULT_TIMEOUT_MS): Promise<T> {
  // AbortController: belirli süre içinde yanıt gelmezse isteği iptal etmemizi sağlar
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)

  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, { ...init, signal: controller.signal })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('Sunucu zamanında yanıt vermedi. Lütfen tekrar deneyin.', null)
    }
    // fetch yalnızca ağ hatasında (sunucu kapalı, yanlış adres) exception fırlatır
    throw new ApiError(
      `Yapay zekâ sunucusuna bağlanılamadı. Backend'in çalıştığından emin olun (${API_URL}).`,
      null,
    )
  } finally {
    clearTimeout(timer)
  }

  if (!response.ok) {
    let message = `Sunucu bir hata döndürdü (kod ${response.status}).`
    try {
      const body: unknown = await response.json()
      if (hasStringDetail(body)) message = body.detail
    } catch {
      // gövde JSON değilse varsayılan mesaj kalır
    }
    throw new ApiError(message, response.status)
  }

  return (await response.json()) as T
}

export const api = {
  /** Görseli yapay zekâ modeline gönderir */
  predict(file: File): Promise<PredictionResponse> {
    const form = new FormData()
    form.append('file', file)
    return request<PredictionResponse>('/predict', { method: 'POST', body: form })
  },

  health(): Promise<HealthResponse> {
    return request<HealthResponse>('/health', undefined, 5_000)
  },

  classes(): Promise<ClassesResponse> {
    return request<ClassesResponse>('/classes', undefined, 5_000)
  },
}

/** Herhangi bir hatayı kullanıcıya gösterilecek metne çevirir */
export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message
  return 'Beklenmeyen bir hata oluştu. Lütfen sayfayı yenileyip tekrar deneyin.'
}
