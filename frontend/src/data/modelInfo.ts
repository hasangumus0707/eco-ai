/**
 * Modelin GERÇEK eğitim ve test sonuçları.
 *
 * Kaynak dosyalar (elle uydurulmadı, oradan kopyalandı):
 *   backend/reports/mobilenet_v3_large/metrics.json
 *   backend/reports/resnet18/metrics.json
 *   dataset/stats.json
 *
 * Model yeniden eğitilirse bu değerler de güncellenmelidir.
 * Canlı doğruluk değeri ayrıca backend'in /health endpointinden okunur.
 */

export const MODEL_INFO = {
  arch: 'MobileNetV3-Large',
  parametersMillion: 4.21,
  sizeMb: 17.0,
  bestEpoch: 4,
  trainingMinutes: 5.9,
  testAccuracy: 0.9515,
  macroPrecision: 0.938,
  macroRecall: 0.9448,
  macroF1: 0.9411,
  confidenceThreshold: 0.823,
  /** Gerçek atıklardan kesin sonuç verilen oran / bunların doğruluğu */
  coverage: 0.897,
  accuracyWhenAccepted: 0.976,
  /** "Diğer" test görsellerinden yanlışlıkla atık sanılan oran */
  otherFalseAcceptRate: 0.0033,
  /** Sınıf bazında test recall (doğru bilinme oranı) */
  perClassRecall: { glass: 0.9298, metal: 0.9217, other: 0.9767, paper: 0.9725, plastic: 0.9231 },
} as const

export const DATASET_INFO = {
  name: 'Garbage Classification (12 classes)',
  source: 'https://www.kaggle.com/datasets/mostafaabla/garbage-classification',
  license: 'Veritabanı: ODbL · Görseller: © orijinal sahipleri',
  originalImages: 15515,
  usedImages: 7565,
  train: 5296,
  val: 1134,
  test: 1135,
} as const

export const MODEL_COMPARISON = [
  { arch: 'MobileNetV3-Large', accuracy: 0.9515, f1: 0.9411, sizeMb: 17.0, params: 4.21, otherFalseAccept: 0.0033, chosen: true },
  { arch: 'ResNet18', accuracy: 0.9498, f1: 0.9403, sizeMb: 44.8, params: 11.18, otherFalseAccept: 0.02, chosen: false },
] as const
