#!/usr/bin/env python3
"""Hafta 2 tarayıcı (E2E) doğrulaması - TC-E2E-01..TC-E2E-09 (Hafta 3'te de gerileme olarak koşulur).

Çalışan bir sunucuya karşı Playwright (Chromium) kullanır.
Django birim/entegrasyon testlerinin tamamlayıcısıdır: gerçek tarayıcıda giriş, rol
menüsü, doğrudan adresle erişim (403), çıkış, mobil görünüm, klavye kullanımı ve
renk kontrastı doğrulanır. Sonuçlar TC kimlikleriyle JSON'a, ekran görüntüleri
klasöre yazılır. Kimlik bilgileri komut satırında değil ortam değişkeninde verilir.

Ön koşul: Sunucu çalışıyor ve `seed_demo_users` aynı parolayla çalıştırılmış olmalı.

Kullanım:
    set E2E_PASSWORD=...            (PowerShell: $env:E2E_PASSWORD="...")
    python e2e/week2_auth_roles.py --base-url http://127.0.0.1:8000 \
        --out-dir docs/evidence/hafta-02/screenshots --results-json reports/e2e-results.json
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import sys
import traceback
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

USERS = {"requester": "demo.talep", "agent": "demo.destek", "manager": "demo.yonetici"}
DESKTOP = {"width": 1440, "height": 900}
MOBILE = {"width": 360, "height": 740}

EFFECTIVE_COLORS_JS = """
(selector) => {
  const el = document.querySelector(selector);
  if (!el) return null;
  const bgOf = (node) => {
    while (node) {
      const c = getComputedStyle(node).backgroundColor;
      if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') return c;
      node = node.parentElement;
    }
    return 'rgb(255, 255, 255)';
  };
  return { fg: getComputedStyle(el).color, bg: bgOf(el) };
}
"""


def parse_rgb(value: str) -> tuple[float, float, float]:
    numbers = [float(n) for n in re.findall(r"[\d.]+", value)[:3]]
    return numbers[0], numbers[1], numbers[2]


def luminance(rgb: tuple[float, float, float]) -> float:
    def channel(c: float) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    high, low = sorted((luminance(parse_rgb(fg)), luminance(parse_rgb(bg))), reverse=True)
    return round((high + 0.05) / (low + 0.05), 2)


# Sayfa ve iç kapsayıcılar (tablo sarmalayıcısı, paneller) yatay taşmamalı (NFR-07).
OVERFLOW_JS = """
() => {
  const doc = document.documentElement;
  const inner = [...document.querySelectorAll('.table-responsive, .sd-panel, main, header')]
    .filter(el => el.scrollWidth > el.clientWidth + 1)
    .map(el => `${el.tagName.toLowerCase()}.${el.className} ${el.scrollWidth}>${el.clientWidth}`);
  return { page: [doc.scrollWidth, doc.clientWidth], inner };
}
"""


class Runner:
    def __init__(self, base_url: str, password: str, out_dir: Path, script: str = "e2e/week2_auth_roles.py"):
        self.base = base_url.rstrip("/")
        self.password = password
        self.out_dir = out_dir
        self.script = script
        self.records: list[dict] = []

    # --- yardımcılar -------------------------------------------------------
    def shot(self, page: Page, name: str, shots: list[str]) -> None:
        path = self.out_dir / name
        page.screenshot(path=str(path), full_page=True)
        shots.append(name)

    def login(self, page: Page, username: str) -> None:
        page.goto(f"{self.base}/hesap/giris/")
        page.wait_for_load_state("networkidle")
        page.fill("#id_username", username)
        page.fill("#id_password", self.password)
        # Gezinme bitmeden sonraki adıma geçilirse giriş isteği iptal olabilir (Hafta 3'te bulundu, RSK-22).
        with page.expect_navigation():
            page.click("form.sd-login__fields button[type=submit]")
        page.wait_for_load_state("networkidle")

    def nav_links(self, page: Page) -> set[str]:
        return {el.get_attribute("data-nav") for el in page.query_selector_all("[data-nav]")}

    def run(self, tc_id: str, title: str, func) -> None:
        shots: list[str] = []
        notes: list[str] = []
        try:
            func(shots, notes)
            outcome, detail = "PASS", "; ".join(notes)
        except AssertionError as exc:
            outcome, detail = "FAIL", f"{exc}; " + "; ".join(notes)
        except Exception:  # noqa: BLE001 - beklenmeyen hata ERROR olarak kaydedilir
            outcome, detail = "ERROR", traceback.format_exc(limit=3)
        self.records.append(
            {
                "tc_id": tc_id,
                "test": f"{self.script}::{tc_id}",
                "title": title,
                "outcome": outcome,
                "detail": detail,
                "screenshots": shots,
            }
        )
        print(f"{tc_id}: {outcome}  {title}")


def main() -> int:
    parser = argparse.ArgumentParser(description="SDS-07 Hafta 2 E2E doğrulaması")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--out-dir", type=Path, default=Path("reports/screenshots"))
    parser.add_argument("--results-json", type=Path, default=Path("reports/e2e-results.json"))
    args = parser.parse_args()

    password = os.environ.get("E2E_PASSWORD")
    if not password:
        print("E2E_PASSWORD ortam değişkeni tanımlı değil.", file=sys.stderr)
        return 2
    args.out_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC)
    runner = Runner(args.base_url, password, args.out_dir)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        def new_page(viewport=DESKTOP):
            # reduced_motion: ekran görüntüleri animasyon ortasında alınmasın (tekrarlanabilir kanıt)
            context = browser.new_context(
                viewport=viewport, locale="tr-TR", timezone_id="Europe/Istanbul", reduced_motion="reduce"
            )
            page = context.new_page()
            page.console_errors = []
            page.on("console", lambda m: page.console_errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: page.console_errors.append(str(e)))
            return context, page

        # TC-E2E-01 -----------------------------------------------------------
        def tc01(shots, notes):
            context, page = new_page()
            response = page.goto(f"{runner.base}/hesap/giris/")
            page.wait_for_load_state("networkidle")
            assert response.status == 200, f"HTTP {response.status}"
            assert page.inner_text("h1").strip() == "Giriş yap", "Başlık 'Giriş yap' değil"
            assert page.get_attribute("html", "lang") == "tr", "html lang=tr değil"
            assert not page.console_errors, f"Konsol hataları: {page.console_errors}"
            font = page.evaluate("document.fonts.check('16px \"IBM Plex Sans\"')")
            notes.append(f"Plex Sans yüklendi={font}")
            runner.shot(page, "01-giris-masaustu.png", shots)
            context.close()

        runner.run("TC-E2E-01", "Giriş sayfası konsol hatasız yüklenir", tc01)

        # TC-E2E-02 ve TC-E2E-03 (aynı oturum) -------------------------------
        context, page = new_page()

        def tc02(shots, notes):
            runner.login(page, USERS["requester"])
            assert page.url == f"{runner.base}/", f"Beklenen panel, gelen {page.url}"
            badge = page.inner_text("[data-testid=role-badge]").strip()
            assert badge == "Talep Sahibi", f"Rol rozeti: {badge}"
            links = runner.nav_links(page)
            assert not ({"support", "manager", "admin"} & links), f"Yetkisiz menü bağlantısı: {links}"
            notes.append("menü bağlantıları: Panelim" + "".join(f", {link}" for link in sorted(links)))
            runner.shot(page, "02-panel-talep-sahibi.png", shots)

        runner.run("TC-E2E-02", "Talep Sahibi girişi; rol rozeti ve kısıtlı menü", tc02)

        def tc03(shots, notes):
            for path, shot in (("/yonetim/", "03-403-yonetim.png"), ("/destek/", "03-403-destek.png")):
                response = page.goto(f"{runner.base}{path}")
                page.wait_for_load_state("networkidle")
                assert response.status == 403, f"{path} için HTTP {response.status}"
                assert "Bu sayfa rolünüze kapalı" in page.inner_text("main"), "403 açıklaması yok"
                assert "Talep Sahibi" in page.inner_text("[data-testid=error-403]"), "Rol bilgisi yok"
                notes.append(f"{path} → 403")
                runner.shot(page, shot, shots)

        runner.run("TC-E2E-03", "Talep Sahibi doğrudan adresle kısıtlı sayfalara giremez", tc03)
        context.close()

        # TC-E2E-04 -----------------------------------------------------------
        def tc04(shots, notes):
            context, page = new_page()
            runner.login(page, USERS["agent"])
            links = runner.nav_links(page)
            assert "support" in links and "manager" not in links, f"Menü: {links}"
            response = page.goto(f"{runner.base}/destek/")
            assert response.status == 200 and page.is_visible("[data-testid=support-workspace]"), (
                "Destek kuyruğu açılmadı"
            )
            runner.shot(page, "04-destek-kuyrugu.png", shots)
            response = page.goto(f"{runner.base}/yonetim/")
            assert response.status == 403, f"/yonetim/ için HTTP {response.status}"
            notes.append("/destek/ 200, /yonetim/ 403")
            context.close()

        runner.run("TC-E2E-04", "Destek Personeli destek kuyruğuna girer, yönetim paneline giremez", tc04)

        # TC-E2E-05 ve TC-E2E-06 (aynı oturum) -------------------------------
        context, page = new_page()

        def tc05(shots, notes):
            runner.login(page, USERS["manager"])
            links = runner.nav_links(page)
            assert {"support", "manager"} <= links, f"Menü: {links}"
            page.click("[data-nav=manager]")
            page.wait_for_load_state("networkidle")
            assert page.is_visible("[data-testid=manager-panel]"), "Yönetim paneli görünmüyor"
            runner.shot(page, "05-yonetim-paneli.png", shots)
            response = page.goto(f"{runner.base}/destek/")
            assert response.status == 200, f"/destek/ için HTTP {response.status}"
            notes.append("menüde iki bağlantı; iki sayfa 200")

        runner.run("TC-E2E-05", "Yönetici iki çalışma alanına da erişir", tc05)

        def tc06(shots, notes):
            page.goto(f"{runner.base}/")
            page.click("[data-testid=logout]")
            page.wait_for_load_state("networkidle")
            assert page.url.startswith(f"{runner.base}/hesap/giris/"), f"Çıkış sonrası adres: {page.url}"
            page.goto(f"{runner.base}/")
            page.wait_for_load_state("networkidle")
            assert "/hesap/giris/?next=/" in page.url, f"Oturum kapanmamış: {page.url}"
            notes.append("çıkış sonrası / → giriş")
            runner.shot(page, "06-cikis-sonrasi.png", shots)

        runner.run("TC-E2E-06", "Çıkış yap düğmesi oturumu kapatır", tc06)
        context.close()

        # TC-E2E-07 -----------------------------------------------------------
        overflow_js = OVERFLOW_JS

        def tc07(shots, notes):
            context, page = new_page(MOBILE)
            page.goto(f"{runner.base}/hesap/giris/")
            page.wait_for_load_state("networkidle")
            login_check = page.evaluate(overflow_js)
            runner.shot(page, "07-giris-mobil-360.png", shots)
            runner.login(page, USERS["requester"])
            panel_check = page.evaluate(overflow_js)
            runner.shot(page, "07-panel-mobil-360.png", shots)
            context.close()
            for name, check in (("giriş", login_check), ("panel", panel_check)):
                width, client = check["page"]
                assert width <= client, f"{name} sayfasında yatay taşma: {check['page']}"
                assert not check["inner"], f"{name} sayfasında iç kapsayıcı taşması: {check['inner']}"
                notes.append(f"{name}: sayfa {width}/{client} px, iç taşma yok")

        runner.run("TC-E2E-07", "360 px genişlikte yatay kaydırma yok", tc07)

        # TC-E2E-08 -----------------------------------------------------------
        def tc08(shots, notes):
            context, page = new_page()
            page.goto(f"{runner.base}/hesap/giris/")
            page.wait_for_load_state("networkidle")
            assert page.evaluate("document.activeElement.id") == "id_username", "Kullanıcı adı alanı odakta değil"
            page.keyboard.type(USERS["requester"])
            page.keyboard.press("Tab")
            assert page.evaluate("document.activeElement.id") == "id_password", "Tab parolaya geçmedi"
            page.keyboard.type(runner.password)
            page.keyboard.press("Enter")
            page.wait_for_url(f"{runner.base}/")
            page.wait_for_load_state("networkidle")
            page.keyboard.press("Tab")
            first = page.evaluate(
                "[document.activeElement.textContent.trim(), getComputedStyle(document.activeElement).outlineStyle]"
            )
            page.keyboard.press("Tab")
            second = page.evaluate(
                "(() => { const s = getComputedStyle(document.activeElement);"
                " return [document.activeElement.className, s.outlineStyle, s.outlineWidth]; })()"
            )
            assert first[0] == "İçeriğe geç", f"İlk odak 'İçeriğe geç' değil: {first}"
            assert second[1] != "none" and second[2] != "0px", f"Odak çizgisi görünmüyor: {second}"
            runner.shot(page, "08-klavye-odak.png", shots)
            notes.append(f"ilk odak: {first[0]}; ikinci odak çizgisi: {second[1]} {second[2]}")
            context.close()

        runner.run("TC-E2E-08", "Yalnız klavyeyle giriş ve görünür odak", tc08)

        # TC-E2E-09 -----------------------------------------------------------
        def tc09(shots, notes):
            context, page = new_page()
            page.goto(f"{runner.base}/hesap/giris/")
            page.wait_for_load_state("networkidle")
            checks = {
                "gövde metni (giriş formu)": ".sd-login__form h1",
                "ikincil metin": ".sd-help",
                "birincil düğme": "form.sd-login__fields button[type=submit]",
                "süreç paneli açıklaması": ".sd-process__intro",
                "süreç adımı metni": ".sd-rail__text",
            }
            failures = []
            for label, selector in checks.items():
                colors = page.evaluate(EFFECTIVE_COLORS_JS, selector)
                assert colors, f"Öğe bulunamadı: {selector}"
                ratio = contrast_ratio(colors["fg"], colors["bg"])
                notes.append(f"{label} {ratio}:1")
                if ratio < 4.5:
                    failures.append(f"{label} {ratio}:1")
            runner.login(page, USERS["requester"])
            for label, selector in {"panel ikincil metin": ".sd-panel .sd-muted", "rol rozeti": ".sd-role"}.items():
                colors = page.evaluate(EFFECTIVE_COLORS_JS, selector)
                ratio = contrast_ratio(colors["fg"], colors["bg"])
                notes.append(f"{label} {ratio}:1")
                if ratio < 4.5:
                    failures.append(f"{label} {ratio}:1")
            assert not failures, f"4.5:1 altında: {failures}"
            context.close()

        runner.run("TC-E2E-09", "Metin ve düğme kontrastı en az 4.5:1", tc09)

        browser_version = browser.version
        browser.close()

    finished = datetime.now(UTC)
    payload = {
        "kind": "e2e-playwright",
        "started_at_utc": started.isoformat(timespec="seconds"),
        "finished_at_utc": finished.isoformat(timespec="seconds"),
        "environment": {
            "browser": f"chromium {browser_version}",
            "playwright": metadata.version("playwright"),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "base_url": runner.base,
        },
        "totals": {
            "run": len(runner.records),
            "failures": sum(r["outcome"] == "FAIL" for r in runner.records),
            "errors": sum(r["outcome"] == "ERROR" for r in runner.records),
            "successful": all(r["outcome"] == "PASS" for r in runner.records),
        },
        "results": runner.records,
    }
    args.results_json.parent.mkdir(parents=True, exist_ok=True)
    args.results_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if payload["totals"]["successful"] else 1


if __name__ == "__main__":
    sys.exit(main())
