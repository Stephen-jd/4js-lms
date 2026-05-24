import os
import django
import sys

# Add current directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fourj_lms.settings')
django.setup()

from resources.models import SyllabusTracker, ResourceItem
from django.db.models import Count

print("=== SYLLABUS MAPPING STATISTICS ===")
total_trackers = SyllabusTracker.objects.count()
print(f"Total SyllabusTracker entries: {total_trackers}")

print("\n--- Count by Year Level and Subject ---")
groupings = SyllabusTracker.objects.values('year_level', 'subject').annotate(count=Count('id')).order_by('year_level', 'subject')
for g in groupings:
    print(f"Year: {g['year_level']:<20} | Subject: {g['subject']:<25} | Count: {g['count']}")

print("\n--- Sample Entries from Each Grouping ---")
for g in groupings[:25]:
    year = g['year_level']
    subj = g['subject']
    sample = SyllabusTracker.objects.filter(year_level=year, subject=subj).first()
    print(f"Year: {year:<15} | Subject: {subj:<25} | Sample Topic: {sample.topic if sample else 'None'}")
