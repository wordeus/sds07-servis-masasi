"""MOD-ROLE - Rol tanımları, rol-yetki matrisi ve grup senkronizasyonu.

Tasarım kararı (docs/SDD.md, KRR-06):
* Rol = Django Group. Kullanıcının rolü grup üyeliğinden okunur (gösterim için).
* Yetki = Django Permission. Görünümler yetkiyi her istekte sunucuda,
  izin (permission) üzerinden denetler; menü bağlantısını gizlemek yetkilendirme
  sayılmaz (FR-09).
* Rol-izin matrisi bu dosyada tanımlıdır ve her `migrate` sonrasında veritabanındaki
  gruplara uygulanır. Yönetim sitesinden gruba elle eklenen izinler bir sonraki
  `migrate` ile matrise geri döner (yapılandırma yönetimi: tek doğruluk kaynağı kod).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from django.core.exceptions import ImproperlyConfigured
from django.db import DEFAULT_DB_ALIAS, transaction

# Aktif proje haftası. Yetenek satırları bu haftaya göre "Kullanılabilir" veya
# "Hafta N" olarak gösterilir (docs/SRS.md §2.6 haftalık plan).
CURRENT_WEEK = 4


@dataclass(frozen=True)
class Role:
    key: str  # Kod içindeki sabit anahtar
    group_name: str  # Veritabanındaki Group.name
    label: str  # Arayüzde görünen ad
    precedence: int  # Birden çok rol grubunda büyük olan geçerli olur (FR-08)


REQUESTER = Role("requester", "Talep Sahibi", "Talep Sahibi", 1)
AGENT = Role("agent", "Destek Personeli", "Destek Personeli", 2)
MANAGER = Role("manager", "Yönetici", "Yönetici", 3)

ROLES: tuple[Role, ...] = (REQUESTER, AGENT, MANAGER)
ROLES_BY_PRECEDENCE: tuple[Role, ...] = tuple(sorted(ROLES, key=lambda r: r.precedence, reverse=True))

PERM_SUPPORT_WORKSPACE = "servicedesk.access_support_workspace"
PERM_MANAGER_PANEL = "servicedesk.access_manager_panel"
# Hafta 3 (MOD-TICKET). Django'nun model başına ürettiği izinler (add/view/change)
# ve Ticket modelindeki özel izin. Kayıt düzeyindeki kural (talep sahibi yalnız kendi
# kayıtlarını görür) services/tickets.py içindeki tek politika fonksiyonundadır.
PERM_ADD_TICKET = "servicedesk.add_ticket"
PERM_VIEW_TICKET = "servicedesk.view_ticket"  # Talep ekranlarına erişim (kendi talepleri)
PERM_VIEW_ALL_TICKETS = "servicedesk.view_all_tickets"  # Tüm talepleri görme
PERM_VIEW_CATEGORY = "servicedesk.view_category"
PERM_ADD_CATEGORY = "servicedesk.add_category"
PERM_CHANGE_CATEGORY = "servicedesk.change_category"
# Hafta 4: yorum (FR-17), üzerine alma ve atama (FR-16), öncelik değişikliği (AK-03, KRR-17).
PERM_ADD_COMMENT = "servicedesk.add_comment"
PERM_TAKE_TICKET = "servicedesk.take_ticket"
PERM_ASSIGN_TICKET = "servicedesk.assign_ticket"
PERM_CHANGE_PRIORITY = "servicedesk.change_ticket_priority"

_TICKET_BASE = frozenset({PERM_ADD_TICKET, PERM_VIEW_TICKET, PERM_ADD_COMMENT})
_TICKET_WORK = frozenset({PERM_VIEW_ALL_TICKETS, PERM_TAKE_TICKET, PERM_CHANGE_PRIORITY})

# Rol-izin matrisi (Hafta 4). Sonraki haftada durum geçişi izinleri eklenecek (PRC-07).
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    REQUESTER.key: _TICKET_BASE,
    AGENT.key: _TICKET_BASE | _TICKET_WORK | {PERM_SUPPORT_WORKSPACE},
    MANAGER.key: _TICKET_BASE
    | _TICKET_WORK
    | {
        PERM_ASSIGN_TICKET,
        PERM_SUPPORT_WORKSPACE,
        PERM_MANAGER_PANEL,
        PERM_VIEW_CATEGORY,
        PERM_ADD_CATEGORY,
        PERM_CHANGE_CATEGORY,
    },
}


@dataclass(frozen=True)
class Capability:
    """Rol matrisindeki bir satır: hangi rol, hangi kapsamla, hangi haftada.

    `week=None`: yetenek bu teslimin kapsamı dışındadır (gelecek çalışma, KRR-18).
    """

    label: str
    week: int | None
    scope: dict  # role.key -> kapsam açıklaması

    def scope_for(self, role: Role | None) -> str | None:
        if role is None:
            return None
        return self.scope.get(role.key)

    @property
    def out_of_scope(self) -> bool:
        return self.week is None

    @property
    def available(self) -> bool:
        return self.week is not None and self.week <= CURRENT_WEEK


FULL = "Tam erişim"
# Hafta 6-10 yetenekleri bu teslimin kapsamı dışındadır (week=None; SRS §1.2, KRR-18).
CAPABILITIES: tuple[Capability, ...] = (
    Capability(
        "Giriş yapma ve kendi panelini görme",
        2,
        {REQUESTER.key: "Kendi hesabı", AGENT.key: "Kendi hesabı", MANAGER.key: "Kendi hesabı"},
    ),
    Capability("Destek kuyruğu çalışma alanı", 2, {AGENT.key: FULL, MANAGER.key: FULL}),
    Capability("Yönetim paneli", 2, {MANAGER.key: FULL}),
    Capability(
        "Talep oluşturma",
        3,
        {REQUESTER.key: "Kendi adına", AGENT.key: "Kendi adına", MANAGER.key: "Kendi adına"},
    ),
    Capability(
        "Talepleri görüntüleme",
        3,
        {REQUESTER.key: "Yalnız kendi talepleri", AGENT.key: "Tüm talepler", MANAGER.key: "Tüm talepler"},
    ),
    Capability("Kategori ekleme ve pasifleştirme", 3, {MANAGER.key: FULL}),
    Capability(
        "Talebe yorum ekleme",
        4,
        {REQUESTER.key: "Kendi taleplerine", AGENT.key: "Tüm taleplere", MANAGER.key: "Tüm taleplere"},
    ),
    Capability("Talebi üzerine alma", 4, {AGENT.key: "Atanmamış talepler", MANAGER.key: "Atanmamış talepler"}),
    Capability("Talebi destek personeline atama", 4, {MANAGER.key: "Tüm talepler"}),
    Capability("Talep önceliğini değiştirme", 4, {AGENT.key: "Tüm talepler", MANAGER.key: "Tüm talepler"}),
    Capability(
        "Durum ilerletme (Açık → İşlemde → Çözüldü)",
        5,
        {AGENT.key: "Kendisine atanmış talepler", MANAGER.key: "Tüm talepler"},
    ),
    Capability(
        "Talebi kapatma (Çözüldü → Kapandı)",
        5,
        {REQUESTER.key: "Kendi talebini onaylayarak", MANAGER.key: "Tüm talepler"},
    ),
    Capability(
        "Değişiklik kaydı açma ve uygulama sonucu girme",
        None,
        {AGENT.key: "Sonuç yalnız onaylı kayıtta", MANAGER.key: "Sonuç yalnız onaylı kayıtta"},
    ),
    Capability("Değişikliği onaylama veya reddetme", None, {MANAGER.key: "Kendi açtığı kayıt hariç"}),
    Capability("SLA süre uyarılarını alma", None, {AGENT.key: "Kendisine atanmış talepler"}),
    Capability("SLA ihlali eskalasyonlarını alma", None, {MANAGER.key: "Tüm ihlaller"}),
    Capability("Memnuniyet puanı verme", None, {REQUESTER.key: "Kendi kapanmış talebine bir kez"}),
    Capability("KPI paneli", None, {MANAGER.key: FULL}),
    Capability("Uygunsuzluk kaydı açma", None, {AGENT.key: FULL, MANAGER.key: FULL}),
    Capability("Kök neden, düzeltici faaliyet ve etkinlik kontrolü", None, {MANAGER.key: FULL}),
)


def get_role(user) -> Role | None:
    """Kullanıcının rolünü grup üyeliğinden belirler (FR-08).

    Birden fazla rol grubu varsa önceliği en yüksek olan döner
    (Yönetici > Destek Personeli > Talep Sahibi). Rol grubu yoksa None.
    """
    if not getattr(user, "is_authenticated", False):
        return None
    group_names = set(user.groups.values_list("name", flat=True))
    return next((r for r in ROLES_BY_PRECEDENCE if r.group_name in group_names), None)


def capabilities_for(role: Role | None) -> list[dict]:
    """Panelde gösterilecek, role açık yetenek satırları."""
    rows = []
    for capability in CAPABILITIES:
        scope = capability.scope_for(role)
        if scope is None:
            continue
        rows.append(
            {
                "label": capability.label,
                "scope": scope,
                "week": capability.week,
                "available": capability.available,
                "out_of_scope": capability.out_of_scope,
            }
        )
    return rows


@dataclass(frozen=True)
class SyncResult:
    role: Role
    created: bool
    added: int
    removed: int


def _resolve_permissions(role: Role, using: str):
    from django.contrib.auth.models import Permission

    permissions = []
    for dotted in sorted(ROLE_PERMISSIONS[role.key]):
        app_label, codename = dotted.split(".", 1)
        try:
            permissions.append(
                Permission.objects.using(using).get(content_type__app_label=app_label, codename=codename)
            )
        except Permission.DoesNotExist as exc:
            raise ImproperlyConfigured(
                f"Rol matrisindeki izin bulunamadı: {dotted}. `migrate` komutunu çalıştırın."
            ) from exc
    return permissions


def sync_role_groups(using: str = DEFAULT_DB_ALIAS) -> list[SyncResult]:
    """Rol gruplarını oluşturur ve izinlerini matrisle birebir eşitler.

    Tekrar çalıştırılabilir (idempotent): ikinci çalıştırmada değişiklik yapmaz.
    """
    from django.contrib.auth.models import Group

    results: list[SyncResult] = []
    with transaction.atomic(using=using):
        for role in ROLES:
            group, created = Group.objects.using(using).get_or_create(name=role.group_name)
            wanted = _resolve_permissions(role, using)
            wanted_ids = {p.pk for p in wanted}
            current_ids = set(group.permissions.values_list("pk", flat=True))
            added = wanted_ids - current_ids
            removed = current_ids - wanted_ids
            if added or removed:
                group.permissions.set(wanted)
            results.append(SyncResult(role, created, len(added), len(removed)))
    return results


def sync_role_groups_on_migrate(sender, using=DEFAULT_DB_ALIAS, verbosity=1, **kwargs):
    """post_migrate alıcısı: her `migrate` sonunda rol matrisini uygular."""
    results = sync_role_groups(using=using)
    if verbosity >= 1:
        changed = [r for r in results if r.created or r.added or r.removed]
        for r in changed:
            sys.stdout.write(
                f"  Rol grubu '{r.role.group_name}': "
                f"{'oluşturuldu' if r.created else 'güncellendi'} "
                f"(+{r.added} / -{r.removed} izin)\n"
            )
