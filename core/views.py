from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from core.models import ConfigItem, Announcement
from dashboard.models import ScheduleItem
from resources.models import SyllabusTracker, ResourceItem
from invoices.models import TimesheetEntry
import json

@ensure_csrf_cookie
def landing_index(request):
    """
    Renders the beautiful White & Gold 4J LMS Core Landing Hub.
    """
    return render(request, 'core/landing.html')

def api_db(request):
    """
    Unified database syncer mimicking /api/db for rich client layouts.
    """
    try:
        # Load Configurations
        total_students_item, _ = ConfigItem.objects.get_or_create(key='total_students', defaults={'value': '148'})
        about_text_item, _ = ConfigItem.objects.get_or_create(
            key='about_academy_text', 
            defaults={'value': "Welcome to 4J's Educational Academy. We are structured to offer absolute dedication in high-standard tuition, specializing in the UK National Curriculum boards including GCSE, Edexcel, AQA, and OCR."}
        )

        announcements = []
        for a in Announcement.objects.all().order_by('-id'):
            announcements.append({
                'id': str(a.id),
                'date': a.date.isoformat(),
                'text': a.text
            })

        config = {
            'totalStudents': int(total_students_item.value),
            'aboutText': about_text_item.value,
            'announcements': announcements
        }

        # Trainers list
        trainers = []
        for user in User.objects.exclude(username='admin'):
            trainers.append({
                'id': user.username,
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'password': 'password123',  # Keep mock schema compatibility
                'hourlyRate': float(user.profile.hourly_rate),
                'subjects': user.profile.subjects
            })

        # Scheduled live slots
        schedule = []
        for s in ScheduleItem.objects.all():
            schedule.append({
                'id': str(s.id),
                'trainerId': s.trainer.username,
                'trainerName': s.trainer.get_full_name() or s.trainer.username,
                'dayOfWeek': s.day_of_week,
                'startTime': s.start_time,
                'endTime': s.end_time,
                'subject': s.subject,
                'classYear': s.class_year,
                'description': s.description
            })

        # Worksheets Resources
        resources = []
        for r in ResourceItem.objects.all():
            resources.append({
                'id': str(r.id),
                'year': r.year,
                'subject': r.subject,
                'topic': r.topic,
                'fileName': r.file_name,
                'fileType': r.file_type,
                'driveUrl': r.drive_url,
                'weekNum': r.week_number,
                'month': r.month or "",
                'weekString': r.week_string or ""
            })

        # Syllabus trackers
        syllabus = []
        for sy in SyllabusTracker.objects.all():
            syllabus.append({
                'id': str(sy.id),
                'board': sy.board,
                'year': sy.year_level,
                'subject': sy.subject,
                'topic': sy.topic,
                'subtopic': sy.subtopic,
                'status': sy.status,
                'lastUpdated': sy.last_updated.isoformat(),
                'coveredBy': sy.covered_by or ""
            })

        # Billable Timesheets
        timesheets = []
        for t in TimesheetEntry.objects.all():
            timesheets.append({
                'id': str(t.id),
                'trainerId': t.trainer.username,
                'date': t.date.isoformat(),
                'subject': t.subject,
                'startTime': t.start_time or '',
                'endTime': t.end_time or '',
                'hours': float(t.hours),
                'rate': float(t.rate_applied),
                'totalPay': float(t.total_pay),
                'isCustom': t.is_custom
            })

        db_data = {
            'config': config,
            'trainers': trainers,
            'schedule': schedule,
            'resources': resources,
            'syllabus': syllabus,
            'timesheets': timesheets
        }
        return JsonResponse(db_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def update_config(request):
    """
    Allows Admin users to customize profile configurations.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated or not request.user.profile.is_admin_flag:
            return JsonResponse({'success': False, 'error': 'Admin permissions required'}, status=403)

        try:
            data = json.loads(request.body)
            about_text = data.get('aboutText')
            total_students = data.get('totalStudents')

            if about_text is not None:
                item, _ = ConfigItem.objects.get_or_create(key='about_academy_text')
                item.value = about_text
                item.save()

            if total_students is not None:
                item, _ = ConfigItem.objects.get_or_create(key='total_students')
                item.value = str(total_students)
                item.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)
