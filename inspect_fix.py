import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enterprise_system.settings')
django.setup()

from django.core.management import call_command

# Run inspectdb and capture output
with open('core/models.py', 'w', encoding='utf-8') as f:
    call_command('inspectdb', stdout=f)

print("Models generated successfully in core/models.py")
