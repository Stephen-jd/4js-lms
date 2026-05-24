import os
import django
import sys

# Add root directory to python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fourj_lms.settings')
django.setup()

from resources.models import SyllabusTracker, ResourceItem

# Query SyllabusTracker for Year 3
y3_trackers = SyllabusTracker.objects.filter(year_level="Year 3")
print(f"Total Year 3 SyllabusTracker entries: {y3_trackers.count()}")
for t in y3_trackers:
    print(f"  Subject: {t.subject} | Topic: {t.topic} | Status: {t.status}")

# Query ResourceItem for Year 3
y3_resources = ResourceItem.objects.filter(year="Year 3")
print(f"\nTotal Year 3 ResourceItem entries: {y3_resources.count()}")
for r in y3_resources:
    print(f"  Subject: {r.subject} | Topic: {r.topic} | File: {r.file_name} | Month: {r.month} ({r.week_string})")
