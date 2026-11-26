"""Doğrulama altyapısının kendisinin testi (NFR-09).

RTM'deki "gerçek sonuç" sütunu config/test_runner.py çıktısına ve tools/build_rtm.py
hesaplarına dayanır. Bu nedenle koşucunun başarılı, başarısız, hatalı, atlanan ve alt
test başarısızlıklarını doğru kaydettiği, RTM üreticinin de durumları doğru hesaplayıp
saydığı ayrıca doğrulanır; yanlış "PASS" veya yanlış sayım izlenebilirliği bozar.
"""

import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from config.test_runner import RecordingTextTestResult, TraceableDiscoverRunner, extract_tc_id


def _make_sample_case():
    """Bilinçli olarak başarısız örnek testler. Fonksiyon içinde tanımlanır ki
    Django'nun test keşfi bunları gerçek test olarak çalıştırmasın."""

    class Sample(unittest.TestCase):
        def test_pass(self):
            """TC-DEMO-01: geçer"""

        def test_fail(self):
            """TC-DEMO-02: başarısız"""
            self.fail("beklenen başarısızlık")

        def test_error(self):
            """TC-DEMO-03: hata"""
            raise RuntimeError("beklenen hata")

        @unittest.skip("örnek atlama")
        def test_skip(self):
            """TC-DEMO-04: atlanır"""

        def test_subtest_fail(self):
            """TC-DEMO-05: alt test başarısız"""
            for value in (1, 2):
                with self.subTest(value=value):
                    self.assertEqual(value, 1)

        def test_without_id(self):
            """Kimliksiz test"""

    return Sample


class TraceableRunnerTests(SimpleTestCase):
    def test_runner_records_every_outcome(self):
        """TC-QA-03: Test koşucusu PASS, FAIL, ERROR, SKIP ve alt test başarısızlığını TC kimliğiyle doğru kaydeder."""
        sample = _make_sample_case()
        suite = unittest.TestLoader().loadTestsFromTestCase(sample)
        result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=RecordingTextTestResult).run(suite)
        outcomes = {r["tc_id"]: r["outcome"] for r in result.records}
        self.assertEqual(
            outcomes,
            {
                "TC-DEMO-01": "PASS",
                "TC-DEMO-02": "FAIL",
                "TC-DEMO-03": "ERROR",
                "TC-DEMO-04": "SKIP",
                "TC-DEMO-05": "FAIL",
                None: "PASS",
            },
        )
        self.assertEqual(sum(1 for r in result.records if r["tc_id"] == "TC-DEMO-05"), 1)
        failure = next(r for r in result.records if r["tc_id"] == "TC-DEMO-02")
        self.assertIn("beklenen başarısızlık", failure["detail"])
        self.assertIsNone(extract_tc_id(sample("test_without_id")))

        with tempfile.TemporaryDirectory() as tmp:
            runner = TraceableDiscoverRunner(results_json=str(Path(tmp) / "out.json"), verbosity=0)
            self.assertIs(runner.get_resultclass(), RecordingTextTestResult)
            runner._write_results(result)
            payload = json.loads((Path(tmp) / "out.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["totals"]["run"], 6)
        self.assertFalse(payload["totals"]["successful"])
        self.assertIsNone(TraceableDiscoverRunner(verbosity=0).get_resultclass())


def _load_rtm_builder():
    """tools/ bir Python paketi değildir; RTM üretici dosya yolundan yüklenir."""
    spec = importlib.util.spec_from_file_location("build_rtm", Path(settings.BASE_DIR) / "tools" / "build_rtm.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RtmBuilderTests(SimpleTestCase):
    def test_rtm_statuses_and_summary_counts(self):
        """TC-QA-04: RTM üretici gereksinim durumlarını doğru hesaplar ve özet tablosunda tam durum adlarıyla sayar."""
        rtm = _load_rtm_builder()
        tc_status = {"TC-A": "PASS", "TC-B": "NOT RUN", "TC-C": "FAIL", "TC-D": "PLANLANDI"}
        cases = [
            ({"tests": "TC-A", "week": "1"}, 1, "PASS"),
            ({"tests": "TC-A;TC-B", "week": "1"}, 1, "KISMİ (1/2 PASS; diğerleri NOT RUN)"),
            ({"tests": "TC-B", "week": "2"}, 2, "NOT RUN"),
            ({"tests": "TC-A;TC-C", "week": "1"}, 1, "FAIL"),
            ({"tests": "TC-D", "week": "4-5"}, 3, "PLANLANDI (Hafta 4-5)"),
            ({"tests": "", "week": "1"}, 1, "TEST TANIMSIZ"),
        ]
        for requirement, week, expected in cases:
            with self.subTest(requirement=requirement, week=week):
                self.assertEqual(rtm.requirement_status(requirement, tc_status, week), expected)
        self.assertEqual(rtm.merge_outcome([{"outcome": "PASS"}, {"outcome": "ERROR"}]), "FAIL")
        self.assertEqual(rtm.merge_outcome([]), "NOT RUN")
        counts = rtm.count_by_status(
            ["NOT RUN", "PASS", "PLANLANDI (Hafta 3)", "KISMİ (1/2 PASS; diğerleri NOT RUN)", "NOT RUN"]
        )
        self.assertEqual(counts, {"KISMİ": 1, "NOT RUN": 2, "PASS": 1, "PLANLANDI": 1})
        # Kaynak yolu her işletim sisteminde "/" ile yazılır (RSK-26; Windows'ta ters bölü çıkıyordu).
        _, runs, _ = rtm.load_results([Path("docs") / "evidence" / "yok.json"])
        self.assertEqual(runs[0]["source"], "docs/evidence/yok.json")
