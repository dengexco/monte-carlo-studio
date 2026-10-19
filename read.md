# Monte Carlo Studio kod rehberi

Bu proje, Monte Carlo yöntemiyle π ve Euler sayısı e'yi tahmin eden yerel bir Python uygulamasıdır. Kullanıcı örneklem büyüklüklerini, bağımsız çalıştırma sayısını, rastgelelik tohumunu ve deney türünü değiştirir. Sonuçları etkileşimli grafiklerde ve tabloda inceler.

Arayüzün sağ altında **doğukan ercan** yer alır. Arayüz İngilizcedir. Bu rehber Türkçedir. Proje yapay zekâ desteğiyle geliştirilmiştir; ders yönergesindeki yapay zekâ kullanım yasağı bu geliştirmeden bağımsız olarak geçerlidir.

## 1. Kurulum ve başlatma

Python 3.10 veya üzeri gerekir. Yeni bir bilgisayarda proje klasöründe:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python odev.py
```

Bu bilgisayarda ortam kurulu olduğu için doğrudan:

```bash
python3 odev.py
```

`odev.py`, proje içindeki `.venv/bin/python` dosyasını bulduğunda o ortamı otomatik kullanır. Ortam yoksa mevcut Python yorumlayıcısıyla devam eder ve bağımlılıkların önceden kurulmuş olması gerekir. Windows'ta `.venv` ortamını manuel etkinleştirmek gerekir; otomatik ortam seçimi macOS/Linux yolu kullanır.

macOS'ta `Monte Carlo.command` dosyasına çift tıklamak da uygulamayı başlatır. Bu başlatıcı proje içindeki sanal ortamın kurulmuş olmasını bekler.

Python yalnızca `127.0.0.1` üzerinde yerel bir sunucu açar ve tarayıcıyı otomatik başlatır. Bu bir internete yayınlama işlemi değildir. Terminal açık kaldığı sürece uygulama çalışır. Sunucuyu kapatmak için terminalde `Ctrl+C` kullanılır. Tarayıcı sekmesini kapatmak Python sunucusunu durdurmaz.

Diğer çalışma biçimleri:

```bash
python3 odev.py --no-browser --port 8765
python3 odev.py --no-gui
```

İlk komut tarayıcı açmadan belirli portta çalışır. İkinci komut arayüzsüz olarak özgün ödev deneylerini çalıştırır, terminale sonuçları ve küçük örneğin adımlarını yazar, `odev_ciktilari` klasörüne grafik ve JSON dosyaları kaydeder.

## 2. Dosya düzeni

| Dosya | Görevi |
|---|---|
| `odev.py` | Deney algoritmaları, terminal çıktıları, statik grafik üretimi ve başlangıç noktası |
| `web_app.py` | Yerel HTTP sunucusu, ayar doğrulama, arka plan simülasyonu, durdurma ve veri indirme |
| `assets/index.html` | Form, sonuç alanı, grafikler, tablo, günlük ve imza |
| `assets/app.css` | Uygulamaya özel yerleşim ve DengeX renk uyarlamaları |
| `assets/app.js` | Düğmeler, sunucuyla iletişim, ekran güncellemeleri ve Plotly grafikleri |
| `assets/vendor/dengex-app.css` | DengeX sitesinden alınan asıl CSS dosyası |
| `assets/vendor/dengex-marketing.css` | DengeX form stilleri |
| `assets/vendor/plotly.min.js` | Yerel etkileşimli grafik kütüphanesi |
| `assets/vendor/SOURCES.md` | Üçüncü taraf dosyaların kaynakları |
| `requirements.txt` | Kurulacak Python paketlerinin sabit sürümleri |
| `test_simulation.py` | Algoritma, giriş doğrulama ve durdurma kontrolleri |
| `.gitignore` | GitHub'a eklenmeyecek yerel dosyalar |

## 3. Arayüz nasıl kullanılır

1. **Sample sizes** alanına `10, 100, 1000, 10000` gibi değerler girilir. Virgüller liste ayırıcıdır; binlik ayırıcı kullanılmaz. Örneğin on bin için `10000` yazılır.
2. **Runs per size** aynı örneklem büyüklüğünde kaç bağımsız tahmin üretileceğini belirler. Ödev düzeni için 5 kullanılır.
3. **Experiment** alanından iki deney birlikte, yalnızca π veya yalnızca e seçilir.
4. **Random seed**, sözde rastgele sayı üretecinin başlangıç değeridir. Aynı ayarlar ve aynı tohum, aynı sırayla aynı sonuçları üretir.
5. **Run simulation** yeni bir çalışma başlatır. İlk açılışta varsayılan ayarlar otomatik çalışır.
6. **Stop** devam eden hesaplamayı iptal eder. Tamamlanmış örneklem grupları ve çalışma günlüğü kalır. Eksik bir grup sonuç tablosuna eklenmez.
7. Grafik üzerinde sürükleyerek yakınlaştırma, çift tıklayarak sıfırlama yapılabilir. Üstteki araçlardan kaydırma ve PNG kaydetme kullanılabilir. Lejanttaki seri adına tıklamak o seriyi gizler veya gösterir.
8. **All results** her çalıştırmanın sonucunu, grup ortalamasını, ortalama hatasını ve standart sapmasını gösterir.
9. **Run log** her tamamlanan çalıştırmanın kaydını gösterir. Bu günlük her üretilen rastgele sayıyı göstermez. Sayı düzeyindeki örnek adımlar için `--no-gui` kullanılır.
10. **CSV** ve **JSON** bağlantıları o andaki sonuçları indirir. JSON ayarları ve çalışma durumunu da içerir. CSV yalnızca tamamlanan örneklem gruplarını içerir; iptal edilen son grubun kısmi çalıştırmaları günlükte kalır.

En büyük n için ortalama ve mutlak hata özet alanında gösterilir. Durdurulmuş bir deneyde bu, son tamamlanmış grubun değeridir. Arayüz deney sırasında ayar değiştirmeye izin verse de çalışan deney, başlatıldığı andaki ayarların kopyasını kullanır. Yeni değerler sonraki çalıştırmada uygulanır.

## 4. Pi algoritması

`pi_tahmini(n, rng, detay=False)` fonksiyonu n nokta üretir. Her noktanın koordinatları için iki bağımsız düzgün dağılımlı değer kullanılır:

```python
x = rng.random()
y = rng.random()
```

`random()` 0 dahil, 1 hariç aralıkta sözde rastgele bir sayı üretir. Noktanın çeyrek daire içinde olup olmadığı şu koşulla bulunur:

```python
x**2 + y**2 <= 1
```

Koşulu sağlayan noktalar `iceride` sayacına eklenir. Sonuç:

```python
4 * iceride / n
```

Birim karenin alanı 1, birim yarıçaplı çeyrek dairenin alanı π/4'tür. İçeride kalma oranı bu alan oranını tahmin eder. Dörtle çarpılması π tahminini verir. Örneğin 10 noktadan 8'i içerideyse tahmin 3.2'dir. Bu örnek, her çalıştırmanın aynı sonucu vereceği anlamına gelmez.

## 5. Euler sayısı algoritması

`e_tahmini(n, rng, detay=False)` fonksiyonu n ayrı toplama deneyi yapar. Her deneyde `toplam` ve `sayac` sıfırlanır. Toplam 1'i aşana kadar sayılar eklenir:

```python
while toplam <= 1:
    sayi = rng.random()
    toplam += sayi
    sayac += 1
```

Döngünün `<= 1` olması önemlidir: toplam tam 1 ise henüz durulmaz. Her deneyin sayacı `toplam_sayac` değişkenine eklenir. Sonuç `toplam_sayac / n` olur.

Örneğin 0.2, 0.6 ve 0.5 üretilirse toplam sırasıyla 0.2, 0.8 ve 1.3 olur. O deneyin sayacı 3'tür. e tahmini tek bir sayaç değildir; n deneyin sayaçlarının ortalamasıdır. Bu sayacın beklenen değeri e'dir.

## 6. n ile tekrar sayısının farkı

π deneyinde n, tek bir tahminde kullanılan nokta sayısıdır. e deneyinde n, tek bir tahminde tamamlanan toplama deneyi sayısıdır. Tekrar sayısı ise bu tahmin işleminin kaç kez yeniden yapıldığıdır.

Dört n değeri, beş tekrar ve iki deney için toplam tahmin sayısı `4 × 5 × 2 = 40` olur. Bu sayı, üretilen rastgele sayı adedi değildir.

## 7. Tohum ve bağımsız çalıştırmalar

Her yeni çalışma başında `random.Random(seed)` ile bir üreteç oluşturulur. Tohum her tekrar başında sıfırlanmaz. Böylece tekrarlar üretecin ilerleyen akışından yeni örnekler alır. Bu, standart sözde rastgele Monte Carlo uygulamasıdır; tohum kullanılması gerçek fiziksel rastgelelik anlamına gelmez.

Varsayılan sırada önce tüm π çalıştırmaları, sonra e çalıştırmaları yapılır. Yalnızca e seçilirse üretecin başlangıcından doğrudan e'ye geçilir. Bu nedenle aynı tohumla “yalnızca e” ve “iki deney birlikte” seçeneklerinin e sonuçları farklı olabilir.

## 8. Özet istatistikler

Bir örneklem büyüklüğündeki tahminler `values` listesinde tutulur:

- `statistics.mean(values)` çalıştırmaların aritmetik ortalamasını verir.
- `abs(mean - reference)` bu ortalamanın teorik değerden mutlak uzaklığıdır. Tek tek çalıştırmaların mutlak hatalarının ortalaması değildir.
- `statistics.stdev(values)` örneklem standart sapmasıdır. R tekrar varsa payda R − 1 kullanılır.

Standart sapma hesaplanabilmesi için arayüz en az iki tekrar ister. Standart sapma, ortalamanın standart hatası veya güven aralığı olarak sunulmaz.

Sağdaki hata grafiğinin düşey ekseni logaritmiktir. Tam sıfır hata veya standart sapma logaritmik eksende gösterilemez; bu değerler grafikte atlanır ve açıklama gösterilir. Tabloda gerçek sıfır değer korunur.

## 9. Python sunucusu

`launch()` fonksiyonu `ThreadingHTTPServer` oluşturur. Port varsayılan olarak 0'dır; işletim sistemi boş bir port seçer. Sunucu yalnızca `127.0.0.1` adresine bağlanır.

| İstek | İşlev |
|---|---|
| `GET /` | HTML arayüzünü döndürür |
| `GET /api/state` | Durum, ilerleme, ayarlar, sonuçlar ve günlük |
| `POST /api/start` | Yeni hesaplama başlatır |
| `POST /api/stop` | Durdurma işaretini ayarlar |
| `GET /export.csv` | Sonuç tablosunu indirir |
| `GET /export.json` | Ayarlar dahil çalışma kaydını indirir |

Sunucu yalnızca önceden tanımlı arayüz dosyalarını servis eder; proje klasörünü genel dosya sunucusu olarak açmaz. Host başlığını kontrol eder. Değişiklik yapan isteklerde sayfaya özgü `X-App-Token` gerekir. Bu, internet kullanıcılarına açık bir kimlik doğrulama sistemi değildir; uygulama yerel kullanım içindir.

## 10. Ekran neden hesaplama sırasında donmaz

`Simulation.start()` ayarları doğrular ve hesaplamayı ayrı bir `threading.Thread` içinde başlatır. HTTP sunucusu bu sırada durum isteklerine cevap vermeye devam eder. `threading.Lock`, paylaşılan durumun hesaplama ve okuma sırasında tutarlı kalmasını sağlar.

JavaScript yaklaşık 400 milisaniyede bir `/api/state` adresini sorgular. Grafikler yalnızca sonuç grupları değiştiğinde yeniden çizilir. Çalıştırma günlüğü ve ilerleme her tamamlanan tekrarda güncellenir. Bu tasarım her rastgele noktada ekran çizmenin maliyetini önler.

`threading.Event` durdurma sinyalini taşır. Algoritmalar her 1.000 nokta veya toplama deneyinde sinyali kontrol eder. Ayrıca her tekrar öncesi ve tamamlanan grup sonrası kontrol yapılır. Durdurma anlık bir zorla süreç sonlandırma değildir; güvenli kontrol noktasında uygulanır.

## 11. CSS ve grafikler

Tkinter CSS yorumlamadığı için bu sürüm tarayıcı tabanlı yerel arayüz kullanır. DengeX'in iki gerçek CSS dosyası `assets/vendor` içinde yerel olarak tutulur. Form, sitedeki `dx-lead-form` sınıfını kullanır. `app.css`, deney ekranına özgü yerleşimi, mavi vurguları, yazı boyutlarını ve mobil düzeni ekler.

Arayüz açıldığında DengeX'e analiz verisi gönderilmez. Stil dosyaları ve Plotly yerelden yüklenir. DengeX bağlantısı kullanıcı tıklarsa dış siteyi açar. Kaynaklar `assets/vendor/SOURCES.md` içinde kayıtlıdır.

Plotly etkileşimli grafiklerin çiziminden sorumludur. Sol grafik tahminleri, ortalamayı ve teorik çizgiyi gösterir. Sağ grafik mutlak hata ile örneklem standart sapmasını karşılaştırır. Matplotlib ise `--no-gui` modundaki PNG/SVG çıktıları üretir.

## 12. Sınırlar ve testler

Arayüz 1–8 farklı n, her n için 1–1.000.000 örnek ve 2–50 tekrar kabul eder. Büyük değerler daha uzun sürebilir. Bu sınırlar, yanlışlıkla sınırsız iş başlatmayı azaltır.

```bash
.venv/bin/python -m unittest -v test_simulation.py
```

Testler varsayılan 40 tahminin tekrar üretimini, başlangıç koşullarını, giriş doğrulamayı ve iptal davranışını kontrol eder. Görünüm ayrıca tarayıcıda incelenir.

Daha büyük n genellikle daha kararlı tahminler sağlar. Ancak teorik değere uzaklığın her adımda azalması zorunlu değildir. Monte Carlo standart hatası tipik olarak 1/√n ile azalır. Bu yüzden hatayı yarıya indirmek yaklaşık dört kat örnek gerektirir.

## 13. GitHub kapsamı

Depoda kod, arayüz dosyaları, bağımlılık listesi, testler ve bu rehber bulunur. Sanal ortam, geçici dosyalar, yerel çıktı görselleri ve Word/PDF raporları `.gitignore` ile dışarıda tutulur. Bunlar kodu çalıştırmak için gerekli değildir.
