# Monte Carlo Studio — sıfırdan, adım adım

Bu rehber hiçbir programlama bilgisi gerektirmeden sistemi anlaman için yazıldı. Önce ekranı ve deneyleri, sonra dosyaların içinde neler olduğunu anlatıyor. Proje AI yardımıyla geliştirilmiştir.

## 1. Bu program ne yapıyor?

Program rastgele sayılar kullanarak iki sayıya yaklaşmaya çalışıyor:

- **π (pi):** yaklaşık 3,141593.
- **e (Euler sayısı):** yaklaşık 2,718282.

Bu sayıları hesap makinesinden okuyup sonuç diye yazmıyor. Deney yapıp bir tahmin üretiyor. Bildiğimiz gerçek değerleri de tahminimizin ne kadar iyi olduğunu görmek için kullanıyor.

“Monte Carlo” burada bir yöntem adı: kesin cevabı doğrudan hesaplamak yerine çok sayıda rastgele deneme yapıyoruz. Az denemede şansın etkisi büyük; çok denemede sonuç genellikle daha dengeli.

## 2. Sistemi üç parça olarak düşün

Bir restoran benzetmesi yapalım:

| Parça | Restorandaki karşılığı | Bu projede yaptığı iş |
| --- | --- | --- |
| Tarayıcıdaki ekran | Menü ve sipariş ekranı | Ayarlarını alır, sonuçları ve grafikleri gösterir. |
| Go programı | Mutfak | Deneyleri hesaplar, sonuçları saklar ve ekrana gönderir. |
| Python dosyası | Kapıyı açan kişi | Hazır Go programını başlatır. Görevi bu kadar. |

Grafikler tarayıcıda JavaScript ile çizilir. Simülasyon hesapları Go ile yapılır. **Python hesaplama yapmaz.** Python kullanmadan Go programını doğrudan çalıştırmak da mümkündür.

## 3. Şimdi nasıl açacağım?

Bu bilgisayardaki proje klasöründe `Monte Carlo.command` dosyasına çift tıklayabilirsin. Terminalden açmak istersen proje klasöründe şu komutu çalıştır:

```sh
python3 odev.py
```

Tarayıcı açılır. Varsayılan deney kendiliğinden başlar. Ekranda `Complete` ve `%100` görünmesi hesaplamanın bittiğini söyler.

Terminal, bilgisayara yazıyla komut verdiğin penceredir. Komutları o pencereye yazıyorsun; Python dosyasının içine yapıştırmıyorsun. “Proje klasöründe çalıştır” demek terminalin bu dosyaların bulunduğu klasörde olması demektir.

Programı kapatmak için onu başlattığın terminalde **Ctrl+C** kullan. Yalnızca tarayıcı sekmesini kapatırsan program arka planda çalışmayı sürdürebilir.

### GitHub’dan ilk kez indiren biri ne yapacak?

Bilgisayarında Go 1.24 veya üzeri kurulu olmalı. Ardından:

```sh
git clone https://github.com/dengexco/monte-carlo-studio.git
cd monte-carlo-studio
go build -trimpath -o bin/monte-carlo-studio .
./bin/monte-carlo-studio
```

Depo gizlidir; indiren kişinin GitHub üzerinden erişim yetkisi olmalıdır. Son iki komut macOS/Linux içindir. Windows'ta derleme çıktısına `.exe` eklenir:

```sh
go build -trimpath -o bin/monte-carlo-studio.exe .
.\bin\monte-carlo-studio.exe
```

“Derlemek” yazdığımız Go dosyalarını bilgisayarın çalıştırabileceği programa çevirmek demektir. `bin` klasörü bu hazır programın bulunduğu yerdir. Hazır program GitHub’a yüklenmez; kaynak koddan oluşturulur. Bu bilgisayardaki hazır dosya macOS ARM64 içindir.

## 4. Ekrandaki kutulara ne yazacağım?

| Ekrandaki yazı | Anlamı | Başlangıç için değer |
| --- | --- | --- |
| Sample sizes | Her tekrarda kaç deneme yapılacak? | `10, 100, 1000, 10000` |
| Runs per size | Her büyüklük kaç kez yeniden denenecek? | `5` |
| Experiment | Hangi sayıyı tahmin edeceğiz? | `Pi + Euler` |
| Random seed | Rastgele sayı dizilerini belirleyen başlangıç numarası | `20261019` |
| Run simulation | Bu ayarlarla yeni deney başlat | Düğmeye bas. |
| Stop | Devam eden hesabı durdur | Gerekirse bas. |

**N ile tekrar sayısı aynı şey değildir.** N=100 ve tekrar=5 dediğinde tek bir 500 denemelik tahmin yapmıyoruz. Her birinde 100 deneme olan 5 ayrı tahmin üretiyoruz. Sonra bu 5 tahminin ortalamasını alıyoruz.

Varsayılan ekrandaki **40**, `4 büyüklük × 5 tekrar × 2 deney türü` demektir. Toplam kullanılan rastgele sayı adedi değildir.

Seed'i bir müzik listesinin numarası gibi düşünebilirsin. Aynı numara ve aynı ayarlar aynı dizileri üretir. Seed'i değiştirince farklı bir deney elde edersin. Aynı seed ile yeniden çalıştırınca aynı sonuç çıkması programın bozulduğu anlamına gelmez.

## 5. Pi deneyi: kareye nokta atmak

Kenarları 1 birim olan bir kare düşün. İçine yarıçapı 1 olan bir çeyrek daire çiz. Bilgisayar bu karenin içine rastgele noktalar koyuyor.

Her noktanın iki koordinatı var: x ve y. İkisi de 0 dahil, 1 hariç aralıktan seçiliyor. `x² + y² ≤ 1` ise nokta çeyrek dairenin içinde veya sınırındadır.

Kare alanı 1; çeyrek daire alanı π/4. Dolayısıyla içeride kalan noktaların oranı yaklaşık π/4 olur. Oranı 4 ile çarpınca π tahmini çıkar.

**Sadece anlatım için örnek:** 100 noktadan 79'u içeride kaldıysa:

```text
İçerideki oran = 79 / 100 = 0,79
Pi tahmini    = 4 × 0,79 = 3,16
```

Program bunu her tekrar için yeniden yapar. Yukarıdaki 79 sayısı sabit bir program sonucu değildir.

## 6. Euler deneyi: toplam 1’i geçene kadar sayı eklemek

Bu deneyde nokta veya daire yok. Başlangıçta toplam 0:

```text
0,40 geldi → toplam 0,40 → devam et
0,35 geldi → toplam 0,75 → devam et
0,50 geldi → toplam 1,25 → dur
```

Bu turda 3 sayı kullandık. Sonuç olarak **3** kaydediyoruz; 1,25'i değil.

Sonra toplamı tekrar sıfırlayıp yeni tur yapıyoruz. N=100 ise 100 tur yapıp her turda kaç sayı gerektiğinin ortalamasını alıyoruz. Bu ortalama e sayısını tahmin ediyor. Yöntemin matematiksel özelliği, bir turdaki sayı adedinin beklenen değerinin e olmasıdır.

Toplamın tam 1 olması yetmez: **1'i aşması** gerekir. Örneğin 0,50 + 0,50 = 1 olduğunda bir sayı daha eklenir.

Buradaki N, kaç tur yaptığımızdır. Tek bir turda birden fazla rastgele sayı kullanılır.

## 7. Sonuçları nasıl okuyacağım?

| Terim | Günlük dille anlamı |
| --- | --- |
| Estimate | Bir tekrarın bulduğu tahmin. |
| Mean | Aynı N için tekrarların ortalaması. |
| Theoretical / Reference | Karşılaştırma için kullandığımız gerçek değer. |
| Absolute error | Ortalamanın gerçek değerden uzaklığı. Küçük olması iyi. |
| SD / Sample SD | Tekrar sonuçlarının birbirinden ne kadar ayrıldığı. Küçükse daha tutarlı. |
| Completed runs | Tamamlanan tekrarların sayısı. |

Örneğin 3 tahmin `3,10; 3,20; 3,15` ise ortalama `(3,10 + 3,20 + 3,15) / 3 = 3,15` olur. Pi için mutlak hata yaklaşık `|3,15 − 3,141593| = 0,008407` olur. Dikey çizgiler “eksi işaretini önemseme, uzaklığı al” demektir.

SD ile hata farklı soruları cevaplar. Tekrarlar birbirine çok yakın olup gerçek değerden uzak olabilir. Bu durumda SD küçük, hata büyük olabilir. SD bir güven aralığı değildir.

Üstteki büyük π ve e kartları **o deney için tamamlanan en büyük N grubunun ortalamasını** gösterir. Tüm N değerlerinin ortak ortalamasını göstermez.

### Grafikler

Her deneyin sol grafiği tahminleri gösterir. Noktalar tekrarlar, ortalama çizgisi onların ortalaması, teorik çizgi hedef değerdir. Sağ grafik hata ve SD'yi gösterir.

Yatay eksende 10, 100, 1000 ve 10000 eşit aralıklı görünebilir. Çünkü eksen logaritmiktir: her adımda 10 kat büyür. Sağ grafiğin dikey ekseni de logaritmiktir. Sıfırın logaritması gösterilemediği için hata veya SD tam sıfırsa o değer bu grafikte atlanır.

Fareyle alan seçerek yakınlaştırabilir, çift tıklayarak görünümü sıfırlayabilirsin. Kamera düğmesi grafiği PNG resim olarak indirir.

### N arttığında ne bekleyeceğim?

Genellikle daha kararlı ve gerçek değere daha yakın tahminler. Ama her yeni N'de hatanın mutlaka düşmesi gerekmez; deney hâlâ rastgeledir. Tipik hata ölçeği yaklaşık `1 / √N` olduğu için deneme sayısını 4 katına çıkarmak hatanın tipik ölçeğini yaklaşık yarıya indirir; bu tek bir çalışmanın garantisi değildir.

## 8. Sonuçları nasıl kaydederim?

- **Overview:** grafikler.
- **All results:** her tekrarın sayısal sonucu ve grup istatistikleri.
- **Run log:** tamamlanan tekrarların sıralı günlüğü.
- **CSV:** Excel gibi programlarla açabileceğin tablo dosyası.
- **JSON:** ayarlar, günlük ve sonuçların programlar tarafından okunabilir kaydı.

Yeni deney başlatınca eski sonuçlar değişir. Programı kapatınca bellekteki sonuçlar kaybolur. Saklamak istiyorsan önce indir.

Stop'a bastığında yarım kalan grup için ortalama tabloya eklenmez. Tamamlanmış tekrarları günlükte görebilirsin; CSV sadece tamamen bitmiş grupları içerir. Bu yüzden iptal edilmiş bir deneyde günlükte CSV'den daha fazla tekrar olabilir.

## 9. Run’a basınca arka planda ne oluyor?

```text
Sen ayarları girersin.
        ↓
Tarayıcı ayarları Go programına yollar.
        ↓
Go değerleri kontrol eder ve hesabı başlatır.
        ↓
Her tekrar bitince sonucu ve ilerlemeyi günceller.
        ↓
Tarayıcı yaklaşık 0,4 saniyede bir yeni durumu sorar.
        ↓
JavaScript sayıları tabloya yazar ve grafikleri çizer.
```

Ekran çok hızlı biten bir deneyde doğrudan %100'e atlayabilir. Bu normaldir: hesaplama, ekranın bir sonraki güncellemesinden önce bitmiştir.

## 10. Dosyaları hangi sırayla okuyayım?

| Sıra / Dosya | İçinde ne var? |
| --- | --- |
| 1. `odev.py` | Kısa başlatıcı. Proje yolunu bulur, hazır Go dosyasını kontrol eder ve çalıştırır. |
| 2. `internal/simulation/simulation.go` | Asıl matematik ve deney yönetimi. |
| 3. `main.go` | Tarayıcıyla konuşan yerel sunucu ve komut seçenekleri. |
| 4. `assets/index.html` | Ekranın iskeleti: kutular, düğmeler ve sonuç alanları. |
| 5. `assets/app.css` | Renkler, boşluklar, yazı büyüklükleri ve mobil görünüm. |
| 6. `assets/app.js` | Başlat/durdur işlemleri, durum sorguları ve Plotly grafikleri. |
| 7. `frontend/components.jsx` | UI TripleD'den uyarlanan animasyonlu sekmeler ve logo/imza hareketi. |
| `assets/components.js` | Yukarıdaki React dosyasının tarayıcıya hazırlanmış hali; bunu elle düzenleme. |
| `assets/vendor/dengex-logo.png` | DengeX sitesinden alınan gerçek logo. |
| `assets/vendor/plotly.min.js` | Grafik çizme kütüphanesi. |
| `assets/vendor/SOURCES.md` | Kullanılan üçüncü taraf kaynaklar ve lisans bilgileri. |
| `go.mod` | Go projesinin adı ve gereken Go sürümü. |
| `package.json` | Ön yüzün derleme komutu ve JavaScript bağımlılıkları. |
| `package-lock.json` | Yüklenen JavaScript paketlerinin kesin sürümleri. |
| `.gitignore` | GitHub'a hangi yerel dosyaların gönderilmeyeceği. |

Eski DengeX CSS dosyaları klasörde duruyor ama güncel sayfada yüklenmiyor. Güncel tasarım özel CSS ile UI TripleD bileşenlerini birleştiriyor.

## 11. Go dosyasındaki isimler ne anlama geliyor?

`Config` deney ayarlarının kutusudur: N listesi, tekrar sayısı, seed ve deney türü. `Validate` bu ayarları kontrol eder. Örneğin N=0 kabul edilmez.

`Manager` deneyin yöneticisidir. Bir deney çalışırken ikinci deneyin başlamasını engeller. `Start` başlatır, `Stop` iptal ister, `Wait` işin bitmesini bekler.

`Estimate` bir tekrarın hesabını yapar. π seçiliyse nokta sayar; e seçiliyse toplamın 1'i aşması için gereken sayı adetlerini toplar.

`summarize` tekrar sonuçlarının ortalamasını, mutlak hatasını ve örneklem standart sapmasını hesaplar. Standart sapma hesabında bölen tekrar sayısının bir eksiğidir.

`Row` bir N grubunun sonuç kutusudur. `Log` tek bir tamamlanmış tekrarın kaydıdır. `State` ekranda görülecek bütün durumdur: çalışıyor mu, yüzde kaç bitti, hangi sonuçlar hazır?

`Snapshot` o durumun bağımsız bir kopyasını alır. Böylece ekran sonuçları okurken hesaplama kendi işine devam edebilir.

Bir **goroutine**, Go'nun ayrı bir iş akışı başlatmasıdır. Hesaplama bu akışta sürerken sunucu tarayıcıya cevap verebilir. **Mutex**, aynı durum bilgisinin eş zamanlı değiştirilmesini/okunmasını düzenleyen kilittir. **Context**, Stop'a basınca çalışana iletilen iptal sinyalidir. Hesaplama bu sinyali düzenli aralıklarla kontrol eder.

`main.go` içindeki `handler`, gelen isteği ilgili işe yönlendirir. **API**, tarayıcı ile Go'nun anlaştığı adreslerdir. `/api/start` başlatma, `/api/state` durum sorma, `/api/stop` durdurma adresidir. **JSON**, bu konuşmada kullanılan yapılandırılmış yazı biçimidir.

## 12. “Local”, port ve token ne demek?

`127.0.0.1` kendi bilgisayarını gösterir. `8765` bir kapı numarası gibi çalışan **port** numarasıdır. `http://127.0.0.1:8765/` bu bilgisayardaki programın o kapısına gitmek demektir. Bu adres internette herkese açık bir site değildir.

Program varsayılan olarak boş bir port seçer. Hep 8765 kullanmak istersen:

```sh
python3 odev.py --port 8765
```

**Token**, programın sayfaya verdiği geçici doğrulama değeridir. Tarayıcı başlatma/durdurma isteğinde bunu geri yollar. Program ayrıca istenen adresi kontrol eder. Bunlar yerel sunucuya yanlış kaynaklardan gelen istekleri sınırlamak içindir; uygulama internete açık çok kullanıcılı servis olarak tasarlanmamıştır.

## 13. Bir şeyi değiştirirsem ne yapmalıyım?

Go, HTML, CSS, `assets/app.js` veya logo değiştirdiysen:

```sh
go build -trimpath -o bin/monte-carlo-studio .
```

Sonra eski programı Ctrl+C ile durdur ve tekrar başlat. Sayfayı yenile. Çünkü Go arayüz dosyalarını derleme sırasında kendi içine alıyor. Sadece dosyayı kaydetmek, çalışan eski programı değiştirmez.

React bileşenlerini (`frontend/components.jsx`) değiştirdiysen önce bunları tarayıcının okuyacağı dosyaya çevir:

```sh
npm ci
npm run build
go build -trimpath -o bin/monte-carlo-studio .
```

Bu işlem için Node.js/npm gerekir. `npm ci` kilit dosyasındaki paketleri yükler; `npm run build` bunları tek bir ön yüz dosyası halinde hazırlar. Hazır dosya depoda bulunduğu için yalnızca uygulamayı çalıştıran kişinin Node.js kurmasına gerek yoktur.

## 14. Sık karşılaşılan durumlar

| Gördüğün durum | Yapacağın şey |
| --- | --- |
| “Go uygulaması derlenmemiş” | Yukarıdaki `go build` komutunu proje klasöründe çalıştır. |
| `go: command not found` | Go kurulu değil veya terminal bulamıyor. Go kurulumu ve PATH ayarını kontrol et. |
| “address already in use” | Seçilen port dolu. Kendi eski uygulamanı kapat veya `--port` vermeden başlat. |
| Tarayıcı sunucuya ulaşamıyor | Terminalde programın çalıştığını ve açtığın adresin terminalde yazan adres olduğunu kontrol et. |
| Tasarım değişikliği görünmüyor | Gerekli ön yüz derlemesini, ardından Go derlemesini yap; programı yeniden başlat ve sayfayı yenile. |
| Sonuçlar her seferinde aynı | Seed aynıysa beklenen davranış. Farklı deney için seed'i değiştir. |
| Eski Python çıktısıyla sayılar uyuşmuyor | Go farklı rastgele sayı üreteci kullanıyor. Eski raporlar otomatik güncellenmez. |
| N büyüdü ama hata da büyüdü | Tek bir rastgele deneyde mümkün. Büyük N her adımda iyileşme garantisi vermez. |

## 15. Programın doğru çalıştığını nasıl kontrol ediyoruz?

```sh
go test -race ./...
go vet ./...
```

İlk komut otomatik kontrolleri çalıştırır; `-race` çalıştırılan kod yollarında eş zamanlı veri erişimi sorunlarını da arar. İkinci komut Go kodunda şüpheli kullanımları inceler. Testin geçmesi mümkün olan bütün hataların yok olduğu anlamına gelmez; test edilen davranışların beklendiği gibi çalıştığını gösterir.

Kontroller arasında π sınırı, e için toplamın tam 1 olması, 40 tekrarın tamamlanması, aynı seed'in aynı sonucu üretmesi, iptal, hatalı ayarlar, API erişim kontrolleri ve CSV satırları var.

## 16. Kendini kontrol et

Bu soruları kendi cümlelerinle cevaplayabiliyorsan temel sistemi anlamışsındır:

1. N=100 ile tekrar=5 arasındaki fark ne?
2. Pi tahmininde neden 4 ile çarpıyoruz?
3. Euler deneyinde 1,25 toplamını mı, kullanılan sayı adedini mi kaydediyoruz?
4. Ortalama, mutlak hata ve SD hangi farklı bilgileri veriyor?
5. Seed aynıysa neden sonuçlar tekrar ediyor?
6. Python'un görevi ne; asıl hesap nerede yapılıyor?
7. CSS değişince neden Go programını tekrar derliyoruz?
8. Sonuçları kaydetmeden programı kapatırsan ne olur?

Aşağıdaki bölüm, ayrıntıya bakmak istediğinde başvurabileceğin teknik bilgileri korur.

---

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

## Ders PDF’si ile doğrulama ve Docs sekmesi

Kaynak: `I-Stochastic Processes.pdf`, 67 sayfa, Manisa Celal Bayar University / Industrial Engineering. 61–66. sayfalar incelendi. π yöntemi 62. sayfadaki çeyrek daire sayımıyla; e yöntemi 64. sayfadaki toplam 1’i aşana kadar çekiliş sayımıyla aynıdır. Algoritma değişikliği gerekmedi. e kodundaki sayaç tüm turların çekilişlerini biriktirir; n’e bölünmesi slayttaki Nᵢ değerlerinin ortalamasıyla aynıdır.

Uygulamanın **Docs** sekmesi yöntemleri, 63 ve 65. sayfalardaki yatay sonuç tablolarını (Run 1…Run 5, Mean, Reference), ayar uygunluğu göstergesini ve 66. sayfadaki beş tartışma sorusunu içerir. Tablolar mevcut simülasyon verisinden oluşur. Yorumlama kılavuzu, gözlenmemiş sonuçlar hakkında hüküm vermez.

Dil şartı farklılığı: PDF 61. sayfada Python ister; ayrıca paylaşılan yönerge başka dillere izin verir. Kullanıcının Go tercihi korunmuştur. Bu nedenle matematiksel yöntem eşleşmesi, Python şartıyla veya AI kullanımı yasağıyla tam teslim uygunluğu anlamına gelmez. Ders PDF’si depoya kopyalanmamıştır.
