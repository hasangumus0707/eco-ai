import { Camera, LoaderCircle, SwitchCamera, X } from 'lucide-react'
import { useEffect } from 'react'
import { useCamera } from '../../hooks/useCamera'

interface Props {
  onCapture: (file: File) => void
  onClose: () => void
}

/** Tam ekran kamera penceresi: canlı görüntü + çek butonu */
export function CameraModal({ onCapture, onClose }: Props) {
  const { videoRef, status, error, start, stop, switchCamera, capture } = useCamera()

  // Pencere açılınca kamerayı başlat
  useEffect(() => {
    void start()
    // yalnızca ilk açılışta
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Esc tuşu ile kapat
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && handleClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  })

  function handleClose() {
    stop()
    onClose()
  }

  async function handleCapture() {
    const file = await capture()
    if (file) {
      stop()
      onCapture(file)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="Kamera ile fotoğraf çek"
    >
      <div className="w-full max-w-2xl overflow-hidden rounded-3xl bg-slate-900 shadow-2xl">
        <div className="flex items-center justify-between px-5 py-3 text-white">
          <p className="font-semibold">Kamerayla Fotoğraf Çek</p>
          <button onClick={handleClose} className="grid size-9 place-items-center rounded-full hover:bg-white/10" aria-label="Kapat">
            <X className="size-5" />
          </button>
        </div>

        <div className="relative aspect-[4/3] bg-black">
          <video ref={videoRef} playsInline muted className="size-full object-cover" />
          {status === 'starting' && (
            <div className="absolute inset-0 grid place-items-center text-white">
              <LoaderCircle className="size-8 animate-spin" />
            </div>
          )}
          {status === 'error' && (
            <div className="absolute inset-0 grid place-items-center p-6 text-center text-sm text-red-200">{error}</div>
          )}
        </div>

        <div className="flex items-center justify-center gap-4 px-5 py-4">
          <button
            onClick={switchCamera}
            disabled={status !== 'active'}
            className="grid size-12 place-items-center rounded-full bg-white/10 text-white transition hover:bg-white/20 disabled:opacity-40"
            aria-label="Ön/arka kamera değiştir"
            title="Kamera değiştir"
          >
            <SwitchCamera className="size-5" />
          </button>
          <button
            onClick={handleCapture}
            disabled={status !== 'active'}
            className="grid size-16 place-items-center rounded-full bg-emerald-500 text-white ring-4 ring-emerald-500/30 transition hover:bg-emerald-400 active:scale-95 disabled:opacity-40"
            aria-label="Fotoğraf çek"
          >
            <Camera className="size-7" />
          </button>
          <span className="size-12" aria-hidden />
        </div>
      </div>
    </div>
  )
}
