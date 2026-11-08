/**
 * LocalStorage için güvenli sarmalayıcılar.
 * Gizli sekme, dolu depolama veya kapalı çerezlerde localStorage hata fırlatabilir;
 * uygulama bu durumda çökmemeli, sadece kayıt tutmadan çalışmaya devam etmelidir.
 */

export function readJSON<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    return raw ? (JSON.parse(raw) as T) : fallback
  } catch {
    return fallback
  }
}

/** Başarılıysa true, depolama dolu/kapalıysa false döner */
export function writeJSON(key: string, value: unknown): boolean {
  try {
    localStorage.setItem(key, JSON.stringify(value))
    return true
  } catch {
    return false
  }
}

export function readString(key: string): string | null {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

export function writeString(key: string, value: string): void {
  try {
    localStorage.setItem(key, value)
  } catch {
    // yok say
  }
}
