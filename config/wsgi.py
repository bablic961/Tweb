import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Автоматически выполняем миграции при каждом деплое
from django.core.management import call_command
import django
django.setup()
call_command('makemigrations', '--noinput')
call_command('migrate', '--noinput')

application = get_wsgi_application()
