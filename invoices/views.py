from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from invoices.models import TimesheetEntry
import json
import datetime

@csrf_exempt
def api_add_timesheet(request):
    """
    Saves a new billable class session under the logged-in trainer's timesheet.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Trainer authentication session required.'}, status=403)
        try:
            data = json.loads(request.body)
            date_str = data.get('date')
            subject = data.get('subject')
            hours = data.get('hours')
            start_time = data.get('startTime', '')
            end_time = data.get('endTime', '')
            is_custom = data.get('isCustom', False)

            if not date_str or not subject or hours is None:
                return JsonResponse({'success': False, 'error': 'Missing core timesheet inputs.'}, status=400)

            date_val = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

            # Create billable log
            entry = TimesheetEntry.objects.create(
                trainer=request.user,
                date=date_val,
                subject=subject,
                hours=float(hours),
                start_time=start_time,
                end_time=end_time,
                rate_applied=request.user.profile.hourly_rate,
                is_custom=bool(is_custom)
            )

            return JsonResponse({
                'success': True,
                'entry': {
                    'id': str(entry.id),
                    'trainerId': entry.trainer.username,
                    'date': entry.date.isoformat(),
                    'subject': entry.subject,
                    'startTime': entry.start_time or '',
                    'endTime': entry.end_time or '',
                    'hours': float(entry.hours),
                    'rate': float(entry.rate_applied),
                    'totalPay': float(entry.total_pay),
                    'isCustom': entry.is_custom
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

@csrf_exempt
def api_delete_timesheet(request, log_id):
    """
    Deletes a billable timesheet session from the active trainer's ledger.
    """
    if request.method == 'DELETE':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Trainer authentication required.'}, status=403)
        try:
            entry = TimesheetEntry.objects.get(id=log_id)
            
            # Authorize deletion: must be own log, or an admin
            if entry.trainer == request.user or request.user.profile.is_admin_flag:
                entry.delete()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Unauthorized to modify this ledger entry.'}, status=403)
        except TimesheetEntry.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Timesheet entry not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'DELETE required'}, status=400)
