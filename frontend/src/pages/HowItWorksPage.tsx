import { ArrowRight, Brain, Gauge, Grid3x3, Layers, ScanSearch, ShieldCheck } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { PageHeader } from '../components/ui/PageHeader'
import { DATASET_INFO, MODEL_INFO } from '../data/modelInfo'
import { formatPercent } from '../utils/image'

const PIPELINE = ['Fotoğraf', '224×224 boyutlandırma', 'Normalizasyon', 'MobileNetV3', 'Olasılıklar', 'Karar kuralı']

export function HowItWorksPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 pb-8 sm:px-6">
      <PageHeader
        eyebrow="Nasıl Çalışır?"
        title="Yapay Zekâ Bir Fotoğrafı Nasıl Tanır?"
        description="ECO AI'ın arkasındaki teknolojiyi adım adım, teknik bilgi gerektirmeden anlatıyoruz."
      />

      {/* İşlem hattı */}
      <div className="card mb-8 p-6">
        <p className="mb-4 text-center text-sm font-semibold text-slate-500 dark:text-slate-400">Bir fotoğrafın yolculuğu</p>
        <div className="flex flex-wrap items-center justify-center gap-2">
          {PIPELINE.map((step, i) => (
            <span key={step} className="flex items-center gap-2">
              <span className="rounded-full bg-emerald-50 px-3 py-1.5 text-sm font-medium text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-300">
                {step}
              </span>
              {i < PIPELINE.length - 1 && <ArrowRight className="size-4 text-emerald-400" />}
            </span>
          ))}
        </div>
      </div>

      <div className="space-y-6">
        <Section icon={<Grid3x3 className="size-6" />} title="Görüntü işleme nedir?">
          <p>
            Bilgisayar için bir fotoğraf, binlerce küçük noktadan (piksel) oluşan bir sayı tablosudur. Her pikselin
            kırmızı, yeşil ve mavi (RGB) olmak üzere üç renk değeri vardır. Görüntü işleme, bu sayılar üzerinde
            hesaplamalar yaparak görselden anlamlı bilgi çıkarmaktır.
          </p>
          <p>
            Modelimize gönderilen her fotoğraf önce <strong>224×224 piksel</strong> boyutuna getirilir ve renk değerleri{' '}
            <strong>normalize edilir</strong>; yani modelin eğitimde alıştığı sayı aralığına ölçeklenir.
          </p>
        </Section>

        <Section icon={<Brain className="size-6" />} title="Yapay zekâ görüntüyü nasıl tanır?">
          <p>
            Kullandığımız yöntem <strong>evrişimli sinir ağı</strong> (Convolutional Neural Network, CNN) olarak
            adlandırılır. Ağ, görseli katman katman inceler:
          </p>
          <ul className="list-inside list-disc space-y-1">
            <li>İlk katmanlar <strong>kenar ve renk geçişlerini</strong> fark eder.</li>
            <li>Orta katmanlar bunları birleştirip <strong>doku ve şekilleri</strong> (parlaklık, kıvrım, etiket) tanır.</li>
            <li>Son katmanlar <strong>bütün nesneyi</strong> anlar: “bu bir şişe”, “bu bir kutu”.</li>
          </ul>
          <p>
            En sonda model, her kategori için bir olasılık hesaplar. Örneğin: Plastik %91, Cam %6, Metal %2…
          </p>
        </Section>

        <Section icon={<Layers className="size-6" />} title="Transfer Learning nedir?">
          <p>
            Sıfırdan bir görüntü modeli eğitmek milyonlarca görsel ve günlerce süren hesaplama gerektirir. Bunun yerine,{' '}
            <strong>ImageNet</strong> adlı 1,2 milyon görsellik veri setiyle önceden eğitilmiş bir model aldık. Bu model
            kenar, doku ve şekil gibi genel görsel bilgileri zaten öğrenmiş durumda.
          </p>
          <p>
            Biz yalnızca modelin son katmanını kendi kategorilerimize göre değiştirdik ve tüm ağı kendi atık
            görsellerimizle kısa bir süre <strong>ince ayardan</strong> (fine-tuning) geçirdik. Bu sayede{' '}
            {DATASET_INFO.usedImages.toLocaleString('tr-TR')} görselle ve bir dizüstü bilgisayarda yalnızca{' '}
            {MODEL_INFO.trainingMinutes.toLocaleString('tr-TR')} dakikalık eğitimle yüksek başarı elde edebildik.
          </p>
          <p className="rounded-xl bg-emerald-50 p-3 text-sm dark:bg-emerald-500/10">
            💡 Benzetme: Bisiklet sürmeyi bilen birinin motosiklet kullanmayı öğrenmesi, hiç bilmeyen birine göre çok daha
            hızlıdır. Model de “görmeyi” zaten bildiği için yalnızca “atıkları ayırt etmeyi” öğrendi.
          </p>
        </Section>

        <Section icon={<ScanSearch className="size-6" />} title="Model nasıl eğitildi?">
          <ul className="space-y-2">
            <li>
              <strong>Veri:</strong> Kaggle “Garbage Classification” veri seti. 12 orijinal sınıf, bizim 4 kategorimize
              ve bir “diğer” sınıfına dönüştürüldü (ör. karton → kâğıt, üç cam rengi → cam).
            </li>
            <li>
              <strong>Bölme:</strong> {DATASET_INFO.train.toLocaleString('tr-TR')} eğitim,{' '}
              {DATASET_INFO.val.toLocaleString('tr-TR')} doğrulama, {DATASET_INFO.test.toLocaleString('tr-TR')} test görseli.
              Test görselleri eğitim boyunca modele hiç gösterilmedi.
            </li>
            <li>
              <strong>Veri çoğaltma:</strong> Eğitim görselleri her turda rastgele kırpıldı, çevrildi, döndürüldü ve ışığı
              değiştirildi. Böylece model ezberlemek yerine genellemeyi öğrendi.
            </li>
            <li>
              <strong>Aşırı öğrenmeye karşı:</strong> Dropout, weight decay ve <em>early stopping</em> kullanıldı. Doğrulama
              başarısı iyileşmeyi bıraktığında eğitim otomatik durdu; en iyi sonuç {MODEL_INFO.bestEpoch}. turda alındı.
            </li>
            <li>
              <strong>Karşılaştırma:</strong> MobileNetV3 ve ResNet18 aynı veriyle eğitildi. MobileNetV3; benzer doğrulukta,
              2,6 kat daha küçük ve atık olmayan nesneleri ayırt etmede daha başarılı olduğu için seçildi.
            </li>
            <li>
              <strong>Sonuç:</strong> Test doğruluğu <strong>{formatPercent(MODEL_INFO.testAccuracy)}</strong>, ortalama
              F1-skoru <strong>{formatPercent(MODEL_INFO.macroF1)}</strong>.
            </li>
          </ul>
        </Section>

        <Section icon={<Gauge className="size-6" />} title="Tahmin güven skoru ne anlama gelir?">
          <p>
            Güven skoru, modelin tahmin ettiği kategoriye verdiği olasılıktır. %95 güven, modelin “büyük ihtimalle bu
            kategori” dediği anlamına gelir. <strong>Ancak bu bir garanti değildir:</strong> model, eğitimde hiç görmediği
            bir nesne için bile yüksek güven verebilir.
          </p>
          <p>Bu yüzden ECO AI iki ek güvenlik katmanı kullanır:</p>
          <ul className="list-inside list-disc space-y-1">
            <li>
              <strong>“Diğer” sınıfı:</strong> Model kıyafet, ayakkabı, yemek, pil gibi nesnelerle eğitilerek “bu dört
              kategoriden biri değil” demeyi öğrendi.
            </li>
            <li>
              <strong>Güven eşiği ({formatPercent(MODEL_INFO.confidenceThreshold)}):</strong> Bu değerin altındaki tahminlerde
              kesin sonuç gösterilmez. Eşik, doğrulama verisinden otomatik olarak hesaplandı.
            </li>
          </ul>
        </Section>

        <Section icon={<ShieldCheck className="size-6" />} title="Bilinen sınırlamalar">
          <ul className="list-inside list-disc space-y-1">
            <li>Eğitim görselleri çoğunlukla internetten toplanmış, sade arka planlı fotoğraflardır. Evde çekilmiş, karışık arka planlı fotoğraflarda başarı düşebilir.</li>
            <li>İnsan, araba, hayvan gibi nesneler eğitimde hiç kullanılmadı; bunlar için “diğer” kontrolü her zaman çalışmayabilir.</li>
            <li>Örnek: Test sırasında küflü bir ekmek dilimi, rengi ve dokusu kartona benzediği için yüksek güvenle “kâğıt” sanıldı.</li>
            <li>Fotoğrafta birden fazla atık varsa model yalnızca tek bir kategori döndürür.</li>
          </ul>
        </Section>
      </div>

      <div className="mt-10 text-center">
        <Link to="/analiz" className="btn-primary">
          <ScanSearch className="size-4" /> Şimdi Dene
        </Link>
      </div>
    </div>
  )
}

function Section({ icon, title, children }: { icon: ReactNode; title: string; children: ReactNode }) {
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
