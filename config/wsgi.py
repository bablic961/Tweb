import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создаём все таблицы при запуске
import django
django.setup()
from django.core.management import call_command
call_command('migrate', '--run-syncdb', '--noinput')

application = get_wsgi_application()
