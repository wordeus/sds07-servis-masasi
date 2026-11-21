#!/usr/bin/env python3
"""Hafta 3 tarayıcı (E2E) doğrulaması - TC-E2E-10..TC-E2E-13.

Gerçek tarayıcıda talep oluşturma, kayıt bazlı erişim (başkasının talebine adres
çubuğundan erişim), destek kuyruğu ve liste filtresi, dar ekran düzeni, durum rozeti
kontrastı ve kategori pasifleştirme doğrulanır. Hafta 2 betiğindeki yardımcılar
(`Runner`, kontrast hesabı, taşma ölçümü) yeniden kullanılır.

Ön koşul: Sunucu çalışıyor ve `seed_demo_users` aynı parolayla çalıştırılmış olmalı.
Betik veritabanına yeni talep ve kategori yazar; geçici veritabanıyla koşun
(`tools/run_e2e.sh` bunu yapar).

Kullanım:
    python e2e/week3_tickets.py --base-url http://127.0.0.1:8000 \
        --out-dir docs/evidence/hafta-03/screenshots --results-json reports/e2e-week3-results.json
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import secrets
import sys
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

from playwright.sync_api import Page, sync_playwright
from week2_auth_roles import DESKTOP, EFFECTIVE_COLORS_JS, MOBILE, OVERFLOW_JS, USERS, Runner, contrast_ratio

TICKET_NUMBER = re.compile(r"^INC-\d{6}$")


def create_ticket(page: Page, base: str, *, title: str, category: str, priority: str) -> str:
    """Formdan talep açar; ayrıntı sayfasının adresini döndürür."""
    page.goto(f"{base}/talepler/yeni/")
    page.wait_for_load_state("networkidle")
    page.fill("#id_title", title)
    page.fill("#id_description", "E2E senaryosu: ekran açılıyor ama kayıt düğmesi tepki vermiyor.")
    page.select_option("#id_category", label=category)
    page.select_option("#id_priority", priority)
    with page.expect_navigation():
        page.click("[data-testid=ticket-form] button[type=submit]")
    page.wait_for_load_state("networkidle")
    return page.url


def check_overflow(page: Page, name: str, notes: list[str]) -> None:
    check = page.evaluate(OVERFLOW_JS)
    width, client = check["page"]
    assert width <= client, f"{name}: sayfada yatay taşma {check['page']}"
    assert not check["inner"], f"{name}: iç kapsayıcı taşması {check['inner']}"
    notes.append(f"{name}: sayfa {width}/{client} px, iç taşma yok")


def main() -> int:
    parser = argparse.ArgumentParser(description="SDS-07 Hafta 3 E2E doğrulaması")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--out-dir", type=Path, default=Path("reports/screenshots"))
    parser.add_argument("--results-json", type=Path, default=Path("reports/e2e-week3-results.json"))
    args = parser.parse_args()

    password = os.environ.get("E2E_PASSWORD")
    if not password:
        print("E2E_PASSWORD ortam değişkeni tanımlı değil.", file=sys.stderr)
        return 2
    args.out_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC)
    runner = Runner(args.base_url, password, args.out_dir, script="e2e/week3_tickets.py")
    base = runner.base
    suffix = secrets.token_hex(3)  # Aynı veritabanında tekrar koşulursa adlar çakışmasın
    state: dict[str, str] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        def new_page(viewport=DESKTOP):
            context = browser.new_context(
                viewport=viewport, locale="tr-TR", timezone_id="Europe/Istanbul", reduced_motion="reduce"
            )
            page = context.new_page()
            page.console_errors = []
            page.on("console", lambda m: page.console_errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: page.console_errors.append(str(e)))
            return context, page

        # TC-E2E-10 -----------------------------------------------------------
        def tc10(shots, notes):
            context, page = new_page()
            runner.login(page, USERS["requester"])
            page.click("[data-nav=tickets]")
            page.wait_for_load_state("networkidle")
            page.click("[data-testid=new-ticket]")
            page.wait_for_load_state("networkidle")
            page.fill("#id_title", "VPN")
            with page.expect_navigation():
                page.click("[data-testid=ticket-form] button[type=submit]")
            assert page.get_attribute("#id_title", "aria-invalid") == "true", "Kısa başlık hatası işaretlenmedi"
            notes.append("4 karakterden kısa başlık reddedildi")
            runner.shot(page, "10-yeni-talep-hata.png", shots)
            title = f"VPN bağlantısı sık kopuyor {suffix}"
            url = create_ticket(page, base, title=title, category="Ağ ve bağlantı", priority="P2")
            number = page.inner_text("[data-testid=ticket-number]").strip()
            assert TICKET_NUMBER.match(number), f"Talep numarası biçimi: {number}"
            assert page.inner_text(".sd-ticket-head .sd-status").strip() == "Açık", "Durum Açık değil"
            assert number in page.inner_text(".sd-messages"), "Başarı mesajı numarayı içermiyor"
            assert not page.console_errors, f"Konsol hataları: {page.console_errors}"
            runner.shot(page, "10-talep-ayrinti.png", shots)
            page.click("[data-nav=tickets]")
            page.wait_for_load_state("networkidle")
            assert number in page.inner_text("[data-testid=ticket-table]"), "Yeni talep listede yok"
            runner.shot(page, "10-taleplerim-liste.png", shots)
            state.update(requester_ticket_url=url, requester_ticket_number=number, requester_ticket_title=title)
            notes.append(f"{number} oluşturuldu; durum Açık; listede görünüyor")
            context.close()

        runner.run("TC-E2E-10", "Talep Sahibi talep açar; numara ve Açık durumu görünür", tc10)

        # TC-E2E-11 -----------------------------------------------------------
        def tc11(shots, notes):
            context, page = new_page()
            runner.login(page, USERS["agent"])
            agent_title = f"Destek personelinin kendi talebi {suffix}"
            agent_url = create_ticket(page, base, title=agent_title, category="Yazılım", priority="P3")
            context.close()
            context, page = new_page()
            runner.login(page, USERS["requester"])
            response = page.goto(agent_url)
            page.wait_for_load_state("networkidle")
            assert response.status == 404, f"Başkasının talebi için HTTP {response.status}"
            text = page.inner_text("main")
            assert "Sayfa veya kayıt bulunamadı" in text, "404 sayfası beklenen metni içermiyor"
            assert agent_title not in text, "404 sayfası talep başlığını sızdırıyor"
            runner.shot(page, "11-baskasinin-talebi-404.png", shots)
            page.goto(f"{base}/talepler/")
            page.wait_for_load_state("networkidle")
            assert agent_title not in page.inner_text("main"), "Başkasının talebi listede görünüyor"
            notes.append(f"{agent_url.removeprefix(base)} → 404; listede yok")
            context.close()

        runner.run("TC-E2E-11", "Talep Sahibi başkasının talebine adres çubuğundan erişemez (404)", tc11)

        # TC-E2E-12 -----------------------------------------------------------
        def tc12(shots, notes):
            number = state.get("requester_ticket_number")
            assert number, "TC-E2E-10 talebi yok (önceki senaryo başarısız)"
            context, page = new_page()
            runner.login(page, USERS["agent"])
            page.click("[data-nav=support]")
            page.wait_for_load_state("networkidle")
            assert number in page.inner_text("[data-testid=support-workspace]"), "Talep destek kuyruğunda yok"
            runner.shot(page, "12-destek-kuyrugu.png", shots)
            page.goto(f"{base}/talepler/")
            page.wait_for_load_state("networkidle")
            page.select_option("#id_priority", "P2")
            page.select_option("#id_status", "OPEN")
            with page.expect_navigation():
                page.click("[data-testid=ticket-filter] button[type=submit]")
            rows = page.inner_text("[data-testid=ticket-table]")
            assert number in rows and "P3 (Orta)" not in rows, "Öncelik filtresi beklenen satırları vermedi"
            runner.shot(page, "12-liste-filtre.png", shots)
            colors = page.evaluate(EFFECTIVE_COLORS_JS, "[data-testid=ticket-table] .sd-status")
            ratio = contrast_ratio(colors["fg"], colors["bg"])
            assert ratio >= 4.5, f"Durum rozeti kontrastı {ratio}:1"
            notes.append(f"kuyrukta ve P2+Açık filtresinde {number}; Açık rozeti {ratio}:1")
            context.close()

            context, page = new_page(MOBILE)
            runner.login(page, USERS["agent"])
            page.goto(f"{base}/talepler/")
            page.wait_for_load_state("networkidle")
            check_overflow(page, "liste 360 px", notes)
            runner.shot(page, "12-liste-mobil-360.png", shots)
            page.goto(state["requester_ticket_url"])
            page.wait_for_load_state("networkidle")
            check_overflow(page, "ayrıntı 360 px", notes)
            runner.shot(page, "12-ayrinti-mobil-360.png", shots)
            context.close()

        runner.run("TC-E2E-12", "Destek kuyruğu, liste filtresi, dar ekran düzeni ve durum rozeti kontrastı", tc12)

        # TC-E2E-13 -----------------------------------------------------------
        def tc13(shots, notes):
            name = f"Toplantı odası {suffix}"
            context, page = new_page()
            runner.login(page, USERS["manager"])
            page.click("[data-nav=categories]")
            page.wait_for_load_state("networkidle")
            page.fill("#id_name", name)
            with page.expect_navigation():
                page.click("[data-testid=category-form] button[type=submit]")
            row = page.locator(f'tr[data-category="{name}"]')
            assert row.count() == 1, "Yeni kategori listede yok"
            requester_context, requester_page = new_page()
            runner.login(requester_page, USERS["requester"])
            requester_page.goto(f"{base}/talepler/yeni/")
            options = requester_page.locator("#id_category option").all_inner_texts()
            assert name in options, "Etkin kategori talep formunda yok"
            with page.expect_navigation():
                row.locator("[data-action=deactivate]").click()
            assert "Pasif" in page.locator(f'tr[data-category="{name}"]').inner_text(), "Kategori pasif görünmüyor"
            runner.shot(page, "13-kategoriler.png", shots)
            requester_page.goto(f"{base}/talepler/yeni/")
            options = requester_page.locator("#id_category option").all_inner_texts()
            assert name not in options, "Pasif kategori talep formunda hâlâ listeleniyor"
            notes.append("kategori eklendi ve formda göründü; pasifleştirilince formdan kalktı")
            requester_context.close()
            context.close()

        runner.run("TC-E2E-13", "Yönetici kategori ekler ve pasifleştirir; pasif kategori formda listelenmez", tc13)

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
