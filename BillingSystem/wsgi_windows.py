activate_this = 'C:/Users/watersystem/AppData/Local/Programs/Python/Python310/Scripts/activate_this.py'
# execfile(activate_this, dict(__file__=activate_this))
exec(open(activate_this).read(),dict(__file__=activate_this))

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('C:/Users/watersystem/AppData/Local/Programs/Python/Python310/Lib/site-packages')




# Add the app's directory to the PYTHONPATH
sys.path.append('D:/MyBillingSystem/BillingSystem')
sys.path.append('D:/MyBillingSystem/BillingSystem/BillingSystem')

os.environ['DJANGO_SETTINGS_MODULE'] = 'BillingSystem.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BillingSystem.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
