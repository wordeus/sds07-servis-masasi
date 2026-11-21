"""FR-15: Başlangıç kategorileri (Hafta 3).

Veri migration'ı tekrar çalıştırılabilir: var olan kategori yeniden oluşturulmaz.
Geri alma işlemi kategorileri silmez; talebi olan kategori silinemez (PROTECT) ve
kategoriler yönetim ekranından pasifleştirilerek kullanımdan kaldırılır.
"""

from django.db import migrations

DEFAULT_CATEGORIES = (
    ("Donanım", "Bilgisayar, yazıcı ve çevre birimleri"),
    ("Yazılım", "Uygulama kurulumu, lisans ve yazılım hataları"),
    ("Ağ ve bağlantı", "İnternet, kablosuz ağ ve VPN"),
    ("Hesap ve erişim", "Parola, yetki ve hesap işlemleri"),
    ("Diğer", "Diğer kategorilere uymayan talepler"),
)


def create_default_categories(apps, schema_editor):
    category_model = apps.get_model("servicedesk", "Category")
    db = schema_editor.connection.alias
    for name, description in DEFAULT_CATEGORIES:
        category_model.objects.using(db).get_or_create(name=name, defaults={"description": description})


class Migration(migrations.Migration):
    dependencies = [
        ("servicedesk", "0003_category_ticket"),
    ]

    operations = [
        migrations.RunPython(create_default_categories, migrations.RunPython.noop),
    ]
