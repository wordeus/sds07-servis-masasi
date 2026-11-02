"""
SDS-07 Servis Masası - Django ayarları (MOD-CFG).

İki çalışma profili vardır:

* development (varsayılan): DEBUG açık, yerel SQLite, yalnız yerel kullanım
  için sabit bir geliştirme anahtarı.
* production (DJANGO_ENV=production): DEBUG kapalı; SECRET_KEY ve
  ALLOWED_HOSTS ortam değişkeninden zorunlu; güvenli çerez ve HTTPS ayarları açık.

İlgili gereksinimler: NFR-01..NFR-06 (docs/SRS.md).
"""

import os
from pathlib import Path

from django.contrib.messages import constants as message_constants
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool) -> bool:
    """'1/true/yes/on' ve '0/false/no/off' değerlerini bool'a çevirir."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ImproperlyConfigured(f"{name} için geçersiz değer: {raw!r} (1/0 bekleniyor).")


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ImproperlyConfigured(f"{name} tam sayı olmalı: {raw!r}") from exc


def env_list(name: str, default: list[str]) -> list[str]:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


# --- Profil ---------------------------------------------------------------
DJANGO_ENV = os.environ.get("DJANGO_ENV", "development").strip().lower()
if DJANGO_ENV not in {"development", "production"}:
    raise ImproperlyConfigured("DJANGO_ENV 'development' veya 'production' olmalı.")
IS_PRODUCTION = DJANGO_ENV == "production"

DEBUG = env_bool("DJANGO_DEBUG", default=not IS_PRODUCTION)
if IS_PRODUCTION and DEBUG:
    raise ImproperlyConfigured("Üretim profilinde DJANGO_DEBUG açılamaz.")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise ImproperlyConfigured("Üretim profilinde DJANGO_SECRET_KEY ortam değişkeni tanımlanmalıdır.")
    # Yalnız yerel geliştirme içindir; üretimde kullanılamaz (yukarıdaki kontrol).
    SECRET_KEY = "django-insecure-sds07-yalniz-yerel-gelistirme-anahtari"

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    default=[] if IS_PRODUCTION else ["localhost", "127.0.0.1", "[::1]"],
)
if IS_PRODUCTION and not ALLOWED_HOSTS:
    raise ImproperlyConfigured("Üretim profilinde DJANGO_ALLOWED_HOSTS tanımlanmalıdır.")

# --- Uygulamalar ---------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "servicedesk.apps.ServicedeskConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Veritabanı (yerel geliştirmede SQLite) -------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_SQLITE_PATH", str(BASE_DIR / "db.sqlite3")),
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Kimlik doğrulama (MOD-AUTH) ------------------------------------------------
# Giriş/çıkış sayfaları Hafta 2'de eklenecek; bu hafta yalnız özel kullanıcı modeli var.
AUTH_USER_MODEL = "servicedesk.User"

# NFR-01: parolalar Django'nun varsayılan PBKDF2-SHA256 hasher'ı ile saklanır.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# NFR-03: oturum süresi bir iş günü (8 saat); oturum çerezi JavaScript'e kapalı.
SESSION_COOKIE_AGE = 8 * 60 * 60
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# --- Yerelleştirme ve zaman (NFR-05, NFR-06) ------------------------------------
LANGUAGE_CODE = "tr"
LANGUAGES = [("tr", "Türkçe")]
TIME_ZONE = "Europe/Istanbul"  # Gösterim saat dilimi
USE_I18N = True
USE_TZ = True  # Zaman damgaları veritabanında UTC olarak saklanır

# --- Statik dosyalar ---------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Bootstrap uyarı sınıflarıyla eşleşme (error -> danger)
MESSAGE_TAGS = {message_constants.ERROR: "danger"}

# --- Test koşucusu: TC kimlikli sonuçları JSON'a yazar (RTM kaynağı) ------------
TEST_RUNNER = "config.test_runner.TraceableDiscoverRunner"

# --- Üretim güvenlik ayarları (NFR-03, NFR-04) -------------------------------
if IS_PRODUCTION:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
    # HTTPS doğrulandıktan sonra 31536000 (1 yıl) değerine yükseltilmesi önerilir.
    SECURE_HSTS_SECONDS = env_int("DJANGO_SECURE_HSTS_SECONDS", 3600)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
    SECURE_HSTS_PRELOAD = False
    # Gerekçe: HSTS preload listesine başvuru bu projenin kapsamı dışında; bilinçli kapalı.
    SILENCED_SYSTEM_CHECKS = ["security.W021"]
    CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", [])
    if env_bool("DJANGO_BEHIND_TLS_PROXY", False):
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
