import os
import django
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fourj_lms.settings')
django.setup()

from resources.models import SyllabusTracker, ResourceItem

print("=== CHECKING SQLite DATABASE SYLLABUS MAPPINGS ===")
all_trackers = SyllabusTracker.objects.all()

weird_mappings = []
for t in all_trackers:
    res_items = ResourceItem.objects.filter(syllabus_match=t)
    for r in res_items:
        if r.topic.upper() in ["NA", "PENDING", "TOPIC", "YEAR", "WEEK", ""]:
            weird_mappings.append(f"Weird topic in DB: Year={r.year}, Subject={r.subject}, Topic={r.topic}, Month={r.month}")

print(f"Total weird topics (NA/empty/placeholders): {len(weird_mappings)}")
for w in weird_mappings[:15]:
    print(w)
