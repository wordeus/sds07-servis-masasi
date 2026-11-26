#!/usr/bin/env python3
"""Mutasyon denetimi: testlerin bilinçli eklenen hataları yakalayıp yakalamadığını ölçer.

Her mutasyon için proje geçici bir klasöre kopyalanır, tek bir metin değişikliği uygulanır,
tüm Django test takımı koşulur ve başarısız olan TC kimlikleri kaydedilir. Orijinal kod
değiştirilmez. Testlerden en az biri başarısız olursa mutasyon "yakalandı" sayılır.

Kullanım:
    python tools/mutation_check.py --week 2 --out docs/evidence/hafta-02/mutation-check.md
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Mutation:
    key: str
    week: int
    path: str
    old: str
    new: str
    description: str


MUTATIONS = (
    Mutation(
        "M1_requester_gets_support_perm",
        2,
        "servicedesk/roles.py",
        "REQUESTER.key: _TICKET_BASE,",
        "REQUESTER.key: _TICKET_BASE | {PERM_SUPPORT_WORKSPACE},",
        "Talep Sahibi rolüne destek kuyruğu izni verildi (yetki yükseltme)",
    ),
    Mutation(
        "M2_manager_panel_no_perm_check",
        2,
        "servicedesk/views/dashboard.py",
        "class ManagerPanelView(PermissionRequiredMixin, TemplateView):",
        "class ManagerPanelView(LoginRequiredMixin, TemplateView):",
        "Yönetim panelinde izin denetimi yerine yalnız oturum denetimi",
    ),
    Mutation(
        "M3_session_two_weeks",
        2,
        "config/settings.py",
        "SESSION_COOKIE_AGE = 8 * 60 * 60",
        "SESSION_COOKIE_AGE = 14 * 24 * 60 * 60",
        "Oturum süresi 8 saatten 2 haftaya çıkarıldı",
    ),
    Mutation(
        "M4_store_naive_local_time",
        2,
        "config/settings.py",
        "USE_TZ = True",
        "USE_TZ = False",
        "USE_TZ=False: zamanlar saat dilimsiz yerel saatle saklanır",
    ),
    Mutation(
        "M5_requester_sees_all_tickets",
        3,
        "servicedesk/services/tickets.py",
        "        return tickets.filter(requester=user)",
        "        return tickets",
        "Kayıt bazlı erişim kuralı kaldırıldı: Talep Sahibi tüm talepleri görür (IDOR)",
    ),
    Mutation(
        "M6_detail_bypasses_policy",
        3,
        "servicedesk/views/tickets.py",
        "        return visible_tickets_for(self.request.user)\n",
        "        return visible_tickets_for(self.request.user).model.objects.all()\n",
        "Ayrıntı görünümü politika fonksiyonunu atlayıp modelden doğrudan sorgular",
    ),
    Mutation(
        "M7_inactive_category_selectable",
        3,
        "servicedesk/services/tickets.py",
        "    return Category.objects.filter(is_active=True)",
        "    return Category.objects.all()",
        "Pasif kategori yeni talep formunda seçilebilir",
    ),
    Mutation(
        "M8_turkish_duplicate_check_removed",
        3,
        "servicedesk/models/ticket.py",
        "        if any(turkish_key(name) == key for name in others):",
        "        if any(name == self.name for name in others):",
        "Kategori adı tekilliğinde Türkçe büyük/küçük harf kuralı kaldırıldı",
    ),
    Mutation(
        "M9_comment_visibility_check_removed",
        4,
        "servicedesk/services/comments.py",
        "    if not author.has_perm(PERM_ADD_COMMENT) or not visible_tickets_for(author).filter(pk=ticket.pk).exists():",
        "    if not author.has_perm(PERM_ADD_COMMENT):",
        "Yorum servisi talebin görünürlüğünü denetlemiyor (başkasının talebine yorum)",
    ),
    Mutation(
        "M10_closed_ticket_comment_allowed",
        4,
        "servicedesk/services/comments.py",
        '        raise ValidationError("Kapanmış talebe yorum eklenemez.")',
        "        pass",
        "Kapanmış talebe yorum eklenebiliyor",
    ),
    Mutation(
        "M11_assign_to_any_user",
        4,
        "servicedesk/services/assignment.py",
        "    if assignee is None or not agents().filter(pk=assignee.pk).exists():",
        "    if assignee is None:",
        "Talep Destek Personeli olmayan kullanıcıya atanabiliyor",
    ),
    Mutation(
        "M12_priority_change_not_audited",
        4,
        "servicedesk/services/assignment.py",
        "        record_event(current, actor, TicketEvent.Kind.PRIORITY_CHANGED, old_value=old, new_value=priority)",
        "        pass",
        "Öncelik değişikliği işlem geçmişine yazılmıyor",
    ),
    Mutation(
        "M13_event_record_mutable",
        4,
        "servicedesk/models/activity.py",
        "        if self.pk is not None:",
        "        if False:",
        "Kaydedilmiş işlem geçmişi kaydı değiştirilebiliyor",
    ),
)


def applicable(week: int) -> list[Mutation]:
    return [m for m in MUTATIONS if m.week <= week]


def run_one(mutation: Mutation, python: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "src"
        shutil.copytree(
            ROOT, work, ignore=shutil.ignore_patterns(".venv", "reports", "docs", "*.sqlite3", "__pycache__")
        )
        target = work / mutation.path
        text = target.read_text(encoding="utf-8")
        if text.count(mutation.old) != 1:
            return {"key": mutation.key, "error": f"değiştirilecek metin bulunamadı: {mutation.old!r}"}
        target.write_text(text.replace(mutation.old, mutation.new), encoding="utf-8")
        results = Path(tmp) / "results.json"
        completed = subprocess.run(  # noqa: S603 - sabit argümanlarla yerel test koşusu
            [python, "manage.py", "test", "--results-json", str(results)],
            cwd=work,
            capture_output=True,
            text=True,
            timeout=600,
        )
        payload = json.loads(results.read_text(encoding="utf-8")) if results.exists() else {"results": []}
    failing = sorted({r["tc_id"] for r in payload["results"] if r["outcome"] in {"FAIL", "ERROR"} and r["tc_id"]})
    return {
        "key": mutation.key,
        "run": payload.get("totals", {}).get("run", 0),
        "exit_code": completed.returncode,
        "failing": failing,
        "caught": bool(failing) or completed.returncode != 0,
    }


def to_markdown(week: int, rows: list[tuple[Mutation, dict]], started: str) -> str:
    caught = sum(1 for _, r in rows if r.get("caught"))
    lines = [
        f"# Mutasyon denetimi (Hafta {week})",
        "",
        "Amaç: Testlerin gerçek hataları yakalayabildiğini göstermek. Kodun geçici kopyasına bilinçli hata "
        "eklendi, tüm Django test takımı koşuldu ve başarısız olan TC'ler kaydedildi. Orijinal kod değiştirilmedi. "
        "Betik: `tools/mutation_check.py`.",
        "",
        "| Mutasyon | Dosya | Eklenen hata | Koşulan test | Başarısız olan TC'ler | Sonuç |",
        "|---|---|---|---|---|---|",
    ]
    for mutation, result in rows:
        if "error" in result:
            lines.append(
                f"| {mutation.key} | `{mutation.path}` | {mutation.description} | - | - | HATA: {result['error']} |"
            )
            continue
        verdict = "Yakalandı" if result["caught"] else "**Yakalanmadı**"
        failing = ", ".join(result["failing"]) or "-"
        lines.append(
            f"| {mutation.key} | `{mutation.path}` | {mutation.description} | {result['run']} | {failing} | {verdict} |"
        )
    lines += ["", f"Koşu başlangıcı (UTC): {started}. Mutasyon puanı: {caught}/{len(rows)} yakalandı.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args(argv)
    started = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    for mutation in applicable(args.week):
        result = run_one(mutation, args.python)
        rows.append((mutation, result))
        print(mutation.key, "->", result)
    args.out.write_text(to_markdown(args.week, rows, started), encoding="utf-8")
    return 0 if all(r.get("caught") for _, r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
