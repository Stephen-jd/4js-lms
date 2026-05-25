"""
Django settings for fourj_lms project.
Production-ready configuration for Vercel serverless deployment.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY — use environment variable on Vercel, fallback for local dev
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-_lo3t!cp++o4u7-#$@wyo=7gf+ww6vsvw^zpn9huvt18ic^cxl"
)

# Debug: off in production (Vercel sets VERCEL=1)
DEBUG = os.environ.get("VERCEL", "") == "" 

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".vercel.app",
    ".now.sh",
    "*",  # Allow all for Vercel serverless
]

# CSRF trusted origins for Vercel domains
CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://*.now.sh",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 4J LMS Core modular applications
    "accounts",
    "core",
    "dashboard",
    "resources",
    "invoices",
    "parser",
    "ai_tutor",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # WhiteNoise for static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fourj_lms.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "fourj_lms.wsgi.application"

# Database — SQLite for local, can be overridden via DATABASE_URL on Vercel
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/tmp/db.sqlite3" if os.environ.get("VERCEL") else BASE_DIR / "db.sqlite3",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/London"  # Unified UK standard timezone
USE_I18N = True
USE_TZ = True

# Static files — WhiteNoise serves them directly from staticfiles/
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise compressed static file storage
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media Files (Worksheets uploading — in-memory only on Vercel serverless)
MEDIA_URL = "/media/"
MEDIA_ROOT = "/tmp/media" if os.environ.get("VERCEL") else BASE_DIR / "media"

# Session & Auth redirect pathways
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Gemini API Key configuration for secure fallback chat query runs
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
