# Paketi açınca

1. ZIP dosyasının tamamını bir klasöre çıkar.
2. macOS Apple Silicon üzerinde `Monte Carlo.command` dosyasını aç veya terminalden `./bin/monte-carlo-studio` çalıştır.
3. Word belgesi: `docs/Proje Kapsamı.docx`.
4. Ayrıntılı anlatım: `read.md`. Kütüphaneler: `docs/Kutuphaneler.md`.

Hazır program macOS ARM64 içindir. Diğer sistemlerde Go 1.24+ ile kaynak koddan derle. Python başlatıcı isteğe bağlıdır: `python3 odev.py`.

Çalışma zamanı kütüphaneleri assets altında ve hazır programın içinde bulunur. İnternet veya npm kurulumu çalıştırma için gerekmez. Ön yüzü yeniden derlemek için Node.js ve `npm ci`, ardından `npm run build` gerekir. Go derlemesi: `go build -trimpath -o bin/monte-carlo-studio .`

Bu paket AI yardımıyla geliştirilmiş öğrenme uygulamasını içerir. Eski Python raporları ve ders PDF’si dahil değildir. Deney sonuçları uygulamadan CSV/JSON olarak indirilebilir.
