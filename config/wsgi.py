"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

BASE_DIR = Path(__file__).resolve().parent.parent

application = get_wsgi_application()

staticfiles_dir = BASE_DIR / 'staticfiles'
static_dir = BASE_DIR / 'static'

if staticfiles_dir.exists():
    application = WhiteNoise(application, root=str(staticfiles_dir))
else:
    application = WhiteNoise(application, root=str(static_dir))

if static_dir.exists():
    application.add_files(str(static_dir))


app = application


