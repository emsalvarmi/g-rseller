#!/usr/bin/env bash
# ترکیه بدون تله üretim araçlarını kurar (her yeni oturumda bir kez). Kullanım: bash farsi/setup.sh
set -euo pipefail
CACHE="${FARSI_CACHE:-/tmp/farsi-cache}"
mkdir -p "$CACHE" && cd "$CACHE"
# sherpa-onnx 1.13.8: daha yeni sürümlerde Farsça ses boş dönüyor (espeak desteği kaldırıldı).
pip install -q --break-system-packages "sherpa-onnx==1.13.8" soundfile numpy pillow espeakng-loader phonemizer-fork playwright 2>&1 | grep -v WARNING || true
[ -d node_modules/vazirmatn ] || npm install --silent vazirmatn
if [ ! -d vits-piper-fa_IR-amir-medium ]; then
  curl -sSL -m 300 -o v.tar.bz2 "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-fa_IR-amir-medium.tar.bz2"
  tar xjf v.tar.bz2 && rm v.tar.bz2
fi
ls vits-piper-fa_IR-amir-medium/*.onnx node_modules/vazirmatn/fonts/ttf/Vazirmatn-Black.ttf >/dev/null
which ffmpeg >/dev/null
echo "Kurulum tamam: $CACHE"
