import { useCallback, useEffect, useRef, useState } from 'react'

type CameraStatus = 'idle' | 'starting' | 'active' | 'error'
export type FacingMode = 'environment' | 'user'

/**
 * Cihaz kamerasını yönetir (getUserMedia API).
 *
 * Not: Tarayıcılar kamerayı yalnızca güvenli adreslerde (https veya localhost) açar.
 * Telefonda http://192.168.x.x gibi bir adresle girilirse bu yöntem çalışmaz;
 * o durumda arayüz telefonun kendi kamera uygulamasını açan dosya seçiciye geri döner.
 */
export function useCamera() {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const [status, setStatus] = useState<CameraStatus>('idle')
  const [error, setError] = useState<string | null>(null)
  const [facingMode, setFacingMode] = useState<FacingMode>('environment')

  const isSupported = typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia && window.isSecureContext

  const stop = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop()) // kamera ışığını söndürür
    streamRef.current = null
    if (videoRef.current) videoRef.current.srcObject = null
    setStatus('idle')
  }, [])

  const start = useCallback(
    async (mode: FacingMode = facingMode) => {
      if (!isSupported) {
        setError('Bu tarayıcı veya bağlantı kamerayı desteklemiyor.')
        setStatus('error')
        return
      }
      streamRef.current?.getTracks().forEach((t) => t.stop())
      setStatus('starting')
      setError(null)
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: mode }, width: { ideal: 1280 }, height: { ideal: 960 } },
          audio: false,
        })
        streamRef.current = stream
        if (videoRef.current) {
          videoRef.current.srcObject = stream
          await videoRef.current.play()
        }
        setFacingMode(mode)
        setStatus('active')
      } catch (err) {
        const name = err instanceof DOMException ? err.name : ''
        setError(
          name === 'NotAllowedError'
            ? 'Kamera izni reddedildi. Tarayıcının adres çubuğundaki kamera simgesinden izin verebilirsiniz.'
            : name === 'NotFoundError'
              ? 'Bu cihazda kamera bulunamadı.'
              : name === 'NotReadableError'
                ? 'Kamera başka bir uygulama tarafından kullanılıyor olabilir.'
                : 'Kamera açılamadı.',
        )
        setStatus('error')
      }
    },
    [facingMode, isSupported],
  )

  const switchCamera = useCallback(() => {
    void start(facingMode === 'environment' ? 'user' : 'environment')
  }, [facingMode, start])

  /** Videodaki o anki kareyi JPEG dosyasına çevirir */
  const capture = useCallback(async (): Promise<File | null> => {
    const video = videoRef.current
    if (!video || !video.videoWidth) return null
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d')?.drawImage(video, 0, 0)
    const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.92))
    return blob ? new File([blob], `kamera-${Date.now()}.jpg`, { type: 'image/jpeg' }) : null
  }, [])

  // Bileşen ekrandan kalkınca kamerayı mutlaka kapat
  useEffect(() => stop, [stop])

  return { videoRef, status, error, facingMode, isSupported, start, stop, switchCamera, capture }
}
