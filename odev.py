import os
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    binary = root / "bin" / ("monte-carlo-studio.exe" if os.name == "nt" else "monte-carlo-studio")
    if not binary.is_file():
        sys.exit("Go uygulaması derlenmemiş. Proje klasöründe çalıştır: go build -o bin/monte-carlo-studio .")
    os.chdir(root)
    os.execv(str(binary), [str(binary), *sys.argv[1:]])


if __name__ == "__main__":
    main()
