import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fourj_lms.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Vercel expects a variable named `app`
app = application
