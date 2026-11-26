#!/usr/bin/env python3
"""Sunum ve canlı demo videosu (Faz 5): HTML slaytlar + gerçek uygulamada talep yaşam döngüsü.

Betik E2E koşusuyla aynı güvenli düzeni kurar (geçici veritabanı, rastgele parola, DEBUG
kapalı sunucu), Playwright ile tek bir tarayıcı oturumunu video olarak kaydeder:

1. `docs/final/sunum/index.html` slaytları (kapak ... demo geçişi)
2. Canlı demo: Talep Sahibi talep açar → başkasının talebi 404 → Yönetici atar →
   Destek Personeli işleme alır, yorum yazar, çözüm açıklaması zorunluluğu → çözer →
   Talep Sahibi onaylayıp kapatır → işlem geçmişi
3. Sonuç slaytları

Ekranın altında her adımın Türkçe açıklaması gösterilir; tıklanan öğe kısa süre vurgulanır.
Video sessizdir. Çıktı: WebM (VP8), 1600×900.

Kullanım:
    python tools/record_demo.py --out reports/demo/SDS-07_Sunum_ve_Demo.webm
"""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SIZE = {"width": 1600, "height": 900}
PORT = 8766
DEMO_SLIDES_BEFORE = [(0, 9), (1, 11), (2, 11), (3, 12), (4, 11), (5, 12), (6, 11), (7, 6)]  # (slayt, saniye)
DEMO_SLIDES_AFTER = [(8, 11), (9, 13), (10, 11), (11, 10)]

CAPTION_JS = """
(() => {
  const KEY = 'sds07-demo-caption';
  function render() {
    const text = sessionStorage.getItem(KEY) || '';
    let bar = document.getElementById('sds07-caption');
    if (!text) { if (bar) bar.remove(); return; }
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'sds07-caption';
      bar.style.cssText = 'position:fixed;left:50%;bottom:28px;transform:translateX(-50%);z-index:2147483647;'
        + 'max-width:1240px;padding:14px 26px;border-radius:10px;background:rgba(23,34,53,.94);color:#fff;'
        + 'font:500 24px/1.35 "IBM Plex Sans",system-ui,sans-serif;box-shadow:0 8px 30px rgba(0,0,0,.25);'
        + 'pointer-events:none;text-align:center';
      document.documentElement.appendChild(bar);
    }
    bar.textContent = text;
  }
  window.__setCaption = (text) => { sessionStorage.setItem(KEY, text || ''); render(); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', render); else render();
})();
"""


def port_in_use(port: int) -> bool:
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


class Demo:
    def __init__(self, page: Page, base: str, password: str):
        self.page, self.base, self.password = page, base, password

    def caption(self, text: str, hold: float = 0.0) -> None:
        self.page.evaluate("t => window.__setCaption && window.__setCaption(t)", text)
        if hold:
            self.page.wait_for_timeout(int(hold * 1000))

    def highlight(self, selector: str) -> None:
        self.page.locator(selector).first.scroll_into_view_if_needed()
        self.page.eval_on_selector(
            selector,
            "el => { el.style.outline = '4px solid #f2b661'; el.style.outlineOffset = '3px';"
            " setTimeout(() => { el.style.outline = ''; }, 900); }",
        )
        self.page.wait_for_timeout(700)

    def click(self, selector: str, navigate: bool = True) -> None:
        self.highlight(selector)
        if navigate:
            with self.page.expect_navigation():
                self.page.click(selector)
            self.page.wait_for_load_state("networkidle")
        else:
            self.page.click(selector)

    def type(self, selector: str, text: str) -> None:
        self.page.click(selector)
        self.page.type(selector, text, delay=35)

    def scroll_to(self, selector: str, pause: float = 1.5) -> None:
        self.page.eval_on_selector(selector, "el => el.scrollIntoView({behavior: 'smooth', block: 'center'})")
        self.page.wait_for_timeout(int(pause * 1000))

    def goto(self, url: str) -> None:
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")

    def login(self, username: str, who: str) -> None:
        self.goto(f"{self.base}/hesap/giris/")
        self.caption(f"{who} giriş yapıyor ({username})", 1.0)
        self.type("#id_username", username)
        self.type("#id_password", self.password)
        self.click("form.sd-login__fields button[type=submit]")

    def logout(self) -> None:
        self.click("[data-testid=logout]")


def run_demo(demo: Demo, other_ticket_url: str) -> None:
    page = demo.page
    demo.login("demo.talep", "1/6 · Talep Sahibi")
    demo.caption("Panel: kullanıcının rolü ve bu role açık yetkiler (sunucu tarafında denetlenir)", 4)
    demo.click("[data-nav=tickets]")
    demo.caption("Talep Sahibi yalnız kendi taleplerini görür (kayıt bazlı erişim)", 3)
    demo.click("[data-testid=new-ticket]")
    demo.caption("2/6 · Yeni talep: başlık, açıklama, kategori ve öncelik", 1)
    demo.type("#id_title", "Muhasebe yazıcısı kâğıt sıkıştırıyor")
    demo.type("#id_description", "Her baskıda ikinci sayfada kâğıt sıkışıyor. Sabahtan beri devam ediyor.")
    page.select_option("#id_category", label="Donanım")
    page.select_option("#id_priority", "P2")
    page.wait_for_timeout(600)
    demo.click("[data-testid=ticket-form] button[type=submit]")
    ticket_url = page.url
    demo.caption("Talep kaydedildi: benzersiz INC numarası, durum Açık; işlem geçmişine ilk kayıt yazıldı", 4.5)
    demo.goto(other_ticket_url)
    demo.caption("Başka birinin talebinin adresi yazılınca: 404. Kaydın var olup olmadığı bile açığa çıkmaz (FR-14)", 5)
    demo.goto(ticket_url)
    demo.logout()

    demo.login("demo.yonetici", "3/6 · Yönetici")
    demo.goto(ticket_url)
    demo.caption("Yönetici talebi yalnız Destek Personeli rolündeki birine atayabilir (FR-16)", 2)
    demo.highlight("[data-testid=assign-form] select")
    page.select_option("[data-testid=assign-form] select", label="Demo Destek Personeli")
    page.wait_for_timeout(700)
    demo.click("[data-testid=assign-form] button[type=submit]")
    demo.caption("Talep atandı; atama işlem geçmişine eski ve yeni değerle yazıldı", 3.5)
    demo.logout()

    demo.login("demo.destek", "4/6 · Destek Personeli")
    demo.goto(ticket_url)
    demo.caption("Atanmış personel talebi İşlemde durumuna alır", 2)
    demo.click("[data-testid=status-form] button[type=submit]")
    demo.caption("Durum: İşlemde. Talep sahibine yorumla bilgi veriliyor (FR-17)", 1.5)
    demo.type(
        "[data-testid=comment-form] textarea",
        "Merdaneleri temizleyip ayarları kontrol edeceğim, öğleden sonra yerinde bakıyorum.",
    )
    demo.click("[data-testid=comment-form] button[type=submit]")
    demo.caption("Çözüldü olarak işaretlerken çözüm açıklaması boş bırakılırsa…", 1.5)
    demo.click("[data-testid=status-form] button[type=submit]")
    demo.caption("…istek reddedilir: çözüm açıklaması zorunludur (FR-19)", 3.5)
    demo.type(
        "[data-testid=status-form] textarea",
        "Merdaneler temizlendi, kâğıt kılavuzu yeniden ayarlandı. Deneme baskısı sorunsuz.",
    )
    demo.click("[data-testid=status-form] button[type=submit]")
    demo.caption("Durum: Çözüldü. Kapatma kararı talep sahibinde", 3.5)
    demo.logout()

    demo.login("demo.talep", "5/6 · Talep Sahibi")
    demo.goto(ticket_url)
    demo.scroll_to("[data-testid=ticket-resolution]", 1)
    demo.caption("Talep sahibi çözüm açıklamasını ve yorumu görür", 3)
    demo.scroll_to("[data-testid=status-panel]", 0.5)
    demo.caption("Çözümü onaylayıp talebi kapatır (ISO 9001 8.6)", 1.5)
    demo.click("[data-testid=status-form] button[type=submit]")
    demo.caption("Durum: Kapandı. Kapanan talebe artık yorum eklenemez", 3.5)
    demo.scroll_to("[data-testid=ticket-history]", 1)
    demo.caption(
        "6/6 · İşlem geçmişi: kim, ne zaman (İstanbul saati), eski → yeni. Kayıtlar değiştirilemez (FR-20, FR-21)", 7
    )
    demo.caption("")


def prepare(env: dict, python: str) -> str:
    """Veritabanı, demo kullanıcılar ve demo için başkasına ait bir talep; o talebin yolunu döndürür."""
    subprocess.run([python, "manage.py", "migrate", "-v", "0"], cwd=ROOT, env=env, check=True)
    subprocess.run(
        [python, "manage.py", "seed_demo_users", "--password", env["E2E_PASSWORD"]],
        cwd=ROOT,
        env=env,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    code = (
        "from django.contrib.auth import get_user_model; from servicedesk.models import Category;"
        "from servicedesk.services.tickets import create_ticket;"
        "u = get_user_model().objects.get(username='demo.destek');"
        "t = create_ticket(requester=u, title='Toplantı odası projektörü bağlanmıyor', description='HDMI girişi görüntü vermiyor.',"
        " category=Category.objects.get(name='Donanım'), priority='P3'); print(t.pk)"
    )
    out = subprocess.run(
        [python, "manage.py", "shell", "-c", code], cwd=ROOT, env=env, check=True, capture_output=True, text=True
    )
    return f"/talepler/{out.stdout.strip().splitlines()[-1]}/"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path("reports/demo/SDS-07_Sunum_ve_Demo.webm"))
    args = parser.parse_args()
    if port_in_use(PORT):
        print(f"HATA: {PORT} portu kullanımda.", file=sys.stderr)
        return 3
    python = sys.executable
    tmp = Path(tempfile.mkdtemp(prefix="sds07-demo-"))
    env = dict(
        os.environ,
        PYTHONUTF8="1",
        DJANGO_SQLITE_PATH=str(tmp / "demo.sqlite3"),
        E2E_PASSWORD="Demo-" + secrets.token_urlsafe(10),
    )
    other_path = prepare(env, python)
    server = subprocess.Popen(
        [python, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload", "--insecure"],
        cwd=ROOT,
        env=dict(env, DJANGO_DEBUG="0"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(60):
            if port_in_use(PORT):
                break
            time.sleep(0.5)
        base = f"http://127.0.0.1:{PORT}"
        slides = (ROOT / "docs/final/sunum/index.html").as_uri()
        video_dir = tmp / "video"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport=SIZE,
                record_video_dir=str(video_dir),
                record_video_size=SIZE,
                locale="tr-TR",
                timezone_id="Europe/Istanbul",
            )
            context.add_init_script(CAPTION_JS)
            page = context.new_page()
            demo = Demo(page, base, env["E2E_PASSWORD"])
            page.goto(slides)
            page.wait_for_timeout(800)
            for index, seconds in DEMO_SLIDES_BEFORE:
                page.evaluate(f"goTo({index})")
                page.wait_for_timeout(seconds * 1000)
            run_demo(demo, base + other_path)
            page.goto(slides)
            for index, seconds in DEMO_SLIDES_AFTER:
                page.evaluate(f"goTo({index})")
                page.wait_for_timeout(seconds * 1000)
            video = page.video
            context.close()
            browser.close()
            args.out.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(video.path(), args.out)
        print(f"Video yazıldı: {args.out}")
        return 0
    finally:
        server.terminate()
        server.wait(timeout=10)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
