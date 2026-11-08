import { Code, Cpu, Database, Globe, Leaf, Server, Target } from 'lucide-react'
import type { ReactNode } from 'react'
import { PageHeader } from '../components/ui/PageHeader'
import { CATEGORIES, CLASS_LABEL_TR } from '../data/categories'
import { DATASET_INFO, MODEL_COMPARISON, MODEL_INFO } from '../data/modelInfo'
import { formatPercent } from '../utils/image'

const TECH = [
  { group: 'Yapay Zekâ', icon: Cpu, items: ['PyTorch', 'Torchvision', 'MobileNetV3-Large', 'Transfer Learning', 'scikit-learn (metrikler)'] },
  { group: 'Backend', icon: Server, items: ['Python 3.12', 'FastAPI', 'Uvicorn', 'Pillow'] },
  { group: 'Frontend', icon: Code, items: ['React', 'TypeScript', 'Vite', 'Tailwind CSS', 'Recharts', 'Lucide Icons'] },
  { group: 'Veri', icon: Database, items: ['Kaggle Garbage Classification', 'LocalStorage (analiz geçmişi)'] },
]

const BENEFITS = [
  'Atıkların kaynağında doğru ayrıştırılmasını kolaylaştırarak geri dönüşüm tesislerine giden atığın kalitesini artırmaya yardımcı olur.',
  'Yanlış kutuya atılan atıkların neden olduğu “kirlenmeyi” azaltma potansiyeli taşır.',
  'Kullanıcılara her analizde ayrıştırma ipuçları vererek geri dönüşüm bilincini artırır.',
  'Tamamen yerel çalışır: fotoğraflar üçüncü taraf bir servise gönderilmez ve ücretli bir API gerekmez.',
]

export function AboutPage() {
  return (
    <div className="mx-auto max-w-5xl px-4 pb-8 sm:px-6">
      <PageHeader
        eyebrow="Proje Hakkında"
        title="ECO AI – Akıllı Geri Dönüşüm Asistanı"
        description="Yapay Zekâ dersi kapsamında geliştirilen, gerçek bir derin öğrenme modeli kullanan dönem projesi."
      />

      <div className="space-y-6">
        <Block icon={<Target className="size-6" />} title="Projenin Amacı">
          <p>
            Pek çok kişi, bir atığın hangi geri dönüşüm kutusuna atılması gerektiğinden emin değildir. Yanlış kutuya atılan
            atıklar geri dönüşüm sürecini zorlaştırır. ECO AI, kullanıcının yüklediği bir atık fotoğrafını kendi eğittiğimiz
            görüntü sınıflandırma modeliyle analiz ederek atığın kategorisini tahmin eder ve doğru kutuya yönlendirir.
          </p>
        </Block>

        <Block icon={<Cpu className="size-6" />} title="Yapay Zekâ Algoritması">
          <p>
            ImageNet üzerinde önceden eğitilmiş <strong>MobileNetV3-Large</strong> evrişimli sinir ağı, transfer learning
            ile 5 sınıfa (4 atık kategorisi + “diğer”) uyarlandı. İki farklı mimari aynı veriyle eğitilip test kümesinde
            karşılaştırıldı:
          </p>
          <div className="overflow-x-auto">
            <table className="mt-2 w-full min-w-[520px] text-left text-sm">
              <thead>
                <tr className="border-b border-emerald-100 text-slate-500 dark:border-slate-800 dark:text-slate-400">
                  <th className="py-2 pr-4 font-medium">Model</th>
                  <th className="py-2 pr-4 font-medium">Test doğruluğu</th>
                  <th className="py-2 pr-4 font-medium">F1-skoru</th>
                  <th className="py-2 pr-4 font-medium">“Diğer”i atık sanma</th>
                  <th className="py-2 pr-4 font-medium">Boyut</th>
                </tr>
              </thead>
              <tbody>
                {MODEL_COMPARISON.map((m) => (
                  <tr key={m.arch} className="border-b border-emerald-50 last:border-0 dark:border-slate-800">
                    <td className="py-2.5 pr-4 font-semibold text-slate-900 dark:text-white">
                      {m.arch}
                      {m.chosen && (
                        <span className="ml-2 rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300">
                          seçildi
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 pr-4">{formatPercent(m.accuracy, 2)}</td>
                    <td className="py-2.5 pr-4">{formatPercent(m.f1, 2)}</td>
                    <td className="py-2.5 pr-4">{formatPercent(m.otherFalseAccept)}</td>
                    <td className="py-2.5 pr-4">{m.sizeMb.toLocaleString('tr-TR')} MB</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-sm">
            Sınıf bazında doğru bilinme oranları (recall):{' '}
            {Object.entries(MODEL_INFO.perClassRecall)
              .map(([cls, v]) => `${CLASS_LABEL_TR[cls as keyof typeof CLASS_LABEL_TR]} ${formatPercent(v)}`)
              .join(' · ')}
          </p>
        </Block>

        <Block icon={<Leaf className="size-6" />} title="Desteklenen Kategoriler">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {CATEGORIES.map((c) => (
              <div key={c.id} className="flex items-center gap-3 rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/60">
                <span className={`grid size-10 place-items-center rounded-xl ${c.accent}`}>
                  <c.icon className="size-5" />
                </span>
                <span>
                  <span className="block font-semibold text-slate-900 dark:text-white">{c.nameTr}</span>
                  <span className="text-xs text-slate-500 dark:text-slate-400">{c.nameEn}</span>
                </span>
              </div>
            ))}
          </div>
          <p className="text-sm">
            Önerilen kutu renkleri Sıfır Atık Yönetmeliği'ndeki öneriye göre ayarlanmıştır; belediyeden belediyeye
            farklılık gösterebileceği için bir yapılandırma dosyasından değiştirilebilir.
          </p>
        </Block>

        <Block icon={<Code className="size-6" />} title="Kullanılan Teknolojiler">
          <div className="grid gap-4 sm:grid-cols-2">
            {TECH.map((t) => (
              <div key={t.group} className="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/60">
                <p className="flex items-center gap-2 font-semibold text-slate-900 dark:text-white">
                  <t.icon className="size-4 text-emerald-600 dark:text-emerald-400" /> {t.group}
                </p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {t.items.map((i) => (
                    <span key={i} className="rounded-full bg-white px-2.5 py-1 text-xs text-slate-600 ring-1 ring-emerald-100 dark:bg-slate-900 dark:text-slate-300 dark:ring-slate-700">
                      {i}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Block>

        <Block icon={<Database className="size-6" />} title="Veri Seti">
          <p>
            <strong>{DATASET_INFO.name}</strong> –{' '}
            <a href={DATASET_INFO.source} target="_blank" rel="noreferrer" className="font-medium text-emerald-700 underline-offset-2 hover:underline dark:text-emerald-400">
              Kaggle
            </a>
            . Lisans: {DATASET_INFO.license}. Orijinal {DATASET_INFO.originalImages.toLocaleString('tr-TR')} görselden
            kopyalar ve çelişkili etiketler temizlenip sınıflar dengelendikten sonra{' '}
            {DATASET_INFO.usedImages.toLocaleString('tr-TR')} görsel kullanıldı.
          </p>
        </Block>

        <Block icon={<Globe className="size-6" />} title="Çevreye Olası Faydaları">
          <ul className="space-y-2">
            {BENEFITS.map((b) => (
              <li key={b} className="flex gap-2">
                <Leaf className="mt-1 size-4 shrink-0 text-emerald-500" />
                {b}
              </li>
            ))}
          </ul>
        </Block>
      </div>
    </div>
  )
}

function Block({ icon, title, children }: { icon: ReactNode; title: string; children: ReactNode }) {
  return (
    <section className="card p-6 sm:p-8">
      <div className="flex items-center gap-3">
        <span className="grid size-11 place-items-center rounded-2xl bg-emerald-600 text-white">{icon}</span>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">{title}</h2>
      </div>
      <div className="mt-4 space-y-3 leading-relaxed text-slate-600 dark:text-slate-300">{children}</div>
    </section>
  )
}
