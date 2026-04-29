"""
Development settings — extends base.
Optimised for local Docker Compose workflow.
"""
from .base import *  # noqa: F401,F403

from decouple import config

# ─────────────────────────────────────────────
# Debug
# ─────────────────────────────────────────────
DEBUG = True

ALLOWED_HOSTS = ["*"]

# ─────────────────────────────────────────────
# CORS — allow all origins in development
# ─────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ─────────────────────────────────────────────
# Email — console backend (prints to terminal)
# ─────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ─────────────────────────────────────────────
# Caches — Redis via django-redis
# ─────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://redis:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# ─────────────────────────────────────────────
# Django Debug Toolbar
# ─────────────────────────────────────────────
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405

MIDDLEWARE.insert(  # noqa: F405
    MIDDLEWARE.index("django.middleware.common.CommonMiddleware") + 1,  # noqa: F405
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)

INTERNAL_IPS = [
    "127.0.0.1",
    "172.0.0.0/8",  # Docker bridge networks
]

# django-debug-toolbar: show toolbar for Docker containers
# (requests come from the Docker gateway IP, not 127.0.0.1)
import socket

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]
