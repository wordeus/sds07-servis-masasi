#!/usr/bin/env bash
# TC-CI-01: Bir GitHub Actions CI koşusunun sonucunu GitHub API'den okuyup kanıt dosyası yazar.
# Çıktı biçimi docs/evidence/hafta-0N/ci-github-actions-YYYY-MM-DD.json (Hafta 1-3 ile aynı).
# Sonuç API'deki gerçek değerdir; koşu bitmemişse dosya yazılmaz (PRC-05).
#
# Gereksinim: gh (oturum açık), jq yerine gh'nin yerleşik --jq seçeneği kullanılır.
# Kullanım: bash tools/record_ci_run.sh <hafta> [commit]
# Örnek:    bash tools/record_ci_run.sh 4            # main'deki son commit'in push koşusu
#           bash tools/record_ci_run.sh 3 aa17057
set -euo pipefail
WEEK="${1:?Kullanım: record_ci_run.sh <hafta> [commit]}"
COMMIT="${2:-$(git rev-parse origin/main)}"
COMMIT="$(git rev-parse "$COMMIT")"
REPO="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
NN="$(printf '%02d' "$WEEK")"

RUN_ID="$(gh api "repos/$REPO/actions/workflows/ci.yml/runs?head_sha=$COMMIT&event=push&per_page=1" \
  --jq '.workflow_runs[0].id // empty')"
[ -n "$RUN_ID" ] || { echo "Bu commit için push koşusu yok: $COMMIT" >&2; exit 1; }

STATUS="$(gh api "repos/$REPO/actions/runs/$RUN_ID" --jq .status)"
[ "$STATUS" = "completed" ] || { echo "Koşu henüz bitmedi (durum: $STATUS). Bitince tekrar çalıştırın." >&2; exit 2; }

ARTIFACTS="$(gh api "repos/$REPO/actions/runs/$RUN_ID/artifacts" --jq .total_count)"
# gh --jq girdi olarak yalnız API yanıtını kabul ettiği için alanlar tek tek okunur.
RUN_NUMBER="$(gh api "repos/$REPO/actions/runs/$RUN_ID" --jq .run_number)"
STARTED="$(gh api "repos/$REPO/actions/runs/$RUN_ID" --jq .run_started_at)"
FINISHED="$(gh api "repos/$REPO/actions/runs/$RUN_ID" --jq .updated_at)"
CONCLUSION="$(gh api "repos/$REPO/actions/runs/$RUN_ID" --jq .conclusion)"
URL="$(gh api "repos/$REPO/actions/runs/$RUN_ID" --jq .html_url)"
JOBS_TOTAL="$(gh api "repos/$REPO/actions/runs/$RUN_ID/jobs?per_page=50" --jq '.jobs | length')"
JOBS_PASSED="$(gh api "repos/$REPO/actions/runs/$RUN_ID/jobs?per_page=50" --jq '[.jobs[] | select(.conclusion=="success")] | length')"
JOB_LINES="$(gh api "repos/$REPO/actions/runs/$RUN_ID/jobs?per_page=50" \
  --jq '[.jobs[] | "\(.name) \((.completed_at|fromdate) - (.started_at|fromdate)) sn \(.conclusion)"] | join(", ")')"

SHORT="${COMMIT:0:7}"
TAG="$(git tag --points-at "$COMMIT" | head -1)"
REF="${TAG:+etiket $TAG, }main"
OUTCOME=PASS; FAILURES=0
if [ "$CONCLUSION" != "success" ] || [ "$JOBS_PASSED" != "$JOBS_TOTAL" ]; then
  OUTCOME=FAIL; FAILURES=$((JOBS_TOTAL - JOBS_PASSED))
fi
DAY="$(printf '%s' "$STARTED" | cut -c1-10)"
OUT="docs/evidence/hafta-$NN/ci-github-actions-$DAY.json"
mkdir -p "$(dirname "$OUT")"
[ ! -e "$OUT" ] || { echo "Kanıt dosyası zaten var, değiştirilmez: $OUT" >&2; exit 3; }

cat > "$OUT" <<EOF
{
  "kind": "github-actions",
  "started_at_utc": "${STARTED%Z}+00:00",
  "finished_at_utc": "${FINISHED%Z}+00:00",
  "recorded_at_utc": "$(date -u +%Y-%m-%dT%H:%M:%S)+00:00",
  "environment": {
    "platform": "GitHub Actions: ubuntu-latest ve windows-latest, Python 3.12 ve 3.13",
    "workflow": ".github/workflows/ci.yml",
    "run_url": "$URL",
    "commit": "$SHORT ($REF)",
    "source": "GitHub REST API (actions/runs/$RUN_ID, /jobs, /artifacts); tools/record_ci_run.sh ile okundu."
  },
  "totals": {
    "run": 1,
    "failures": $FAILURES,
    "jobs_passed": $JOBS_PASSED,
    "jobs_total": $JOBS_TOTAL
  },
  "results": [
    {
      "tc_id": "TC-CI-01",
      "test": "GitHub Actions matrisi (ubuntu/windows × Python 3.12/3.13)",
      "outcome": "$OUTCOME",
      "detail": "Koşu #$RUN_NUMBER (push, main, commit $SHORT): $JOB_LINES; sonuç $CONCLUSION; $ARTIFACTS rapor arşivi (artifact) üretildi."
    }
  ]
}
EOF
echo "Yazıldı: $OUT ($OUTCOME, $JOBS_PASSED/$JOBS_TOTAL iş)"
