"""
WSGI config for ui app.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

from main import debugger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

debugger.init_debugpy()

application = get_wsgi_application()  # pylint: disable=invalid-name
