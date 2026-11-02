#!/usr/bin/env bash
# TC-INST-01: Projenin temiz bir kopyasını temiz sanal ortamda kurar ve CI adımlarının
# yerel eşdeğerini koşar. Sonuç (BAŞARILI/BAŞARISIZ) günlüğün son satırındadır.
#
# Kullanım: bash tools/install_check.sh <python-yorumlayıcı> <etiket> <günlük-dosyası> [kaynak-klasör]
# Örnek:    bash tools/install_check.sh python3.13 linux-py313 reports/install-check-linux-py313.log
set -uo pipefail
PY="$1"; LABEL="$2"; LOG="$3"; SRC="$(cd "${4:-.}" && pwd)"
WORK="$(mktemp -d)"
STATUS=0
{
  echo "== TC-INST-01 [$LABEL] başlangıç (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "== kaynak: $(basename "$(dirname "$SRC")")/$(basename "$SRC") (venv, db, reports hariç) -> geçici klasör"
  (cd "$SRC" && tar --exclude=.venv --exclude=reports --exclude=db.sqlite3 --exclude='__pycache__' --exclude=.ruff_cache -cf - .) | (cd "$WORK" && tar -xf -)
  cd "$WORK"
  echo "== $("$PY" --version)"
  "$PY" -m venv .venv || STATUS=1
  . .venv/bin/activate
  python -m pip install -q --upgrade pip || STATUS=1
  echo "== pip install -r requirements-dev.txt"
  pip install -q -r requirements-dev.txt || STATUS=1
  pip freeze
  echo "== ruff format --check / ruff check"
  ruff format --check . || STATUS=1
  ruff check . || STATUS=1
  echo "== manage.py check / makemigrations --check"
  python manage.py check || STATUS=1
  python manage.py makemigrations --check --dry-run || STATUS=1
  echo "== migrate (temiz veritabanı)"
  python manage.py migrate -v 1 || STATUS=1
  echo "== test + coverage"
  coverage run manage.py test --results-json reports/unit-results.json || STATUS=1
  coverage report | tail -3
  echo "== check --deploy (üretim profili)"
  DJANGO_ENV=production DJANGO_ALLOWED_HOSTS=sds07.example \
    DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')" \
    python manage.py check --deploy --fail-level WARNING || STATUS=1
  echo "== bitiş (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ) | durum: $([ $STATUS -eq 0 ] && echo BAŞARILI || echo BAŞARISIZ)"
} > "$LOG" 2>&1
rm -rf "$WORK"
exit $STATUS
