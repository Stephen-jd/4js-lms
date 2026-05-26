import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fourj_lms.settings')

import django
django.setup()

# Database initialization for Vercel Serverless environment
if os.environ.get("VERCEL"):
    db_path = "/tmp/db.sqlite3"
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        print("Vercel: /tmp/db.sqlite3 not found or empty. Running migrations...")
        from django.core.management import call_command
        try:
            call_command('migrate', interactive=False)
            print("Vercel migrations completed successfully.")
        except Exception as e:
            print(f"Vercel migration error: {e}")

        # Run database seeders
        try:
            import seed_data
            seed_data.seed()
            print("Vercel database seeding completed.")
        except Exception as e:
            print(f"Error seeding data on Vercel: {e}")
            
        try:
            import seed_syllabus
            seed_syllabus.seed()
            print("Vercel syllabus seeding completed.")
        except Exception as e:
            print(f"Error seeding syllabus on Vercel: {e}")

        # Enforce simple correct credentials for admin and trainer
        from django.contrib.auth.models import User
        try:
            # Admin User -> admin / admin
            admin_user, _ = User.objects.get_or_create(username='admin')
            admin_user.email = 'admin@4j.com'
            admin_user.set_password('admin')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            admin_profile = admin_user.profile
            admin_profile.is_admin_flag = True
            admin_profile.save()
            
            # Stephen User -> stephen / stephen
            stephen_user, _ = User.objects.get_or_create(username='stephen')
            stephen_user.email = 'stephenjdurai@gmail.com'
            stephen_user.set_password('stephen')
            stephen_user.save()
            stephen_profile = stephen_user.profile
            stephen_profile.is_admin_flag = False
            stephen_profile.save()
            print("Vercel user credentials set: admin/admin and stephen/stephen.")
        except Exception as e:
            print(f"Error setting custom user credentials on Vercel: {e}")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Vercel expects a variable named `app`
app = application
