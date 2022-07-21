
import os

import sys

import site

from django.core.wsgi import get_wsgi_application

# Add the app’s directory to the PYTHONPATH

sys.path.append('D:/MyBillingSystem/BillingSystem')

sys.path.append('D:/MyBillingSystem/BillingSystem/BillingSystem')

os.environ['DJANGO_SETTINGS_MODULE'] = "BillingSystem.settings"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BillingSystem.settings')

application = get_wsgi_application()


