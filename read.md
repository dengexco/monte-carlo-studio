# Monte Carlo Studio — Go sürümü

Bu proje AI yardımıyla geliştirilmiş bir simülasyon uygulamasıdır. Hesaplama, HTTP sunucusu, doğrulama ve dışa aktarma Go ile yapılır. Python yalnızca derlenmiş programı başlatan isteğe bağlı bir dosyadır. Arayüz HTML/CSS/JavaScript ve yerel Plotly dosyasından oluşur.

## Çalıştırma ve derleme

Bu bilgisayar için derlenmiş macOS ARM64 programı `bin/monte-carlo-studio` konumundadır. `Monte Carlo.command` dosyasına çift tıklamak doğrudan Go programını açar. Python üzerinden başlatmak için:

```sh
python3 odev.py
```

Python paketi veya sanal ortam gerekmez. Python bir sunucu açmaz, hesaplama yapmaz, Go derlemez; `os.execv` ile kendi sürecini Go programına devreder. `--port`, `--no-browser` ve `--no-gui` seçeneklerini olduğu gibi aktarır. Dosya bulunamazsa derleme komutunu gösterir.

Kaynak koddan derlemek için Go 1.24 veya üzeri gerekir:

```sh
go build -trimpath -o bin/monte-carlo-studio .
./bin/monte-carlo-studio
```

Windows'ta çıktı adı `bin/monte-carlo-studio.exe` olmalıdır. Derleme işletim sistemine ve işlemci mimarisine özeldir. Git deposuna derlenmiş program veya `.venv` gönderilmez. Kaynak veya arayüz değişirse yeniden derleyip programı yeniden başlatmalısın.

```sh
python3 odev.py --port 8765
python3 odev.py --no-browser
python3 odev.py --no-gui
```

Normal başlatmada uygun bir yerel port seçilir, adres terminale yazdırılır ve tarayıcı açılır. Sayfa açılınca varsayılan 40 tekrar otomatik başlar. `--no-browser` tarayıcıyı açmaz. `--no-gui` 40 tekrarı terminale yazdırır ve `odev_ciktilari/results.json` dosyasına kaydeder; bu mod eski Python sürümünün PNG dosyalarını üretmez. Grafikler web arayüzündeki kamera simgesinden kaydedilir. Ctrl+C uygulamayı kapatır. Tarayıcı sekmesini kapatmak sunucuyu kapatmaz.

## Dosyalar ve sorumlulukları

| Dosya | Görevi |
| --- | --- |
| `main.go` | Gömülü arayüz, HTTP API, indirmeler, port, tarayıcı açma ve kapanış |
| `internal/simulation/simulation.go` | π/e algoritmaları, ayarlar, durum yönetimi, istatistikler ve iptal |
| `odev.py` | Yalnızca Go programını başlatma |
| `assets/index.html` | Form, sonuç alanları, tablolar ve imza |
| `assets/app.js` | API çağrıları, 400 ms durum sorgulama ve Plotly grafikleri |
| `assets/app.css` | Uygulamaya özel görünüm |
| `assets/vendor/` | DengeX CSS, Plotly ve kaynak bilgileri |
| `main_test.go` | HTTP erişimi, doğrulama ve dışa aktarma testleri |
| `internal/simulation/simulation_test.go` | Algoritma, tekrar üretilebilirlik, iptal ve istatistik testleri |

Go `embed` ile arayüz dosyaları derleme sırasında programın içine alınır. Böylece derlenmiş program çalışma klasöründeki CSS/JS dosyalarına bağımlı değildir. DengeX dosyalarının kaynakları `assets/vendor/SOURCES.md` içinde kayıtlıdır.

## Kullanıcı kontrolleri

- Sample sizes: virgülle ayrılmış 1–8 örneklem büyüklüğü; her biri 1–1.000.000 arasında tam sayı. Tekrarlanan büyüklükler çıkarılır ve liste sıralanır.
- Runs per size: her büyüklük için 2–50 tekrar; ödev varsayılanı 5.
- Experiment: yalnız π, yalnız e veya ikisi.
- Random seed: 0–4.294.967.295 arasında tam sayı. Aynı ayarlarla aynı sonuç elde edilir.
- Run simulation: yeni deney; mevcut sonuçları sıfırlar. Çalışma sürerken ikinci deney başlatılamaz.
- Stop: çalışmayı iptal eder. Tamamlanmış tekrarlar günlükte, tamamlanmış örneklem grupları tabloda kalır.
- CSV: tamamlanmış gruplardaki tüm tekrarlar ve grup istatistikleri.
- JSON: motor bilgisi, ayarlar, günlük, sonuçlar ve durumun tamamı.

## π tahmini

Her denemede [0,1) aralığından iki sayı x ve y üretilir. `x*x+y*y <= 1` ise nokta birim çeyrek dairenin içindedir. Karenin alanı 1, çeyrek daireninki π/4 olduğundan:

`π tahmini = 4 × içerideki nokta sayısı / N`

N bir tekrardaki nokta sayısıdır. Beş tekrar beş ayrı tahmin oluşturur. Örneğin N=100 ve 79 iç nokta varsa tahmin 3,16'dır. Bu bir açıklama örneğidir, programın sabit çıktısı değildir.

## Euler sayısının tahmini

Bir deney için toplam sıfırdan başlar. Bağımsız uniform sayılar toplam 1'i **aşana kadar** eklenir. Gerekli sayı adedi K olarak tutulur. Tam 1 olması durdurmaz. Bu işlem N kez yapılıp K değerlerinin ortalaması alınır:

`e tahmini = (K₁ + ... + Kₙ) / N`

Bu yöntemin temeli E[K]=e eşitliğidir. N burada üretilen toplam uniform sayı adedi değil, e için tamamlanan deney sayısıdır.

## Rastgelelik ve tekrar üretilebilirlik

Go motoru `math/rand/v2` içindeki PCG üretecini kullanır. Her tekrar için ayrı üreteç oluşturulur. Birinci başlangıç değeri kullanıcı seed'idir. İkincisi örneklem büyüklüğü, tekrar indeksi ve deney türünden oluşturulur:

`uint64(n)<<32 | uint64(run)<<8 | tag`

Geçerli sınırlar içinde alanlar çakışmaz; π için tag=1, e için tag=2 kullanılır. Böylece deney sırası veya başka bir örneklem büyüklüğü eklenmesi aynı grubun sonuçlarını değiştirmez. Euler-only sonuçları aynı seed ve ayarlarla both içindeki Euler sonuçlarıyla aynıdır. Bunlar deterministik sözde rastgele akışlardır; matematiksel bağımsızlık garantisi olarak yorumlanmamalıdır.

**Önceki Python sürümü farklı üreteç kullanıyordu. Aynı seed ile eski sayılar beklenmemelidir. Eski raporlar otomatik güncellenmez; yeni raporda Go sonuçları kullanılmalıdır.**

## Sonuçlar ve grafikler

`Row` her N için tekrar değerlerini, ortalamayı, teorik değeri, mutlak hatayı ve örneklem standart sapmasını tutar. Ortalama tekrar tahminlerinin toplamının tekrar sayısına bölünmesidir. Mutlak hata `abs(ortalama - teorik değer)` şeklindedir; tekrarların mutlak hatalarının ortalaması değildir. SD, kare farkları toplamının `(tekrar sayısı - 1)` değerine bölünmesinin kareköküdür. SD bir güven aralığı veya standart hata değildir.

Sol grafik tekrarları, ortalamayı ve teorik değeri gösterir. Sağ grafik hata ile SD'yi gösterir. N ekseni ve sağ grafiğin büyüklük ekseni logaritmiktir; sıfır değerler logaritmik grafikte gösterilmez. Yakınlaştırma, kaydırma, eksen sıfırlama ve PNG indirme bulunur.

N arttıkça tahminler genellikle daha kararlı olur; Monte Carlo hatasının tipik ölçeği yaklaşık 1/√N'dir. Ancak her çalışmada veya her ardışık N'de hata azalmak zorunda değildir. Özellikle beş tekrar üzerinden hesaplanan SD de değişkenlik gösterir.

## Go içinde çalışma akışı

1. `main` komut seçeneklerini okur, loopback adresinde dinleyici açar ve oturuma özel rastgele token üretir.
2. Ana sayfa token ile sunulur. JavaScript başlatma isteğini `/api/start` adresine gönderir.
3. API, JSON yapısını ve değerlerini doğrular. `Config.Validate` kabul edilen sınırları kontrol eder.
4. `Manager.Start` ayarları kopyalar, çalışan deney kontrolü yapar ve bir goroutine başlatır.
5. `Estimate` sayısal hesabı yürütür. Her 256 adımda context iptali kontrol edilir; Euler'in iç döngüsü de iptal edilebilir.
6. Her tamamlanan tekrar sonrası günlük ve ilerleme güncellenir. Grup bitince `summarize` istatistikleri hesaplar.
7. Mutex, durumun eş zamanlı okunması ve yazılması sırasında veri yarışını önler. `Snapshot` dışarıya bağımsız bir kopya verir.
8. Stop context'i iptal eder. Ctrl+C hem işi iptal eder hem HTTP sunucusunu kapatır; program işçinin bitmesini bekler.

Tek bir simülasyon işi çalışır; HTTP istekleri Go sunucusunun eş zamanlı istek desteğiyle yanıtlanır. Sonuçlar bellektedir; program kapanmadan CSV/JSON indirilmelidir.

## API

| Yol | Yöntem | İşlev |
| --- | --- | --- |
| `/api/state` | GET | Durum ve sonuçlar |
| `/api/start` | POST | Doğrulanmış ayarlarla başlatma |
| `/api/stop` | POST | İptal isteme |
| `/export.csv` | GET | Tamamlanmış grupları indirme |
| `/export.json` | GET | Durumun tamamını indirme |

Sunucu yalnızca 127.0.0.1 üzerinde dinler. Host denetimi vardır. POST istekleri sayfadaki `X-App-Token` değerini gerektirir. Başlatma gövdesi 8192 baytla sınırlıdır; bilinmeyen alanlar ve birden fazla JSON nesnesi reddedilir. Sadece izin verilen arayüz dosyaları sunulur. Bu yerel kullanım içindir; internete açık çok kullanıcılı bir servis değildir.

## Kontroller

```sh
go test -race ./...
go vet ./...
```

Testler π sınır koşulunu, e toplamının tam 1 olması durumunu, 40 varsayılan tekrarı, tekrar üretilebilirliği, deneylerin birbirinden etkilenmemesini, doğrulamayı, aynı anda ikinci çalışmanın reddini, iptali, SD hesabını, HTTP token/Host kontrollerini ve CSV satırlarını kapsar. Race kontrolü testlerde çalıştırılan eş zamanlı kod yollarını denetler.

## Teknik kaynaklar

- [Go embed](https://pkg.go.dev/embed): arayüzün derlenmiş dosyaya alınması.
- [Go math/rand/v2](https://pkg.go.dev/math/rand/v2): PCG ve deterministik üreteç.

## UI TripleD arayüzü

Güncel arayüz UI TripleD'nin MIT lisanslı Native Tabs ve Native Magnetic bileşenlerinden uyarlanmıştır. `frontend/components.jsx` gerçek React / Base UI / Framer Motion bileşenlerini içerir. Sekmeler klavye ile kullanılabilir; aktif sekme hareketli bir arka planla belirtilir. İmza üzerinde hafif manyetik hareket vardır; azaltılmış hareket tercihinde kapatılır. Go hesaplaması değişmemiştir. DengeX CSS artık sayfada yüklenmez; eski dosyalar kaynak bilgileriyle korunur.

Arayüz bileşenlerini değiştirdikten sonra:

```sh
npm ci
npm run build
go build -trimpath -o bin/monte-carlo-studio .
```

Node.js yalnızca ön yüzü derlemek için gerekir. Hazır `assets/components.js` Git deposunda olduğundan normal Go derlemesi ve programın çalışması Node.js gerektirmez. `assets/vendor/SOURCES.md` uyarlanan dosyaları ve lisansı açıklar.
