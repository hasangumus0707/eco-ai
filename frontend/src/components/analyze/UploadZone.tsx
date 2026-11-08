import { Camera, ImagePlus, Upload } from 'lucide-react'
import { useRef, useState, type DragEvent } from 'react'
import { ACCEPT_ATTR } from '../../utils/image'

interface Props {
  onFile: (file: File) => void
  onOpenCamera: () => void
  /** Tarayıcı içi kamera (getUserMedia) kullanılabilir mi? */
  cameraSupported: boolean
}

/** Sürükle-bırak + dosya seçme + kamera butonları */
export function UploadZone({ onFile, onOpenCamera, cameraSupported }: Props) {
  const fileInput = useRef<HTMLInputElement>(null)
  const nativeCameraInput = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) onFile(file)
  }

  function handleFiles(files: FileList | null) {
    const file = files?.[0]
    if (file) onFile(file)
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={`flex flex-col items-center justify-center gap-5 rounded-3xl border-2 border-dashed px-6 py-14 text-center transition ${
        dragging
          ? 'scale-[1.01] border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10'
          : 'border-emerald-200 bg-white dark:border-slate-700 dark:bg-slate-900'
      }`}
    >
      <span className="grid size-16 place-items-center rounded-2xl bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300">
        <ImagePlus className="size-8" />
      </span>
      <div>
        <p className="text-lg font-semibold text-slate-900 dark:text-white">
          {dragging ? 'Bırakın, yükleyelim!' : 'Atık fotoğrafını buraya sürükleyin'}
        </p>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">JPG, PNG veya WEBP · en fazla 10 MB</p>
      </div>

      <div className="flex flex-wrap justify-center gap-3">
        <button type="button" className="btn-primary" onClick={() => fileInput.current?.click()}>
          <Upload className="size-4" /> Fotoğraf Seç
        </button>
        <button
          type="button"
          className="btn-secondary"
          // Tarayıcı kamerası yoksa (ör. telefonda http bağlantısı) cihazın kendi kamera uygulamasını aç
          onClick={() => (cameraSupported ? onOpenCamera() : nativeCameraInput.current?.click())}
        >
          <Camera className="size-4" /> Kamerayla Çek
        </button>
      </div>

      <input
        ref={fileInput}
        type="file"
        accept={ACCEPT_ATTR}
        className="hidden"
        onChange={(e) => {
          handleFiles(e.target.files)
          e.target.value = '' // aynı dosya tekrar seçilebilsin
        }}
      />
      <input
        ref={nativeCameraInput}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={(e) => {
          handleFiles(e.target.files)
          e.target.value = ''
        }}
      />
      <p className="text-xs text-slate-400 dark:text-slate-500">
        İpucu: En iyi sonuç için tek bir atığı sade bir zeminde, yakından ve iyi ışıkta çekin.
      </p>
    </div>
  )
}
