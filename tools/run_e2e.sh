#!/usr/bin/env bash
# E2E koşusu (Linux/macOS/CI). Windows adımları için docs/INSTALL.md'ye bakın.
#
# 1) Port boş mu? (Eski bir sunucu açık kalırsa testler eski kodla koşar; Hafta 2'de yaşandı, RSK-08.)
# 2) Geçici veritabanı + migrate + rastgele parolayla demo kullanıcılar
# 3) Sunucuyu başlat, hazır olmasını bekle, E2E betiğini koş
# 4) Sunucuyu kapat ve portun boşaldığını doğrula
set -euo pipefail

PORT="${E2E_PORT:-8765}"
PYTHON="${PYTHON:-python}"
# Playwright başka bir ortamda kuruluysa E2E betiği için ayrı yorumlayıcı verilebilir.
E2E_PYTHON="${E2E_PYTHON:-$PYTHON}"
OUT_DIR="${E2E_OUT_DIR:-reports/screenshots}"
RESULTS="${E2E_RESULTS:-reports/e2e-results.json}"
TMP_DIR="$(mktemp -d)"
export DJANGO_SQLITE_PATH="$TMP_DIR/e2e.sqlite3"
export E2E_PASSWORD="E2e-$("$PYTHON" -c 'import secrets; print(secrets.token_urlsafe(12))')"

port_in_use() { "$PYTHON" -c "import socket,sys; s=socket.socket(); sys.exit(0 if s.connect_ex(('127.0.0.1', $PORT))==0 else 1)"; }

if port_in_use; then
  echo "HATA: $PORT portu kullanımda. Eski sunucuyu kapatın (eski kodla test riski)." >&2
  exit 3
fi

"$PYTHON" manage.py migrate -v 0
"$PYTHON" manage.py seed_demo_users --password "$E2E_PASSWORD" > /dev/null

"$PYTHON" manage.py runserver "127.0.0.1:$PORT" --noreload > "$TMP_DIR/server.log" 2>&1 &
SERVER_PID=$!
cleanup() {
  kill "$SERVER_PID" 2> /dev/null || true
  wait "$SERVER_PID" 2> /dev/null || true
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

for _ in $(seq 1 60); do
  port_in_use && break
  sleep 0.5
done
port_in_use || { echo "HATA: sunucu başlamadı"; cat "$TMP_DIR/server.log"; exit 4; }

set +e
"$E2E_PYTHON" e2e/week2_auth_roles.py --base-url "http://127.0.0.1:$PORT" --out-dir "$OUT_DIR" --results-json "$RESULTS"
STATUS=$?
set -e

cleanup
trap - EXIT
if port_in_use; then
  echo "UYARI: koşu sonrası $PORT portu hâlâ açık." >&2
  exit 5
fi
exit "$STATUS"
