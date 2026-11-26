#!/usr/bin/env python3
"""RTM ve test sonuç tablosunu GERÇEK test çıktılarından üretir.

Girdi:
  docs/traceability/requirements.csv  gereksinim -> modül -> test eşlemesi (hafta ve sprint planı)
  docs/traceability/tests.csv         test kataloğu (seviye, ön koşul, beklenen çıktı, hafta)
  --results  JSON dosyaları            config/test_runner.py, e2e/*.py ve elle yapılan
                                       kontrol kayıtları (manual-checks.json)
  --coverage reports/coverage.json     TC-QA-01 (kapsam eşiği)
  --ruff     reports/ruff.json         TC-QA-02 (statik analiz bulgusu)
  --week N                             aktif hafta: N'den sonraki haftalara planlananlar PLANLANDI olur

Çıktı:
  docs/RTM.md, docs/TEST_RESULTS.md

Kural: Sonucu olmayan test "NOT RUN" yazılır; tahmini sonuç üretilmez.
--strict: izlenemeyen test, testsiz aktif gereksinim veya FAIL/ERROR varsa çıkış kodu 1.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ISTANBUL = ZoneInfo("Europe/Istanbul")
FAILING = {"FAIL", "ERROR", "UNEXPECTED_SUCCESS"}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(handle)]


def split_ids(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[;,]", value) if item.strip()]


def first_number(value: str) -> int:
    """'4-5' veya '11-12' gibi değerlerin ilk sayısı (planın başladığı hafta)."""
    match = re.search(r"\d+", value)
    return int(match.group()) if match else 99


def to_istanbul(iso_utc: str | None) -> str:
    if not iso_utc:
        return "-"
    moment = datetime.fromisoformat(iso_utc)
    return moment.astimezone(ISTANBUL).strftime("%d.%m.%Y %H:%M")


def read_json(path: Path):
    """JSON okur. utf-8-sig: Windows PowerShell'in eklediği BOM'u da kabul eder."""
    text = path.read_text(encoding="utf-8-sig").strip()
    return json.loads(text) if text else None


def load_results(paths: list[Path]) -> tuple[dict, list[dict], list[str]]:
    """TC kimliği -> sonuç listesi; çalıştırma bilgileri; kimliksiz testler."""
    outcomes: dict[str, list[dict]] = {}
    runs: list[dict] = []
    unidentified: list[str] = []
    for path in paths:
        if not path.exists():
            runs.append({"source": path.as_posix(), "missing": True})
            continue
        payload = read_json(path) or {}
        runs.append(
            {
                "source": path.as_posix(),
                "kind": payload.get("kind", "?"),
                "started": payload.get("started_at_utc"),
                "finished": payload.get("finished_at_utc"),
                "environment": payload.get("environment", {}),
                "totals": payload.get("totals", {}),
            }
        )
        for record in payload.get("results", []):
            tc_id = record.get("tc_id")
            if not tc_id:
                unidentified.append(f"{path.name}: {record.get('test', '?')}")
                continue
            outcomes.setdefault(tc_id, []).append({**record, "source": path.name})
    return outcomes, runs, unidentified


def add_metric_results(outcomes: dict, coverage_path: Path | None, ruff_path: Path | None, threshold: float):
    metrics = {}
    if coverage_path and coverage_path.exists():
        totals = read_json(coverage_path)["totals"]
        percent = round(totals["percent_covered"], 2)
        metrics["coverage_percent"] = percent
        outcomes.setdefault("TC-QA-01", []).append(
            {
                "outcome": "PASS" if percent >= threshold else "FAIL",
                "detail": f"Kapsam %{percent} (eşik %{threshold})",
                "source": coverage_path.name,
            }
        )
    if ruff_path and ruff_path.exists():
        findings = read_json(ruff_path) or []
        metrics["ruff_findings"] = len(findings)
        outcomes.setdefault("TC-QA-02", []).append(
            {
                "outcome": "PASS" if not findings else "FAIL",
                "detail": f"{len(findings)} bulgu",
                "source": ruff_path.name,
            }
        )
    return metrics


def merge_outcome(records: list[dict]) -> str:
    values = {r["outcome"] for r in records}
    if values & FAILING:
        return "FAIL"
    if "PASS" in values:
        return "PASS"
    if "SKIP" in values:
        return "SKIP"
    return "NOT RUN"


def requirement_status(req: dict, tc_status: dict, current_week: int) -> str:
    tests = split_ids(req["tests"])
    if first_number(req["week"]) > current_week:
        return f"PLANLANDI (Hafta {req['week']})"
    if not tests:
        return "TEST TANIMSIZ"
    statuses = [tc_status.get(t, "NOT RUN") for t in tests]
    if any(s == "FAIL" for s in statuses):
        return "FAIL"
    passed = sum(s == "PASS" for s in statuses)
    if passed == len(statuses):
        return "PASS"
    if passed:
        return f"KISMİ ({passed}/{len(statuses)} PASS; diğerleri NOT RUN)"
    return "NOT RUN"


def md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def consistency_problems(requirements, catalog, outcomes, unidentified, tc_status, week) -> list[str]:
    problems: list[str] = []
    req_ids = {r["id"] for r in requirements}
    for req in requirements:
        for tc_id in split_ids(req["tests"]):
            if tc_id not in catalog:
                problems.append(f"{req['id']} katalogda olmayan teste bağlı: {tc_id}")
        if first_number(req["week"]) <= week and not split_ids(req["tests"]):
            problems.append(f"{req['id']} aktif haftada ama test tanımı yok")
    for tc_id, row in catalog.items():
        for req_id in split_ids(row["requirements"]):
            if req_id not in req_ids:
                problems.append(f"{tc_id} bilinmeyen gereksinime bağlı: {req_id}")
    for tc_id in outcomes:
        if tc_id not in catalog:
            problems.append(f"İzlenemeyen test sonucu (katalogda yok): {tc_id}")
    problems.extend(f"TC kimliği olmayan test: {name}" for name in unidentified)
    problems.extend(f"Başarısız test: {t}" for t in sorted(t for t, s in tc_status.items() if s == "FAIL"))
    return problems


def run_table(runs: list[dict], metrics: dict) -> list[str]:
    lines = ["| Kaynak | Tür | Başlangıç (İstanbul) | Ortam | Özet |", "|---|---|---|---|---|"]
    for run in runs:
        if run.get("missing"):
            lines.append(f"| `{run['source']}` | - | - | - | DOSYA YOK (NOT RUN) |")
            continue
        env = run["environment"]
        env_text = ", ".join(f"{k} {v}" for k, v in env.items() if k in {"python", "django", "browser", "platform"})
        totals = ", ".join(f"{k}={v}" for k, v in run["totals"].items())
        lines.append(
            f"| `{run['source']}` | {run['kind']} | {to_istanbul(run['started'])} | {md_escape(env_text)} | {totals} |"
        )
    lines += [f"| ölçüm | {name} | - | - | {value} |" for name, value in metrics.items()]
    return lines


def count_by_status(statuses) -> dict[str, int]:
    """Durumları sayar. Parantezli ayrıntı atılır: 'PLANLANDI (Hafta 3)' -> 'PLANLANDI'.
    'NOT RUN' gibi iki sözcüklü durum adı bölünmez (Hafta 1'de 'NOT' olarak sayılıyordu, RSK-06)."""
    counts: dict[str, int] = {}
    for status in statuses:
        key = status.split(" (")[0]
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--requirements", type=Path, default=Path("docs/traceability/requirements.csv"))
    parser.add_argument("--tests", type=Path, default=Path("docs/traceability/tests.csv"))
    parser.add_argument("--results", type=Path, nargs="*", default=[])
    parser.add_argument("--coverage", type=Path)
    parser.add_argument("--ruff", type=Path)
    parser.add_argument("--coverage-threshold", type=float, default=80.0)
    parser.add_argument("--week", type=int, required=True, help="Aktif proje haftası (1-14)")
    parser.add_argument("--rtm-out", type=Path, default=Path("docs/RTM.md"))
    parser.add_argument("--results-out", type=Path, default=Path("docs/TEST_RESULTS.md"))
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    requirements = read_csv(args.requirements)
    catalog = {row["id"]: row for row in read_csv(args.tests)}
    outcomes, runs, unidentified = load_results(args.results)
    metrics = add_metric_results(outcomes, args.coverage, args.ruff, args.coverage_threshold)

    tc_status = {
        tc_id: ("PLANLANDI" if first_number(row["week"]) > args.week else merge_outcome(outcomes.get(tc_id, [])))
        for tc_id, row in catalog.items()
    }
    problems = consistency_problems(requirements, catalog, outcomes, unidentified, tc_status, args.week)
    req_statuses = {r["id"]: requirement_status(r, tc_status, args.week) for r in requirements}
    generated = datetime.now(ISTANBUL).strftime("%d.%m.%Y %H:%M")
    runs_md = run_table(runs, metrics)
    header = f"> Üretim: {generated} (Europe/Istanbul) · Aktif hafta: {args.week}"

    # --- RTM
    rtm = [
        "# Gereksinim İzlenebilirlik Matrisi (RTM)",
        "",
        "> Bu dosya `tools/build_rtm.py` tarafından gerçek test çıktılarından üretilir; elle düzenlemeyin.",
        "> Kaynaklar: `docs/traceability/requirements.csv`, `docs/traceability/tests.csv` ve aşağıdaki sonuç dosyaları.",
        header,
        "",
        "## Çalıştırma kayıtları",
        "",
        *runs_md,
        "",
        "## Gereksinim → mimari bileşen → test → gerçek sonuç",
        "",
        "| ID | Tip | Gereksinim (kısa) | Öncelik | Kaynak | Mimari bileşen (SDD) | Doğrulama yöntemi | Test ID (STD) | Hafta | Gerçek sonuç |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for req in requirements:
        tests = split_ids(req["tests"])
        test_cells = ", ".join(f"{t} ({tc_status.get(t, '?')})" for t in tests) or "-"
        rtm.append(
            f"| {req['id']} | {req['type']} | {md_escape(req['title'])} | {req['priority']} | {md_escape(req['source'])} | "
            f"{md_escape(req['modules'])} | {req['verification']} | {test_cells} | {req['week']} | {req_statuses[req['id']]} |"
        )
    counts = count_by_status(req_statuses.values())
    rtm += [
        "",
        "## Özet",
        "",
        "| Durum | Gereksinim sayısı |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in counts.items()],
        "",
        "## Standart eşlemesi (bilgi amaçlı)",
        "",
        "| ID | ISO 9001:2026 maddesi | ISO/IEC 25010:2023 karakteristiği / alt karakteristiği |",
        "|---|---|---|",
        *[f"| {r['id']} | {r['iso9001_2026']} | {r['iso25010_2023']} |" for r in requirements],
        "",
        "Madde numaralarının doğrulama durumu için `docs/STANDARDS.md` dosyasına bakın.",
        "",
        "## Tutarlılık denetimi",
        "",
    ]
    rtm += (
        [f"- {p}" for p in problems]
        if problems
        else ["- Sorun bulunmadı (izlenemeyen test, testsiz aktif gereksinim veya başarısız test yok)."]
    )
    args.rtm_out.write_text("\n".join(rtm) + "\n", encoding="utf-8")

    # --- Test sonuçları (final şablonu 4.2 sütunları)
    results = [
        "# Doğrulama ve Geçerleme Test Sonuçları",
        "",
        "> Bu dosya `tools/build_rtm.py` tarafından üretilir. Sonuçlar yalnız gerçek çalıştırma kayıtlarından gelir.",
        header,
        "",
        *runs_md,
        "",
        "| Test ID | Doğrulanan gereksinim | Test seviyesi | Ön koşul ve test girdisi | Beklenen çıktı | Hafta | Sonuç | Kanıt |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for tc_id, row in catalog.items():
        records = outcomes.get(tc_id, [])
        detail = "; ".join(sorted({r.get("source", "") for r in records})) or row["automation"]
        note = next((r.get("detail") for r in records if r.get("detail") and r["outcome"] == "PASS"), "")
        evidence = md_escape(detail + (f" ({note})" if note and len(note) < 80 else ""))
        results.append(
            f"| {tc_id} | {row['requirements']} | {row['level']} | {md_escape(row['precondition_input'])} | "
            f"{md_escape(row['expected'])} | {row['week']} | **{tc_status[tc_id]}** | {evidence} |"
        )
    summary = count_by_status(tc_status.values())
    results += ["", "| Sonuç | Test sayısı |", "|---|---|", *[f"| {k} | {v} |" for k, v in summary.items()]]
    args.results_out.write_text("\n".join(results) + "\n", encoding="utf-8")

    print(f"RTM yazıldı: {args.rtm_out} | Test sonuçları: {args.results_out}")
    print("Gereksinim durumları:", counts)
    print("Test durumları:", summary)
    for problem in problems:
        print("UYARI:", problem)
    return 1 if (args.strict and problems) else 0


if __name__ == "__main__":
    sys.exit(main())
