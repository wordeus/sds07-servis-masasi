#!/usr/bin/env python3
"""Hafta 5 tarayıcı (E2E) doğrulaması - TC-E2E-17, TC-E2E-18.

Gerçek tarayıcıda talebin tam yaşam döngüsü (Açık → İşlemde → Çözüldü → Kapandı), işlem
geçmişi görünümü, atanmamış personelin durum değiştirememesi, dört durum rozetinin
kontrastı ve geçmişli ayrıntı sayfasının dar ekran düzeni doğrulanır. Ortak iskelet
(`run_suite`) ve yardımcılar Hafta 2 betiğindedir.

Kullanım:
    python e2e/week5_status.py --base-url http://127.0.0.1:8000 \
        --out-dir reports/screenshots --results-json reports/e2e-week5-results.json
"""

from __future__ import annotations

import sys
from functools import partial

from playwright.sync_api import Page
from week2_auth_roles import EFFECTIVE_COLORS_JS, MOBILE, USERS, Ctx, contrast_ratio, run_suite
from week3_tickets import check_overflow, create_ticket

AGENT_NAME = "Demo Destek Personeli"


def submit(page: Page, selector: str) -> None:
    with page.expect_navigation():
        page.click(f"{selector} button[type=submit]")
    page.wait_for_load_state("networkidle")


def status_of(page: Page) -> str:
    return page.inner_text(".sd-ticket-head .sd-status").strip()


def tc17(ctx: Ctx, shots, notes):
    runner, base = ctx.runner, ctx.runner.base
    context, page = ctx.new_page()
    runner.login(page, USERS["requester"])
    url = create_ticket(
        page, base, title=f"Toplantı odası ekranı açılmıyor {ctx.suffix}", category="Donanım", priority="P2"
    )
    assert page.locator("[data-testid=status-form]").count() == 0, "Talep sahibi Açık talepte durum düğmesi görüyor"
    context.close()

    context, page = ctx.new_page()
    runner.login(page, USERS["manager"])
    page.goto(url)
    page.select_option("[data-testid=assign-form] select", label=AGENT_NAME)
    submit(page, "[data-testid=assign-form]")
    context.close()

    context, page = ctx.new_page()
    runner.login(page, USERS["agent"])
    page.goto(url)
    page.wait_for_load_state("networkidle")
    submit(page, "[data-testid=status-form]")  # İşleme al
    assert status_of(page) == "İşlemde", f"Durum: {status_of(page)}"
    submit(page, "[data-testid=status-form]")  # Çözüm açıklaması olmadan
    field = page.locator("[data-testid=status-form] textarea")
    assert field.get_attribute("aria-invalid") == "true", "Boş çözüm açıklaması işaretlenmedi"
    assert status_of(page) == "İşlemde", "Çözüm açıklaması olmadan durum değişti"
    field.fill("HDMI kablosu değiştirildi; ekran açılıyor.")
    submit(page, "[data-testid=status-form]")
    assert status_of(page) == "Çözüldü", f"Durum: {status_of(page)}"
    runner.shot(page, "17-cozuldu.png", shots)
    context.close()

    context, page = ctx.new_page()
    runner.login(page, USERS["requester"])
    page.goto(url)
    page.wait_for_load_state("networkidle")
    assert "HDMI kablosu" in page.inner_text("[data-testid=ticket-resolution]"), "Çözüm açıklaması görünmüyor"
    submit(page, "[data-testid=status-form]")  # Onayla ve kapat
    assert status_of(page) == "Kapandı", f"Durum: {status_of(page)}"
    assert page.locator("[data-testid=comment-form]").count() == 0, "Kapanan talepte yorum formu var"
    kinds = page.locator("[data-testid=history-item]").evaluate_all("els => els.map(e => e.dataset.kind)")
    expected = ["CREATED", "ASSIGNED", "STATUS_CHANGED", "STATUS_CHANGED", "STATUS_CHANGED"]
    assert kinds == expected, f"İşlem geçmişi: {kinds}"
    history = page.inner_text("[data-testid=ticket-history]")
    assert "Çözüldü → Kapandı" in history, "Kapanış geçmişte yok"
    assert not page.console_errors, f"Konsol hataları: {page.console_errors}"
    runner.shot(page, "17-kapandi-gecmis.png", shots)
    ctx.state["ticket_url"] = url
    notes.append("Açık → İşlemde → Çözüldü (boş açıklama reddedildi) → Kapandı; geçmişte 5 kayıt sırayla")
    context.close()


def tc18(ctx: Ctx, shots, notes):
    runner, base = ctx.runner, ctx.runner.base
    context, page = ctx.new_page()
    runner.login(page, USERS["requester"])
    url = create_ticket(page, base, title=f"Atanmamış talep {ctx.suffix}", category="Yazılım", priority="P3")
    context.close()

    context, page = ctx.new_page()
    runner.login(page, USERS["agent"])
    page.goto(url)
    page.wait_for_load_state("networkidle")
    assert page.locator("[data-testid=status-form]").count() == 0, "Atanmamış talepte durum düğmesi görünüyor"
    path = url.removeprefix(base) + "durum/"
    status = page.evaluate(
        """async (path) => {
            const token = document.querySelector('input[name=csrfmiddlewaretoken]').value;
            const body = new URLSearchParams({csrfmiddlewaretoken: token, target: 'IN_PROGRESS'});
            const r = await fetch(path, {method: 'POST', body, credentials: 'same-origin'});
            return r.status;
        }""",
        path,
    )
    assert status == 403, f"Atanmamış personelin durum isteği HTTP {status}"
    notes.append(f"atanmamış personel: düğme yok, POST {path} → 403")
    page.goto(f"{base}/")  # Panelin durum özetinde dört durum rozeti her zaman bulunur
    page.wait_for_load_state("networkidle")
    ratios = []
    for code in ("OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"):
        selector = f".sd-summary .sd-status[data-status={code}]"
        assert page.locator(selector).count(), f"Panelde {code} rozeti yok"
        colors = page.evaluate(EFFECTIVE_COLORS_JS, selector)
        ratio = contrast_ratio(colors["fg"], colors["bg"])
        ratios.append(f"{code} {ratio}:1")
        assert ratio >= 4.5, f"{code} rozeti kontrastı {ratio}:1"
    notes.append("rozet kontrastı: " + ", ".join(ratios))
    context.close()

    assert ctx.state.get("ticket_url"), "TC-E2E-17 talebi yok (önceki senaryo başarısız)"
    context, page = ctx.new_page(MOBILE)
    runner.login(page, USERS["requester"])
    page.goto(ctx.state["ticket_url"])
    page.wait_for_load_state("networkidle")
    check_overflow(page, "geçmişli ayrıntı 360 px", notes)
    runner.shot(page, "18-gecmis-mobil-360.png", shots)
    context.close()


def scenarios(ctx: Ctx) -> None:
    run = ctx.runner.run
    run("TC-E2E-17", "Talebin tam yaşam döngüsü ve işlem geçmişi", partial(tc17, ctx))
    run("TC-E2E-18", "Atanmamış personel durum değiştiremez; rozet kontrastı; 360 px geçmiş", partial(tc18, ctx))


def main() -> int:
    return run_suite(
        "SDS-07 Hafta 5 E2E doğrulaması", "e2e/week5_status.py", "reports/e2e-week5-results.json", scenarios
    )


if __name__ == "__main__":
    sys.exit(main())
