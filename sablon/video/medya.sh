#!/usr/bin/env bash
# Videoları ana dalı (main) şişirmeden yayınlamak için tek bir "medya" dalı kullanılır.
# Her çalıştırmada dal, yalnızca o çalıştırmanın videolarını içeren tek bir commit ile ÜZERİNE YAZILIR (force push).
# Metricool, createScheduledPost sırasında dosyaları kendi sunucusuna (static.metricool.com) kopyaladığı için
# önceki çalıştırmanın bağlantılarının kırılması sorun değildir; eski videolar depoda birikmez.
# (Dal silme bu ortamda izinli değil; bu yüzden dal silinmez, üzerine yazılır.)
#
# Kullanım (depo kökünden):
#   sablon/video/medya.sh <klasör>...      # her klasörde reel.mp4 ve kapak.jpg olmalı
# Her video için iki herkese açık bağlantı yazdırır:
#   https://raw.githubusercontent.com/emsalvarmi/g-rseller/medya/<klasör-adı>/reel.mp4
#   https://raw.githubusercontent.com/emsalvarmi/g-rseller/medya/<klasör-adı>/kapak.jpg
# Planlamayı medya.sh'den hemen sonra yapın; başka bir çalıştırma dalın üzerine yazmadan önce
# Metricool'un yanıtındaki media adreslerinin static.metricool.com olduğunu kontrol edin.
# İsteğe bağlı: COMMIT_TRAILERS ortam değişkeni commit mesajının sonuna eklenir.
set -euo pipefail
BR=medya
[ "$#" -gt 0 ] || { echo "Kullanım: $0 <klasör>..." >&2; exit 1; }
for d in "$@"; do
  [ -f "$d/reel.mp4" ] && [ -f "$d/kapak.jpg" ] || { echo "Eksik dosya: $d/reel.mp4 ya da $d/kapak.jpg" >&2; exit 1; }
done
repo=$(git rev-parse --show-toplevel)
tmp=$(mktemp -d)
git -C "$repo" worktree add -q --detach "$tmp"
(
  cd "$tmp"
  git checkout -q --orphan "$BR-yerel-$$"
  git rm -rfq . >/dev/null 2>&1 || true
  for d in "$@"; do
    n=$(basename "$d"); mkdir -p "$n"
    cp "$d/reel.mp4" "$d/kapak.jpg" "$n/"
  done
  git add -A
  git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -q -m "medya: $(date +%F)" ${COMMIT_TRAILERS:+-m "$COMMIT_TRAILERS"}
  if ! git push -q --force origin "HEAD:refs/heads/$BR" 2>push.err; then
    cat push.err >&2; echo "medya dalına push başarısız" >&2; exit 1
  fi
)
git -C "$repo" worktree remove --force "$tmp"
git -C "$repo" branch -D "$BR-yerel-$$" >/dev/null 2>&1 || true
sleep 3
for d in "$@"; do
  n=$(basename "$d")
  for f in reel.mp4 kapak.jpg; do
    u="https://raw.githubusercontent.com/emsalvarmi/g-rseller/$BR/$n/$f"
    code=$(curl -s -o /dev/null -w '%{http_code}' -I "$u")
    echo "$u $code"
  done
done
