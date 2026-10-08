from datetime import timedelta
from pathlib import Path
from decouple import config
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("SECRET_KEY", default="dev-only-change-me")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*").split(",")

INSTALLED_APPS = [
    "unfold",  # thème de l'administration (doit précéder django.contrib.admin)
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "rest_framework", "corsheaders", "drf_spectacular",
    "accounts", "schools", "courses", "quizzes", "payments",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"

if config("USE_SQLITE", default=False, cast=bool):
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
else:
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DB_NAME", default="elearning"),
        "USER": config("DB_USER", default="root"),
        "PASSWORD": config("DB_PASSWORD", default="1234"),
        "HOST": config("DB_HOST", default="127.0.0.1"),
        "PORT": config("DB_PORT", default="3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    }}

AUTH_USER_MODEL = "accounts.User"
LANGUAGE_CODE = "fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(hours=2), "REFRESH_TOKEN_LIFETIME": timedelta(days=7)}
SPECTACULAR_SETTINGS = {"TITLE": "E-Learning API", "VERSION": "1.0.0", "SERVE_INCLUDE_SCHEMA": False}
CORS_ALLOW_ALL_ORIGINS = DEBUG

# ---------- Thème de l'administration (django-unfold) ----------
def _nav(title, icon, name):
    return {"title": title, "icon": icon, "link": reverse_lazy(f"admin:{name}_changelist")}

UNFOLD = {
    "SITE_TITLE": "École en ligne",
    "SITE_HEADER": "École en ligne",
    "SITE_SUBHEADER": "Administration",
    "SITE_SYMBOL": "school",
    "SITE_URL": "/",
    "DASHBOARD_CALLBACK": "config.dashboard.dashboard_callback",
    "COLORS": {"primary": {
        "50": "oklch(98.4% .014 180.72)", "100": "oklch(95.3% .051 180.801)",
        "200": "oklch(91% .096 180.426)", "300": "oklch(85.5% .138 181.071)",
        "400": "oklch(77.7% .152 181.912)", "500": "oklch(70.4% .14 182.503)",
        "600": "oklch(60% .118 184.704)", "700": "oklch(51.1% .096 186.391)",
        "800": "oklch(43.7% .078 188.216)", "900": "oklch(38.6% .063 188.416)",
        "950": "oklch(27.7% .046 192.524)",
    }},
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {"title": "Pilotage", "items": [
                {"title": "Tableau de bord", "icon": "dashboard", "link": reverse_lazy("admin:index")},
                {"title": "Retour au site", "icon": "home", "link": "/"},
            ]},
            {"title": "Établissement", "items": [
                _nav("Écoles", "school", "schools_school"),
                _nav("Classes", "meeting_room", "schools_classroom"),
                _nav("Inscriptions", "how_to_reg", "schools_enrollment"),
            ]},
            {"title": "Pédagogie", "items": [
                _nav("Cours", "menu_book", "courses_course"),
                _nav("Leçons", "play_lesson", "courses_lesson"),
                _nav("Quiz", "quiz", "quizzes_quiz"),
                _nav("Questions", "help", "quizzes_question"),
                _nav("Résultats", "grading", "quizzes_attempt"),
            ]},
            {"title": "Finances", "items": [
                _nav("Frais de scolarité", "request_quote", "payments_fee"),
                _nav("Paiements", "payments", "payments_payment"),
            ]},
            {"title": "Accès", "items": [
                _nav("Utilisateurs", "group", "accounts_user"),
                _nav("Groupes", "admin_panel_settings", "auth_group"),
            ]},
        ],
    },
}
