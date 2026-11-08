import { ArrowRight, Brain, Camera, Recycle, ScanSearch, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'
import { CATEGORIES } from '../data/categories'
import { DATASET_INFO, MODEL_INFO } from '../data/modelInfo'
import { useHistoryStats } from '../hooks/useHistory'
import { formatPercent } from '../utils/image'

const STEPS = [
  { icon: Camera, title: 'Fotoğrafını Yükle', text: 'Atığın fotoğrafını yükleyin, sürükleyip bırakın veya kamerayla çekin.' },
  { icon: Brain, title: 'Yapay Zekâ Analiz Etsin', text: 'Kendi eğittiğimiz MobileNetV3 modeli görseli saniyenin altında inceler.' },
  { icon: Recycle, title: 'Doğru Kutuya At', text: 'Kategoriyi, güven skorunu ve hangi kutuya atılacağını öğrenin.' },
]

export function HomePage() {
  const stats = useHistoryStats()

  return (
    <>
      {/* ---------- GİRİŞ (HERO) ---------- */}
      <section className="relative overflow-hidden">
        <div aria-hidden className="pointer-events-none absolute -top-40 left-1/2 size-[640px] -translate-x-1/2 rounded-full bg-emerald-300/30 blur-3xl dark:bg-emerald-500/10" />
        <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:py-24">
          <div className="animate-fade-up text-center lg:text-left">
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white/70 px-4 py-1.5 text-sm font-medium text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300">
              <Sparkles className="size-4" /> Yapay Zekâ Destekli Geri Dönüşüm
            </span>
            <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-emerald-950 sm:text-5xl lg:text-6xl dark:text-white">
              Atığını Tanı,
              <br />
              <span className="bg-gradient-to-r from-emerald-600 to-teal-500 bg-clip-text text-transparent dark:from-emerald-400 dark:to-teal-300">
                Geleceği Koru
              </span>
            </h1>
            <p className="mt-6 text-lg text-slate-600 dark:text-slate-300">
              ECO AI, yüklediğiniz atık fotoğrafını derin öğrenme modeliyle analiz eder; atığın plastik, kâğıt, metal
              veya cam olduğunu tahmin ederek sizi doğru geri dönüşüm kutusuna yönlendirir.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3 lg:justify-start">
              <Link to="/analiz" className="btn-primary px-8 py-4 text-base">
                <ScanSearch className="size-5" /> Atığını Analiz Et
              </Link>
              <Link to="/nasil-calisir" className="btn-secondary px-8 py-4 text-base">
                Nasıl Çalışır? <ArrowRight className="size-4" />
              </Link>
            </div>
          </div>

          {/* Dekoratif görsel: 4 kategori simgesi */}
          <div className="animate-fade-up [animation-delay:150ms]">
            <div className="card mx-auto grid max-w-sm grid-cols-2 gap-4 p-6">
              {CATEGORIES.map((c) => (
                <div key={c.id} className="flex flex-col items-center gap-3 rounded-2xl bg-emerald-50/60 p-5 dark:bg-slate-800/60">
                  <span className={`grid size-14 place-items-center rounded-2xl ${c.accent}`}>
                    <c.icon className="size-7" />
                  </span>
                  <span className="font-semibold text-slate-800 dark:text-slate-100">{c.nameTr}</span>
                </div>
              ))}
              <div className="col-span-2 flex items-center justify-center gap-2 rounded-2xl bg-emerald-600 py-3 text-sm font-semibold text-white">
                <Recycle className="size-4" /> 4 kategori · 1 model
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ---------- KATEGORİLER ---------- */}
      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <SectionTitle eyebrow="Kategoriler" title="Tanıyabildiğimiz Atık Türleri" />
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {CATEGORIES.map((c) => (
            <div key={c.id} className="card p-6 transition hover:-translate-y-1 hover:shadow-lg">
              <span className={`grid size-12 place-items-center rounded-2xl ${c.accent}`}>
                <c.icon className="size-6" />
              </span>
              <h3 className="mt-4 text-lg font-bold text-slate-900 dark:text-white">{c.nameTr}</h3>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{c.description}</p>
              <div className="mt-4 flex flex-wrap gap-1.5">
                {c.examples.map((e) => (
                  <span key={e} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                    {e}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
        <p className="mt-4 text-center text-xs text-slate-400 dark:text-slate-500">
          * Bu dört kategorinin dışındaki nesneler (ör. kıyafet, yemek) için sistem kesin sonuç vermez ve kullanıcıyı uyarır.
        </p>
      </section>

      {/* ---------- NASIL ÇALIŞIR (3 ADIM) ---------- */}
      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <SectionTitle eyebrow="3 Adımda" title="Nasıl Çalışır?" />
        <div className="grid gap-5 md:grid-cols-3">
          {STEPS.map((s, i) => (
            <div key={s.title} className="card relative p-7">
              <span className="absolute top-5 right-6 text-5xl font-black text-emerald-100 dark:text-slate-800">{i + 1}</span>
              <span className="relative grid size-12 place-items-center rounded-2xl bg-emerald-600 text-white">
                <s.icon className="size-6" />
              </span>
              <h3 className="relative mt-5 text-lg font-bold text-slate-900 dark:text-white">{s.title}</h3>
              <p className="relative mt-2 text-sm text-slate-500 dark:text-slate-400">{s.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ---------- İSTATİSTİKLER (yalnızca gerçek değerler) ---------- */}
      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <div className="rounded-[2rem] bg-gradient-to-br from-emerald-700 to-emerald-900 p-8 text-white sm:p-12 dark:from-emerald-900 dark:to-slate-900">
          <div className="text-center">
            <h2 className="text-2xl font-bold sm:text-3xl">Modelimiz Rakamlarla</h2>
            <p className="mt-2 text-emerald-100/80">
              Modelin eğitimde hiç görmediği {DATASET_INFO.test.toLocaleString('tr-TR')} test görselinde ölçülen gerçek sonuçlar
            </p>
          </div>
          <div className="mt-10 grid grid-cols-2 gap-6 lg:grid-cols-4">
            <Stat value={formatPercent(MODEL_INFO.testAccuracy)} label="Test doğruluğu" />
            <Stat value={formatPercent(MODEL_INFO.macroF1)} label="Ortalama F1-skoru" />
            <Stat value={DATASET_INFO.usedImages.toLocaleString('tr-TR')} label="Eğitimde kullanılan görsel" />
            <Stat value={stats.total.toLocaleString('tr-TR')} label="Bu tarayıcıda yapılan analiz" />
          </div>
          <p className="mt-8 text-center text-xs text-emerald-100/60">
            Gerçek hayattaki fotoğraflarda (farklı ışık, arka plan, kirli atık) başarı daha düşük olabilir.
          </p>
        </div>
      </section>
    </>
  )
}

function SectionTitle({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div className="mb-10 text-center">
      <p className="text-sm font-semibold tracking-wider text-emerald-600 uppercase dark:text-emerald-400">{eyebrow}</p>
      <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-emerald-950 dark:text-white">{title}</h2>
    </div>
  )
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-2xl bg-white/10 p-5 text-center backdrop-blur">
      <p className="text-3xl font-extrabold sm:text-4xl">{value}</p>
      <p className="mt-1 text-sm text-emerald-100/80">{label}</p>
    </div>
  )
}
