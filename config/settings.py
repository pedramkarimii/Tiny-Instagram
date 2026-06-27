from pathlib import Path

from decouple import config


def csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"

DEBUG = config("DEBUG", cast=bool, default=False)
SECRET_KEY = config("SECRET_KEY")
TIME_ZONE = config("TIME_ZONE", default="UTC")

default_allowed_hosts = "localhost,127.0.0.1" if DEBUG else ""
ALLOWED_HOSTS = csv(config("ALLOWED_HOSTS", default=default_allowed_hosts))
CSRF_TRUSTED_ORIGINS = csv(config("CSRF_TRUSTED_ORIGINS", default=""))

USE_TZ = True
USE_I18N = True
LANGUAGE_CODE = "en-us"

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
AUTH_USER_MODEL = "account.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "ckeditor",
    "app.account",
    "app.post",
    "app.core",
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

if config("ENABLE_ERROR_REDIRECT_MIDDLEWARE", cast=bool, default=False):
    MIDDLEWARE.append("app.core.middlewares.LoginRequiredMiddleware")

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "app.account.authenticate.EmailAuthBackend",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "template"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", cast=int, default=5432),
    },
}

REDIS_HOST = config("REDIS_HOST", default="redis")
REDIS_PORT = config("REDIS_PORT", cast=int, default=6379)
REDIS_URL = config("REDIS_URL", default=f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    },
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "storage" / "static_collected"
STATICFILES_DIRS = [BASE_DIR / "storage" / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "storage" / "media"

default_storage_backend = config(
    "DEFAULT_FILE_STORAGE",
    default="django.core.files.storage.FileSystemStorage",
)

STORAGES = {
    "default": {"BACKEND": default_storage_backend},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL", default="")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_FILE_OVERWRITE = config("AWS_S3_FILE_OVERWRITE", cast=bool, default=False)
AWS_SERVICE_NAME = config("AWS_SERVICE_NAME", default="s3")

LOG_FILE_PATH = config("LOG_FILE_PATH", default="/tmp/tiny-instagram.log")

email_prefix = "DEBUG_" if DEBUG else ""
EMAIL_BACKEND = config(
    f"{email_prefix}EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_USE_TLS = config(f"{email_prefix}EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_USE_SSL = config(f"{email_prefix}EMAIL_USE_SSL", cast=bool, default=False)
EMAIL_HOST = config(f"{email_prefix}EMAIL_HOST", default="localhost")
EMAIL_PORT = config(f"{email_prefix}EMAIL_PORT", cast=int, default=1025)
EMAIL_HOST_USER = config(f"{email_prefix}EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config(f"{email_prefix}EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(f"{email_prefix}DEFAULT_FROM_EMAIL", default="dev@example.com")

X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_CONTENT_TYPE_NOSNIFF = True

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", cast=bool, default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
