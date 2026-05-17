import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Автоматически создаём таблицы при запуске
from django.core.management import call_command
import django
django.setup()
call_command('migrate', '--noinput')

application = get_wsgi_application()
