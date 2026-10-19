import os
import sys

from pathlib import Path

ortam_python = Path(__file__).resolve().parent / ".venv" / "bin" / "python"
if ortam_python.exists() and Path(sys.prefix).resolve() != ortam_python.parent.parent.resolve():
    os.execv(str(ortam_python), [str(ortam_python), str(Path(__file__).resolve()), *sys.argv[1:]])

import json
import math
import random
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


BOYUTLAR = [10, 100, 1000, 10000]
TEKRAR = 5
TOHUM = 20261019
IPTAL = None


def pi_tahmini(n, rng, detay=False):
    iceride = 0

    for i in range(1, n + 1):
        if i % 1000 == 0 and IPTAL is not None and IPTAL.is_set():
            raise InterruptedError("Simulation stopped")
        x = rng.random()
        y = rng.random()
        uzaklik_kare = x**2 + y**2
        durum = uzaklik_kare <= 1

        if durum:
            iceride += 1

        if detay:
            print(
                f"Nokta {i:2}: x={x:.5f}, y={y:.5f}, "
                f"x²+y²={uzaklik_kare:.5f} | "
                f"{'İçeride' if durum else 'Dışarıda'}"
            )

    tahmin = 4 * iceride / n

    if detay:
        print(f"İçerideki nokta sayısı: {iceride}")
        print(f"π tahmini = 4 × {iceride} / {n} = {tahmin:.5f}")

    return tahmin


def e_tahmini(n, rng, detay=False):
    toplam_sayac = 0

    for deney in range(1, n + 1):
        if deney % 1000 == 0 and IPTAL is not None and IPTAL.is_set():
            raise InterruptedError("Simulation stopped")
        toplam = 0.0
        sayac = 0

        if detay:
            print(f"\nDeney {deney}")

        while toplam <= 1:
            sayi = rng.random()
            toplam += sayi
            sayac += 1

            if detay:
                print(
                    f"  Adım {sayac}: sayı={sayi:.5f}, "
                    f"toplam={toplam:.5f}"
                )

        toplam_sayac += sayac

        if detay:
            print(f"  Toplam 1'i geçti. Kullanılan sayı adedi: {sayac}")

    tahmin = toplam_sayac / n

    if detay:
        print(f"\nSayaçların toplamı: {toplam_sayac}")
        print(f"e tahmini = {toplam_sayac} / {n} = {tahmin:.5f}")

    return tahmin


def tablo_yazdir(ad, satirlar):
    print(f"\n{ad.upper()} SONUÇ TABLOSU")
    basliklar = [
        "n", "Run 1", "Run 2", "Run 3", "Run 4", "Run 5",
        "Mean", "Reference", "Abs. error", "Std. dev."
    ]
    print(" | ".join(f"{baslik:>11}" for baslik in basliklar))
    print("-" * 137)

    for satir in satirlar:
        degerler = [str(satir["n"])]
        degerler += [f"{x:.5f}" for x in satir["runs"]]
        degerler += [
            f"{satir[alan]:.5f}"
            for alan in ["mean", "reference", "error", "sd"]
        ]
        print(" | ".join(f"{deger:>11}" for deger in degerler))


def grafik_stili():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "figure.facecolor": "#F5F7FC",
        "axes.facecolor": "#FFFFFF",
        "axes.edgecolor": "#DCE1EF",
        "axes.labelcolor": "#535C72",
        "text.color": "#191C29",
        "xtick.color": "#535C72",
        "ytick.color": "#535C72",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": "#E7EBF4",
        "grid.linewidth": 0.7,
        "legend.frameon": False,
        "svg.fonttype": "none",
    })


def eksen_duzenle(ax, boyutlar, baslik, etiket):
    ax.set_xscale("log")
    ax.set_xticks(boyutlar, [f"{n:,}" for n in boyutlar])
    ax.set_xlabel("Simulation size n · logarithmic scale", labelpad=10)
    ax.set_ylabel(etiket, labelpad=10)
    ax.set_title(baslik, loc="left", fontsize=13, fontweight="bold", pad=18)
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    ax.tick_params(length=0, pad=8)
    ax.margins(x=0.1)


def tahmin_ciz(ax, ad, satirlar):
    boyutlar = [r["n"] for r in satirlar]
    ortalamalar = [r["mean"] for r in satirlar]
    for tekrar in range(TEKRAR):
        ax.scatter(
            boyutlar, [r["runs"][tekrar] for r in satirlar],
            color="#A6B3FB", s=40, edgecolors="white", linewidths=0.6,
            zorder=3, label="Individual runs" if tekrar == 0 else None,
        )
    ax.plot(boyutlar, ortalamalar, "o-", color="#4058F5",
            linewidth=2.5, markersize=6, zorder=4, label=f"Mean of {TEKRAR} runs")
    ax.axhline(satirlar[0]["reference"], color="#D27645",
               linestyle=(0, (5, 4)), linewidth=1.6, label="Theoretical value")
    eksen_duzenle(ax, boyutlar,
                   "Pi estimates" if ad == "pi" else "Euler's number estimates",
                   "Estimated value")
    ax.legend(loc="best", fontsize=8)


def hata_ciz(ax, satirlar):
    boyutlar = [r["n"] for r in satirlar]
    ax.plot(boyutlar, [r["error"] for r in satirlar], "o-",
            color="#4058F5", linewidth=2.3, label="Absolute error of mean")
    ax.plot(boyutlar, [r["sd"] for r in satirlar], "s--",
            color="#16978F", linewidth=2, label=f"Sample SD across {TEKRAR} runs")
    ax.set_yscale("log")
    eksen_duzenle(ax, boyutlar, "Accuracy and stability", "Magnitude · logarithmic scale")
    ax.legend(loc="best", fontsize=8)


def grafik_olustur(ad, satirlar, klasor):
    grafik_stili()
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.8))
    fig.subplots_adjust(left=0.075, right=0.97, top=0.70, bottom=0.19, wspace=0.30)
    fig.text(0.075, 0.93, "MONTE CARLO SIMULATION", fontsize=10,
             color="#4058F5", fontweight="bold")
    fig.text(0.075, 0.84, "Estimating pi" if ad == "pi" else "Estimating Euler's number",
             fontsize=25, fontweight="bold")
    son = satirlar[-1]
    fig.text(0.97, 0.86, f"n = {son['n']:,} mean  {son['mean']:.5f}",
             ha="right", fontsize=13, color="#4058F5", fontweight="bold")
    tahmin_ciz(axes[0], ad, satirlar)
    hata_ciz(axes[1], satirlar)
    fig.text(0.075, 0.06,
             f"{TEKRAR} independent runs per sample size. Error need not decrease at every step.",
             fontsize=9, color="#535C72")
    for uzanti in ["png", "svg"]:
        dosya = klasor / f"{ad}_grafik.{uzanti}"
        fig.savefig(dosya, dpi=220)
        print(f"Grafik kaydedildi: {dosya}")
    plt.close(fig)


def gorsel_rapor(sonuclar, klasor):
    grafik_stili()
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.subplots_adjust(left=0.075, right=0.97, top=0.77, bottom=0.17,
                        wspace=0.30, hspace=0.62)
    fig.text(0.075, 0.95, "STOCHASTIC PROCESSES", fontsize=10,
             color="#4058F5", fontweight="bold")
    fig.text(0.075, 0.89, "Monte Carlo simulation", fontsize=30, fontweight="bold")
    fig.text(0.075, 0.845, "Pi and Euler's number · 4 sample sizes · 5 runs each",
             fontsize=13, color="#535C72")
    for i, (ad, satirlar) in enumerate(sonuclar.items()):
        tahmin_ciz(axes[i, 0], ad, satirlar)
        hata_ciz(axes[i, 1], satirlar)
    fig.text(0.075, 0.045,
             "Larger samples produced more stable estimates. Accuracy did not improve monotonically.\n"
             "All 40 estimates use seed 20261019. SD describes variation across five runs, not a confidence interval.",
             fontsize=9, color="#535C72", linespacing=1.7)
    for uzanti in ["png", "svg"]:
        dosya = klasor / f"gorsel_rapor.{uzanti}"
        fig.savefig(dosya, dpi=220)
        print(f"Görsel rapor kaydedildi: {dosya}")
    plt.close(fig)


def simulasyonu_calistir():
    rng = random.Random(TOHUM)
    klasor = Path(__file__).resolve().parent / "odev_ciktilari"
    klasor.mkdir(exist_ok=True)
    tum_sonuclar = {}
    deneyler = [
        ("pi", pi_tahmini, math.pi),
        ("e", e_tahmini, math.e),
    ]

    for ad, fonksiyon, referans in deneyler:
        print(f"\n{'=' * 65}\n{ad.upper()} TAHMİNİ")
        print(f"Teorik değer: {referans:.8f}")
        satirlar = []

        for n in BOYUTLAR:
            print(f"\nn = {n}")
            sonuclar = []

            for tekrar in range(TEKRAR):
                detay = n == 10 and tekrar == 0

                if detay:
                    print("\nİlk çalıştırmanın adımları:")

                sonuc = fonksiyon(n, rng, detay=detay)
                sonuclar.append(sonuc)
                print(f"Çalıştırma {tekrar + 1}: {sonuc:.5f}")

            ortalama = statistics.mean(sonuclar)
            hata = abs(ortalama - referans)
            sapma = statistics.stdev(sonuclar)
            print(f"Ortalama: {ortalama:.5f}")
            print(f"Mutlak hata: {hata:.5f}")
            print(f"Standart sapma: {sapma:.5f}")
            satirlar.append({
                "n": n,
                "runs": sonuclar,
                "mean": ortalama,
                "reference": referans,
                "error": hata,
                "sd": sapma,
            })

        tum_sonuclar[ad] = satirlar
        tablo_yazdir(ad, satirlar)
        grafik_olustur(ad, satirlar, klasor)

    gorsel_rapor(tum_sonuclar, klasor)
    dosya = klasor / "sonuclar.json"
    dosya.write_text(
        json.dumps(tum_sonuclar, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nTüm sonuçlar kaydedildi: {dosya}")
    return tum_sonuclar, klasor


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Monte Carlo Studio")
    parser.add_argument("--no-gui", action="store_true")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int, default=0)
    options = parser.parse_args()
    if options.no_gui:
        simulasyonu_calistir()
        return
    from web_app import launch
    launch(sys.modules[__name__], port=options.port, open_browser=not options.no_browser)


if __name__ == "__main__":
    main()
