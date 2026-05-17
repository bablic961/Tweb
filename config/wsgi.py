import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Запускаем миграции автоматически
from django.core.management import call_command
from django import setup
setup()
call_command('migrate', '--noinput')

application = get_wsgi_application()
