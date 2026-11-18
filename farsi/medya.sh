#!/usr/bin/env bash
# Farsça sayfanın medya dosyalarını "medya-farsi" dalına yükler (dal her çalıştırmada ÜZERİNE YAZILIR).
# @emsalvarmi akışının "medya" dalına ve sablon/ klasörüne DOKUNMAZ.
# Kullanım (depo kökünden): farsi/medya.sh <klasör>...   → klasörlerin içindeki tüm .mp4/.jpg/.png dosyaları yüklenir.
# Her dosya için commit'e sabitlenmiş (önbellekten etkilenmeyen) bağlantıyı ve HTTP kodunu yazdırır.
# Planlamayı hemen ardından yapın: Metricool dosyaları kendi sunucusuna kopyalar.
set -euo pipefail
BR=medya-farsi
[ "$#" -gt 0 ] || { echo "Kullanım: $0 <klasör>..." >&2; exit 1; }
repo=$(git rev-parse --show-toplevel); tmp=$(mktemp -d)
git -C "$repo" worktree add -q --detach "$tmp"
(
  cd "$tmp"; git checkout -q --orphan "$BR-yerel-$$"; git rm -rfq . >/dev/null 2>&1 || true
  for d in "$@"; do
    case "$d" in /*) src="$d";; *) src="$OLDPWD/$d";; esac
    n=$(basename "$d"); mkdir -p "$n"
    find "$src" -maxdepth 1 -type f \( -name '*.mp4' -o -name '*.jpg' -o -name '*.png' \) -exec cp {} "$n/" \;
  done
  git add -A
  git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -q -m "medya-farsi: $(date +%F)" ${COMMIT_TRAILERS:+-m "$COMMIT_TRAILERS"}
  git push -q --force origin "HEAD:refs/heads/$BR"
  git rev-parse HEAD > "$tmp/.sha"
)
sha=$(cat "$tmp/.sha")
files=$(cd "$tmp" && git ls-files)
git -C "$repo" worktree remove --force "$tmp"; git -C "$repo" branch -D "$BR-yerel-$$" >/dev/null 2>&1 || true
sleep 4
for f in $files; do
  u="https://raw.githubusercontent.com/emsalvarmi/g-rseller/$sha/$f"
  echo "$u $(curl -s -o /dev/null -w '%{http_code}' -I "$u")"
done
