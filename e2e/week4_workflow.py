#!/usr/bin/env python3
"""Hafta 4 tarayıcı (E2E) doğrulaması - TC-E2E-14..TC-E2E-16.

Gerçek tarayıcıda yorumlar, talebi üzerine alma, atama ve öncelik değişikliği; boş yorumun
erişilebilir hata bildirimi; başkasının talebinin yorum adresine tarayıcıdan gönderilen
isteğin 404 alması ve işlem panelli ayrıntı sayfasının dar ekran düzeni doğrulanır.
Hafta 2-3 betiklerindeki yardımcılar yeniden kullanılır.

Ön koşul: Sunucu çalışıyor ve `seed_demo_users` aynı parolayla çalıştırılmış olmalı.
Betik veritabanına talep ve yorum yazar; geçici veritabanıyla koşun.

Kullanım:
    python e2e/week4_workflow.py --base-url http://127.0.0.1:8000 \
        --out-dir reports/screenshots --results-json reports/e2e-week4-results.json
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import secrets
import sys
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

from playwright.sync_api import Page, sync_playwright
from week2_auth_roles import DESKTOP, MOBILE, USERS, Runner
from week3_tickets import check_overflow, create_ticket

NAMES = {"agent": "Demo Destek Personeli", "manager": "Demo Yönetici", "requester": "Demo Talep Sahibi"}


def submit(page: Page, selector: str) -> None:
    """Formu gönderir ve yeni sayfanın yüklenmesini bekler (RSK-22)."""
    with page.expect_navigation():
        page.click(f"{selector} button[type=submit]")
    page.wait_for_load_state("networkidle")


def add_comment(page: Page, text: str) -> None:
    page.fill("[data-testid=comment-form] textarea", text)
    submit(page, "[data-testid=comment-form]")


def main() -> int:
    parser = argparse.ArgumentParser(description="SDS-07 Hafta 4 E2E doğrulaması")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--out-dir", type=Path, default=Path("reports/screenshots"))
    parser.add_argument("--results-json", type=Path, default=Path("reports/e2e-week4-results.json"))
    args = parser.parse_args()

    password = os.environ.get("E2E_PASSWORD")
    if not password:
        print("E2E_PASSWORD ortam değişkeni tanımlı değil.", file=sys.stderr)
        return 2
    args.out_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC)
    runner = Runner(args.base_url, password, args.out_dir, script="e2e/week4_workflow.py")
    base = runner.base
    suffix = secrets.token_hex(3)
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

        # TC-E2E-14 -----------------------------------------------------------
        def tc14(shots, notes):
            context, page = new_page()
            runner.login(page, USERS["requester"])
            url = create_ticket(
                page, base, title=f"Ortak sürücü açılmıyor {suffix}", category="Ağ ve bağlantı", priority="P3"
            )
            assert page.locator("[data-testid=ticket-actions]").count() == 0, "Talep sahibi işlem panelini görüyor"
            add_comment(page, "Sabah 9'dan beri açılmıyor.")
            context.close()

            context, page = new_page()
            runner.login(page, USERS["agent"])
            page.goto(url)
            page.wait_for_load_state("networkidle")
            submit(page, "[data-testid=take-form]")
            assert NAMES["agent"] in page.inner_text("[data-testid=ticket-assignee]"), "Atanan kişi güncellenmedi"
            assert page.locator("[data-testid=take-form]").count() == 0, "Üzerime al düğmesi hâlâ görünüyor"
            add_comment(page, "Sunucu tarafını kontrol ediyorum.")
            page.select_option("[data-testid=priority-form] select", "P1")
            submit(page, "[data-testid=priority-form]")
            assert page.inner_text("[data-testid=ticket-priority]").strip() == "P1 (Kritik)", "Öncelik değişmedi"
            assert not page.console_errors, f"Konsol hataları: {page.console_errors}"
            runner.shot(page, "14-destek-islemleri.png", shots)
            context.close()

            context, page = new_page()
            runner.login(page, USERS["requester"])
            page.goto(url)
            page.wait_for_load_state("networkidle")
            comments = page.locator("[data-testid=comment]").all_inner_texts()
            assert len(comments) == 2, f"Yorum sayısı {len(comments)}"
            assert "Sabah 9" in comments[0] and "Sunucu tarafını" in comments[1], "Yorum sırası yanlış"
            assert NAMES["agent"] in comments[1], "Yorumu yazan görünmüyor"
            assert page.inner_text("[data-testid=ticket-priority]").strip() == "P1 (Kritik)"
            runner.shot(page, "14-talep-sahibi-gorunum.png", shots)
            state["ticket_url"] = url
            notes.append("talep sahibi yorum yazdı; destek üzerine aldı, yanıtladı, P3→P1")
            notes.append("talep sahibi iki yorumu sırayla gördü")
            context.close()

        runner.run("TC-E2E-14", "Yorumlaşma, üzerine alma ve öncelik değişikliği", tc14)

        # TC-E2E-15 -----------------------------------------------------------
        def tc15(shots, notes):
            context, page = new_page()
            runner.login(page, USERS["requester"])
            url = create_ticket(
                page, base, title=f"Yeni kullanıcı hesabı {suffix}", category="Hesap ve erişim", priority="P4"
            )
            context.close()

            context, page = new_page()
            runner.login(page, USERS["manager"])
            page.goto(url)
            page.wait_for_load_state("networkidle")
            options = page.locator("[data-testid=assign-form] select option").all_inner_texts()
            assert NAMES["agent"] in options, f"Atama listesinde destek personeli yok: {options}"
            assert NAMES["manager"] not in options and NAMES["requester"] not in options, f"Liste: {options}"
            page.select_option("[data-testid=assign-form] select", label=NAMES["agent"])
            submit(page, "[data-testid=assign-form]")
            assert NAMES["agent"] in page.inner_text("[data-testid=ticket-assignee]"), "Atama yapılmadı"
            assert "atandı" in page.inner_text(".sd-messages"), "Atama mesajı yok"
            submit(page, "[data-testid=comment-form]")  # boş yorum
            field = page.locator("[data-testid=comment-form] textarea")
            assert field.get_attribute("aria-invalid") == "true", "Boş yorum hatası işaretlenmedi"
            assert field.get_attribute("aria-describedby") == "body-hata", "Hata mesajı alanla ilişkili değil"
            assert "Yorum boş olamaz." in page.inner_text("#body-hata")
            runner.shot(page, "15-yonetici-atama.png", shots)
            notes.append("atama listesinde yalnız destek personeli; atama yapıldı")
            notes.append("boş yorum aria-invalid ile reddedildi")
            context.close()

        runner.run("TC-E2E-15", "Yönetici atama yapar; boş yorum erişilebilir biçimde reddedilir", tc15)

        # TC-E2E-16 -----------------------------------------------------------
        def tc16(shots, notes):
            context, page = new_page()
            runner.login(page, USERS["agent"])
            agent_url = create_ticket(
                page, base, title=f"Personelin kendi talebi {suffix}", category="Yazılım", priority="P3"
            )
            context.close()

            context, page = new_page()
            runner.login(page, USERS["requester"])
            page.goto(f"{base}/talepler/yeni/")
            page.wait_for_load_state("networkidle")
            path = agent_url.removeprefix(base) + "yorum/"
            status = page.evaluate(
                """async (path) => {
                    const token = document.querySelector('input[name=csrfmiddlewaretoken]').value;
                    const body = new URLSearchParams({csrfmiddlewaretoken: token, body: 'izinsiz yorum'});
                    const r = await fetch(path, {method: 'POST', body, credentials: 'same-origin'});
                    return r.status;
                }""",
                path,
            )
            assert status == 404, f"Başkasının talebine yorum isteği HTTP {status}"
            notes.append(f"POST {path} → 404")
            context.close()

            assert state.get("ticket_url"), "TC-E2E-14 talebi yok (önceki senaryo başarısız)"
            context, page = new_page(MOBILE)
            runner.login(page, USERS["manager"])
            page.goto(state["ticket_url"])
            page.wait_for_load_state("networkidle")
            check_overflow(page, "yorumlu ve işlem panelli ayrıntı 360 px", notes)
            runner.shot(page, "16-ayrinti-mobil-360.png", shots)
            context.close()

        runner.run("TC-E2E-16", "Başkasının talebine yorum isteği 404; ayrıntı sayfası 360 px'te taşmaz", tc16)

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
