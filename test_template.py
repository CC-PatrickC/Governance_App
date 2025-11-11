import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_intake.settings')
django.setup()

from django.template.loader import get_template
try:
    template = get_template('projects/my_governance.html')
    print('✅ Template loads successfully - READY TO DEPLOY!')
except Exception as e:
    print(f'❌ Template error: {e}')