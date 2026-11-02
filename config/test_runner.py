"""
İzlenebilir test koşucusu (V&V desteği, IEEE 1012-2024 ile ilişkili).

Django'nun DiscoverRunner sınıfını genişletir. `--results-json YOL` verilirse
her testin sonucunu, test metodunun belge dizesinin (docstring) ilk satırındaki
TC kimliğiyle birlikte JSON dosyasına yazar. Bu dosya, RTM'deki "gerçek sonuç"
sütununun tek kaynağıdır (bkz. tools/build_rtm.py). Elle sonuç yazılmaz.

Kullanım:
    python manage.py test --results-json reports/unit-results.json
"""

from __future__ import annotations

import json
import platform
import re
import sys
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path

import django
from django.test.runner import DiscoverRunner

TC_PATTERN = re.compile(r"\b(TC-[A-Z0-9]+-\d{2,3})\b")


def extract_tc_id(test) -> str | None:
    """Test metodunun docstring'inin ilk satırından TC kimliğini çıkarır."""
    doc = getattr(test, "_testMethodDoc", None) or ""
    first_line = doc.strip().splitlines()[0] if doc.strip() else ""
    match = TC_PATTERN.search(first_line)
    return match.group(1) if match else None


class RecordingTextTestResult(unittest.TextTestResult):
    """Standart sonuç sınıfı; ek olarak her testin sonucunu kaydeder."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records: list[dict] = []
        self._started: dict[str, float] = {}
        self._failed_ids: set[str] = set()

    def startTest(self, test):
        self._started[test.id()] = time.perf_counter()
        super().startTest(test)

    def _record(self, test, outcome: str, detail: str = "") -> None:
        started = self._started.pop(test.id(), None)
        duration = round(time.perf_counter() - started, 4) if started else None
        doc = getattr(test, "_testMethodDoc", None) or ""
        self.records.append(
            {
                "test": test.id(),
                "tc_id": extract_tc_id(test),
                "title": doc.strip().splitlines()[0] if doc.strip() else "",
                "outcome": outcome,
                "duration_s": duration,
                "detail": detail[-4000:],
            }
        )

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._failed_ids.add(test.id())
        self._record(test, "FAIL", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self._failed_ids.add(test.id())
        self._record(test, "ERROR", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, "SKIP", reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._record(test, "XFAIL", self._exc_info_to_string(err, test))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._failed_ids.add(test.id())
        self._record(test, "UNEXPECTED_SUCCESS")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        # Alt testlerden biri başarısızsa üst test için tek bir FAIL kaydı tutulur.
        if err is not None and test.id() not in self._failed_ids:
            self._failed_ids.add(test.id())
            self._record(test, "FAIL", f"{subtest}: {self._exc_info_to_string(err, test)}")


class TraceableDiscoverRunner(DiscoverRunner):
    """`--results-json` seçeneği ekleyen DiscoverRunner."""

    def __init__(self, results_json: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.results_json = results_json
        self._started_at = datetime.now(UTC)

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--results-json",
            default=None,
            help="Test sonuçlarını TC kimlikleriyle bu JSON dosyasına yaz.",
        )

    def get_resultclass(self):
        base = super().get_resultclass()
        if self.results_json and base is None:
            return RecordingTextTestResult
        return base

    def run_suite(self, suite, **kwargs):
        result = super().run_suite(suite, **kwargs)
        if self.results_json and isinstance(result, RecordingTextTestResult):
            self._write_results(result)
        return result

    def _write_results(self, result: RecordingTextTestResult) -> None:
        finished_at = datetime.now(UTC)
        payload = {
            "kind": "django-unit-integration",
            "started_at_utc": self._started_at.isoformat(timespec="seconds"),
            "finished_at_utc": finished_at.isoformat(timespec="seconds"),
            "environment": {
                "python": platform.python_version(),
                "django": django.get_version(),
                "platform": platform.platform(),
                "argv": sys.argv,
            },
            "totals": {
                "run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
                "skipped": len(result.skipped),
                "successful": result.wasSuccessful(),
            },
            "results": result.records,
        }
        path = Path(self.results_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
