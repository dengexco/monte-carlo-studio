# Kullanılan kütüphaneler

| Kütüphane | Sürüm | Görev |
|---|---|---|
| react | 19.3.1 | Arayüz bileşenleri |
| react-dom | 19.3.1 | React bileşenlerini sayfaya yerleştirme |
| framer-motion | 12.43.0 | Sekme ve imza animasyonları |
| @base-ui/react | 1.9.0 | Klavye destekli sekmeler |
| esbuild | 0.25.12 | Ön yüzü tek dosyaya derleme |
| Plotly.js | 4.1.1 | Grafikler ve PNG indirme |
| UI TripleD | Kaynak uyarlaması | Native Tabs ve Native Magnetic |

Go motoru yalnızca standart kütüphane kullanır. Python başlatıcı yalnızca os, sys ve pathlib kullanır. React ve diğer çalışma zamanı bağımlılıkları assets/components.js içinde paketlidir. Plotly assets/vendor/plotly.min.js içindedir. Çalıştırmak için npm kurulumu veya internet gerekmez. Yeniden ön yüz derlemek için npm ci gerekir; node_modules pakete dahil edilmez. Kesin bağımlılık ağacı package-lock.json içindedir. Lisanslar licenses ve assets/vendor klasörlerinde korunur. DengeX logosu bir marka varlığıdır; açık kaynak kütüphane lisansı kapsamında değildir.
