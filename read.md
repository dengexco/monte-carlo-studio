# Monte Carlo Studio

Bu uygulama, rastgele sayılarla pi ve Euler sayısını tahmin eder. Deneyleri Go hesaplar; tarayıcı sonuçları ve grafikleri gösterir. `odev.py` yalnızca hazır Go programını başlatır.

## Çalıştırma

ZIP dosyasını tamamen çıkar. macOS Apple Silicon üzerinde `Monte Carlo.command` dosyasını aç. Terminalden çalıştırmak için:

```sh
./bin/monte-carlo-studio
```

İstersen aynı programı `python3 odev.py` ile de başlatabilirsin. Python paketi kurman gerekmez. Terminalde Ctrl+C programı kapatır. Tarayıcı sekmesini kapatmak sunucuyu durdurmaz.

Hazır dosya macOS ARM64 içindir. Başka bir sistemde Go 1.24 veya üzeriyle derle:

```sh
go build -trimpath -o bin/monte-carlo-studio .
```

Windows için çıktı adı `bin/monte-carlo-studio.exe` olmalı. Sabit adres istersen `--port 8765`, tarayıcı açılmasın istersen `--no-browser` ekle. `--no-gui` varsayılan deneyi terminalde çalıştırıp `odev_ciktilari/results.json` dosyasına kaydeder.

## Deney ayarları

Ders için n değerleri 10, 100, 1000 ve 10000; her biri için tekrar sayısı 5. İki deneyle toplam 40 tahmin oluşur. Bu, yalnızca 40 rastgele sayı kullanıldığı anlamına gelmez.

n=100 ve tekrar=5, her biri 100 denemeden oluşan beş ayrı tahmindir. Seed başlangıç numarasıdır. Aynı seed ve ayarlar aynı sonuçları üretir. Yeni bir deney için seed'i değiştirebilirsin. Her deney, n ve tekrar birleşimi ayrı bir PCG akışı kullanır.

## Pi nasıl hesaplanıyor?

Birim kareye rastgele noktalar atılır. Her noktanın x ve y koordinatı 0 dahil, 1 hariç aralıktadır. x²+y² ≤ 1 ise nokta çeyrek daireye dahildir.

Pi tahmini = 4 × içerideki nokta sayısı / n.

Örneğin 100 noktanın 79'u içerideyse tahmin 3,16 olur. Dörtle çarpmamızın nedeni, çeyrek dairenin kareye alan oranının pi/4 olmasıdır.

## Euler sayısı nasıl hesaplanıyor?

Toplam sıfırdan başlar. Rastgele sayılar toplam 1'i aşana kadar eklenir. Kaç sayı kullanıldığı kaydedilir. Bu tur n kez yapılıp sayı adetlerinin ortalaması alınır.

Örneğin 0,40 + 0,35 + 0,50 için üç sayı kullanılmıştır. Kaydedilen değer 3'tür, 1,25 değil. Toplamın tam 1 olması yetmez; bir sayı daha çekilir. Bu sayı adedinin beklenen değeri e'dir.

## Ekrandaki sonuçlar

- Mean: aynı n için tekrarların ortalaması.
- Absolute error: bu ortalamanın teorik değere uzaklığı.
- SD: tekrar sonuçlarının ne kadar yayıldığı. Hesapta tekrar sayısının bir eksiğine bölünür; güven aralığı değildir.
- Overview: tahmin, hata ve SD grafikleri.
- All results: bütün tekrarlar.
- Run log: tamamlanan tekrarların sırası.
- Docs: yöntemler, ders biçimindeki tablolar ve kullanılan kütüphaneler.

Kartlar en büyük tamamlanmış n grubunun ortalamasını gösterir. CSV tamamlanan grupları, JSON bütün durumu kaydeder. Yeni deney eski sonuçların yerini alır; saklamak istiyorsan önce indir. Stop kullanıldığında yarım grubun tamamlanan tekrarları günlükte bulunabilir, fakat grubun ortalaması tabloya eklenmez.

Grafiklerde n ekseni logaritmiktir: 10'dan 100'e geçiş ile 100'den 1000'e geçiş aynı mesafededir. Hata ve SD grafiğinin dikey ekseni de logaritmiktir; sıfır değer gösterilemez. Kamera simgesi PNG indirir, çift tıklama yakınlaştırmayı sıfırlar.

## Bu paketteki çalışma

20 Ekim 2026 tarihinde uygulama varsayılan ayarlar ve seed 20261019 ile bir kez çalıştırıldı. `results/2026-10-20` klasöründe JSON, CSV, tekrar günlüğü ve uygulamadan indirilen iki PNG var. `docs/Monte-Carlo-Report.pdf` bu kaydı kullanır; farklı çalışmalardan sonuç birleştirilmedi.

N=10000 için pi ortalaması 3,135920, e ortalaması 2,717560 oldu. Bunlar sabit hedefler değil, kayıtlı çalışmanın sonuçlarıdır. Yeni seed ile değişmeleri normaldir.

## Dosyalar

| Dosya | Görevi |
|---|---|
| `main.go` | Yerel HTTP sunucusu, API ve dışa aktarma |
| `internal/simulation/simulation.go` | Deney hesabı, doğrulama, istatistik ve iptal |
| `odev.py` | Go programını başlatma |
| `assets/app.js` | Durumu 400 ms aralıklarla sorgulama ve grafik çizme |
| `assets/index.html`, `assets/app.css` | Ekran yapısı ve görünüm |
| `frontend/components.jsx` | UI TripleD sekmeleri ve logo hareketi |
| `assets/components.js` | Tarayıcı için derlenmiş React bileşenleri |
| `docs/Proje Kapsamı.docx` | Projenin kapsamı ve yapısı |
| `docs/Kutuphaneler.md`, `licenses` | Kütüphane sürümleri ve lisanslar |
| `package-lock.json` | Ön yüz bağımlılıklarının kesin sürümleri |

Go tarafındaki `Config` ayarları, `Manager` çalışan deneyi, `State` sonuçları tutar. `Estimate` bir tahmin hesaplar; `summarize` tekrarları özetler. Hesap bir goroutine'de sürer. Mutex, ortak durum okunurken veya değiştirilirken erişimi düzenler. Stop, context üzerinden iptal sinyali verir; hesaplama düzenli aralıklarla bu sinyali kontrol eder.

Sunucu yalnızca kendi bilgisayarındaki 127.0.0.1 adresinde dinler. Başlatma ve durdurma isteklerinde oturuma özel token gerekir. Hesaplar bellektedir; veritabanı yoktur.

## Değişiklik yaptıktan sonra

Go, HTML, CSS veya app.js değiştiyse Go programını yeniden derle ve yeniden başlat. Arayüz dosyaları programın içine gömüldüğünden sadece sayfayı yenilemek yeterli değildir.

React bileşenlerini değiştirdiysen önce:

```sh
npm ci
npm run build
go build -trimpath -o bin/monte-carlo-studio .
```

Node.js yalnızca ön yüzü yeniden derlemek için gerekir. Çalışma zamanı kütüphaneleri pakette yereldir. Programı açarken npm kurulumu veya internet bağlantısı gerekmez.

## Kontrol ve sorun çözme

```sh
go test -race ./...
go vet ./...
```

Testler sınır koşullarını, tekrar üretilebilirliği, iptali, doğrulamayı ve API'yi kontrol eder. Port doluysa kendi eski uygulamanı kapat veya port belirtmeden başlat. Program bulunamıyorsa derleme yap. Tasarım eski görünüyorsa yeniden derle, eski programı durdur ve yenisini aç.

## Ders kaynağı ve kullanım

Yöntemler `I-Stochastic Processes.pdf` sayfa 62 ve 64 ile eşleşir. Tablo düzenleri sayfa 63 ve 65'e, tartışma sayfa 66'ya dayanır. PDF sayfa 61 Python ister; ayrıca paylaşılan yönerge başka dillere izin verir. Bu programın hesaplama dili Go'dur.

Proje ve belgeler AI yardımıyla hazırlanmıştır. Paylaşılan ödev yönergesindeki AI yasağı nedeniyle bu paket bağımsız öğrenci çalışması olarak sunulmamalıdır. DengeX logosunun kaynağı ve üçüncü taraf lisans bilgileri `assets/vendor/SOURCES.md` içindedir.

PDF raporunu kayıtlı verilerden yeniden üretmek için scripts/build_report.py kullanılır. Bu yardımcı betik ReportLab ve REPORT_FONT ortam değişkeninde bir Unicode TTF yazı tipi yolu gerektirir. Bunlar uygulamayı çalıştırmak için gerekli değildir.
