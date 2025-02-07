"""
WSGI config for equ project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

env = os.getenv("DJANGO_ENV", "production")  # В продакшене грузим production
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"equ.settings.{env}")

application = get_wsgi_application()