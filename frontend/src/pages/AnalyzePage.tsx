import { useEffect, useState } from 'react'
import { BackendStatus } from '../components/analyze/BackendStatus'
import { CameraModal } from '../components/analyze/CameraModal'
import { ImagePreview } from '../components/analyze/ImagePreview'
import { ResultPanel } from '../components/analyze/ResultPanel'
import { UploadZone } from '../components/analyze/UploadZone'
import { ErrorAlert } from '../components/ui/ErrorAlert'
import { PageHeader } from '../components/ui/PageHeader'
import { useCamera } from '../hooks/useCamera'
import { api, errorMessage } from '../services/api'
import { historyStore } from '../services/historyStore'
import type { PredictionResponse } from '../types/api'
import { createThumbnail, validateImageFile } from '../utils/image'

/**
 * Sayfanın durumları (state machine):
 *   idle      -> henüz fotoğraf yok
 *   selected  -> fotoğraf seçildi, önizleme gösteriliyor
 *   analyzing -> backend'e gönderildi, yanıt bekleniyor
 *   result    -> sonuç geldi
 * Tek bir "phase" alanı kullanmak, "hem yükleniyor hem sonuç var" gibi imkânsız durumları engeller.
 */
type Phase =
  | { phase: 'idle' }
  | { phase: 'selected'; file: File; url: string }
  | { phase: 'analyzing'; file: File; url: string }
  | { phase: 'result'; file: File; url: string; result: PredictionResponse }

export function AnalyzePage() {
  const [state, setState] = useState<Phase>({ phase: 'idle' })
  const [error, setError] = useState<string | null>(null)
  const [cameraOpen, setCameraOpen] = useState(false)
  const { isSupported: cameraSupported } = useCamera()

  const imageUrl = state.phase === 'idle' ? null : state.url

  // Önizleme adresi (blob URL) artık kullanılmadığında belleği serbest bırak
  useEffect(() => {
    return () => {
      if (imageUrl) URL.revokeObjectURL(imageUrl)
    }
  }, [imageUrl])

  function selectFile(file: File) {
    const problem = validateImageFile(file)
    if (problem) {
      setError(problem)
      return
    }
    setError(null)
    setState({ phase: 'selected', file, url: URL.createObjectURL(file) })
  }

  function reset() {
    setError(null)
    setState({ phase: 'idle' })
  }

  async function analyze() {
    if (state.phase !== 'selected') return
    const { file, url } = state
    setError(null)
    setState({ phase: 'analyzing', file, url })
    try {
      const result = await api.predict(file)
      setState({ phase: 'result', file, url, result })
      // Geçmişe kaydet (önizleme üretilemezse kayıt yine de yapılır)
      const thumbnail = await createThumbnail(file).catch(() => null)
      historyStore.add(result, thumbnail)
    } catch (err) {
      setError(errorMessage(err))
      setState({ phase: 'selected', file, url }) // fotoğraf kaybolmasın, tekrar denenebilsin
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 pb-8 sm:px-6">
      <PageHeader
        eyebrow="Atık Analizi"
        title="Atığını Yapay Zekâ ile Tanı"
        description="Bir fotoğraf yükleyin veya kamerayla çekin; model atığın plastik, kâğıt, metal ya da cam olup olmadığını tahmin etsin."
      />

      <div className="mb-6 flex justify-center">
        <BackendStatus />
      </div>

      {error && (
        <div className="mx-auto mb-6 max-w-2xl">
          <ErrorAlert message={error} onRetry={state.phase === 'selected' ? analyze : undefined} />
        </div>
      )}

      <div className="mx-auto max-w-2xl lg:max-w-none">
        {state.phase === 'idle' && (
          <div className="mx-auto max-w-2xl animate-fade-up">
            <UploadZone onFile={selectFile} onOpenCamera={() => setCameraOpen(true)} cameraSupported={cameraSupported} />
          </div>
        )}

        {(state.phase === 'selected' || state.phase === 'analyzing') && (
          <div className="mx-auto max-w-2xl animate-fade-up">
            <ImagePreview
              src={state.url}
              fileName={state.file.name}
              analyzing={state.phase === 'analyzing'}
              onRemove={reset}
              onAnalyze={analyze}
            />
          </div>
        )}

        {state.phase === 'result' && <ResultPanel result={state.result} imageSrc={state.url} onReset={reset} />}
      </div>

      {cameraOpen && (
        <CameraModal
          onClose={() => setCameraOpen(false)}
          onCapture={(file) => {
            setCameraOpen(false)
            selectFile(file)
          }}
        />
      )}
    </div>
  )
}
