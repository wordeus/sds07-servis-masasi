#!/usr/bin/env bash
# Windows'un konsol dışı (yönlendirilmiş/borulu) çıktı kodlamasını Linux'ta taklit eder.
# Kullanım: win_encoding_sim.sh <paket-klasörü> <hafta> <PYTHONIOENCODING değeri>
set -u
PKG="$1"; WEEK="$2"; ENC="$3"
PY=/home/claude/sds07-servis-masasi/.venv/bin/python
WORK="$(mktemp -d)"
cp -r "$PKG/." "$WORK/"
cd "$WORK"
rm -rf reports db.sqlite3 && mkdir -p reports
EV="docs/evidence/hafta-0$WEEK"
echo "### Paket: $(basename "$PKG") (Hafta $WEEK) | PYTHONIOENCODING=$ENC | $(date -u +%Y-%m-%dT%H:%M:%SZ) | Python $($PY -c 'import platform;print(platform.python_version())')"
echo "\$ python manage.py test -v 2 --results-json reports/unit-results.json"
PYTHONIOENCODING="$ENC" "$PY" manage.py test -v 2 --results-json reports/unit-results.json > out-test.txt 2>&1
echo "çıkış kodu: $?"
if grep -q "UnicodeEncodeError" out-test.txt; then
  grep -B2 -A0 "sys.stdout.write\|print(" out-test.txt | grep -v "^--$" | sed 's/^/    /' | head -6
  grep "UnicodeEncodeError" out-test.txt | sed 's/^/    /' | head -2
else
  grep -E "^Ran [0-9]+ tests|^OK|^FAILED" out-test.txt | sed 's/^/    /'
fi
echo "\$ python tools/build_rtm.py --week $WEEK --strict --results $EV/unit-results.json --coverage $EV/coverage.json --ruff $EV/ruff.json --rtm-out reports/RTM.md --results-out reports/TEST_RESULTS.md"
PYTHONIOENCODING="$ENC" "$PY" tools/build_rtm.py --week "$WEEK" --strict --results "$EV/unit-results.json" \
  --coverage "$EV/coverage.json" --ruff "$EV/ruff.json" --rtm-out reports/RTM.md --results-out reports/TEST_RESULTS.md > out-rtm.txt 2>&1
echo "çıkış kodu: $?"
if grep -q "UnicodeEncodeError" out-rtm.txt; then
  grep -B1 "print(" out-rtm.txt | grep -v "^--$" | sed 's/^/    /' | head -3
  grep "UnicodeEncodeError" out-rtm.txt | sed 's/^/    /' | head -2
else
  sed 's/^/    /' out-rtm.txt | head -4
fi
echo
cd / && rm -rf "$WORK"
