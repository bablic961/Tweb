import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Выполняем миграции
import django
django.setup()
from django.core.management import call_command
call_command('migrate', '--noinput')

application = get_wsgi_application()
