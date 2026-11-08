/** Görsel dosyalarıyla ilgili yardımcı fonksiyonlar (tarayıcı tarafı) */

export const MAX_FILE_BYTES = 10 * 1024 * 1024 // backend ile aynı sınır: 10 MB
export const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'] as const
export const ACCEPT_ATTR = ACCEPTED_TYPES.join(',')

/**
 * Dosyayı sunucuya göndermeden önce hızlı ön kontrol.
 * Asıl güvenlik kontrolü backend'de yapılır; bu yalnızca kullanıcıya erken geri bildirim içindir.
 * Dönüş: hata mesajı veya sorun yoksa null
 */
export function validateImageFile(file: File): string | null {
  if (!(ACCEPTED_TYPES as readonly string[]).includes(file.type)) {
    return 'Desteklenmeyen dosya türü. Lütfen JPG, PNG veya WEBP formatında bir görsel seçin.'
  }
  if (file.size > MAX_FILE_BYTES) {
    return `Dosya çok büyük (${(file.size / 1024 / 1024).toFixed(1)} MB). En fazla 10 MB yükleyebilirsiniz.`
  }
  return null
}

/**
 * Geçmişte saklamak için küçük bir önizleme (thumbnail) üretir.
 * LocalStorage'ın ~5 MB sınırı olduğu için tam boy fotoğraf yerine ~160 px JPEG saklanır.
 */
export async function createThumbnail(file: Blob, maxSide = 160): Promise<string> {
  const bitmap = await createImageBitmap(file, { imageOrientation: 'from-image' })
  const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height))
  const canvas = document.createElement('canvas')
  canvas.width = Math.round(bitmap.width * scale)
  canvas.height = Math.round(bitmap.height * scale)
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('Canvas desteklenmiyor')
  ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height)
  bitmap.close()
  return canvas.toDataURL('image/jpeg', 0.7)
}

/** 0.9515 -> "95,2%" (Türkçe ondalık ayırıcı) */
export function formatPercent(value: number, digits = 1): string {
  return `${(value * 100).toLocaleString('tr-TR', { minimumFractionDigits: digits, maximumFractionDigits: digits })}%`
}
