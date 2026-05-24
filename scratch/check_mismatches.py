import os
import django
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fourj_lms.settings')
django.setup()

from resources.models import SyllabusTracker, ResourceItem

print("=== CHECKING TOPIC MISMATCHES ===")
trackers = SyllabusTracker.objects.all()
resources = ResourceItem.objects.all()

print(f"Total SyllabusTrackers: {trackers.count()}")
print(f"Total ResourceItems: {resources.count()}")

mismatch_t_to_r = []
for t in trackers:
    # Check if there is any ResourceItem matching this tracker's year, subject, and topic
    match = ResourceItem.objects.filter(year=t.year_level, subject=t.subject, topic=t.topic).exists()
    if not match:
        mismatch_t_to_r.append(t)

print(f"\nSyllabusTrackers with NO matching ResourceItem: {len(mismatch_t_to_r)}")
for t in mismatch_t_to_r[:10]:
    print(f"  Year: {t.year_level} | Subject: {t.subject} | Topic: '{t.topic}'")

mismatch_r_to_t = []
for r in resources:
    match = SyllabusTracker.objects.filter(year_level=r.year, subject=r.subject, topic=r.topic).exists()
    if not match:
        mismatch_r_to_t.append(r)

print(f"\nResourceItems with NO matching SyllabusTracker: {len(mismatch_r_to_t)}")
for r in mismatch_r_to_t[:10]:
    print(f"  Year: {r.year} | Subject: {r.subject} | Topic: '{r.topic}'")
