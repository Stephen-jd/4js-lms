from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dashboard.models import ScheduleItem
import json

@csrf_exempt
def api_add_trainer(request):
    """
    Registers a new faculty trainer under the 4J LMS platform.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated or not request.user.profile.is_admin_flag:
            return JsonResponse({'success': False, 'error': 'Admin privileges required.'}, status=403)
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            name = data.get('name', '').strip()
            password = data.get('password', '')
            subjects = data.get('subjects', ["Maths"])
            hourly_rate = data.get('hourlyRate', 45)

            if not email or not name or not password:
                return JsonResponse({'success': False, 'error': 'Missing name, email or password fields.'}, status=400)

            # Generate unique clean username
            username = email.split('@')[0].lower().replace('.', '_')
            
            # Check duplicates
            if User.objects.filter(username=username).exists() or User.objects.filter(email__iexact=email).exists():
                return JsonResponse({'success': False, 'error': 'A user with this email/username already exists.'}, status=400)

            # Split names
            parts = name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''

            # Create standard User
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Update Profile configurations
            profile = user.profile
            profile.hourly_rate = float(hourly_rate)
            profile.subjects = subjects
            profile.is_admin_flag = False
            profile.save()

            return JsonResponse({
                'success': True,
                'trainer': {
                    'id': user.username,
                    'name': user.get_full_name() or user.username,
                    'email': user.email,
                    'hourlyRate': float(profile.hourly_rate),
                    'subjects': profile.subjects
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

@csrf_exempt
def api_delete_trainer(request, trainer_id):
    """
    Unregisters a faculty trainer and automatically drops their scheduled active classes.
    """
    if request.method == 'DELETE':
        if not request.user.is_authenticated or not request.user.profile.is_admin_flag:
            return JsonResponse({'success': False, 'error': 'Admin privileges required.'}, status=403)
        try:
            user = User.objects.get(username=trainer_id)
            user.delete() # Automatically cascades and deletes their trainer profile
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Trainer not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'DELETE required'}, status=400)

@csrf_exempt
def api_add_schedule(request):
    """
    Saves a new weekly scheduled class slot linked to a specific trainer.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated or not request.user.profile.is_admin_flag:
            return JsonResponse({'success': False, 'error': 'Admin privileges required.'}, status=403)
        try:
            data = json.loads(request.body)
            trainer_id = data.get('trainerId')
            day = data.get('dayOfWeek')
            start = data.get('startTime')
            end = data.get('endTime')
            subj = data.get('subject')
            year = data.get('classYear')
            desc = data.get('description', '')

            if not trainer_id or not day or not start or not end or not subj or not year:
                return JsonResponse({'success': False, 'error': 'Missing core scheduling values.'}, status=400)

            try:
                trainer_user = User.objects.get(username=trainer_id)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Assigned trainer user does not exist.'}, status=400)

            item = ScheduleItem.objects.create(
                trainer=trainer_user,
                day_of_week=day,
                start_time=start,
                end_time=end,
                subject=subj,
                class_year=year,
                description=desc
            )

            return JsonResponse({
                'success': True,
                'item': {
                    'id': str(item.id),
                    'trainerId': item.trainer.username,
                    'trainerName': item.trainer.get_full_name() or item.trainer.username,
                    'dayOfWeek': item.day_of_week,
                    'startTime': item.start_time,
                    'endTime': item.end_time,
                    'subject': item.subject,
                    'classYear': item.class_year,
                    'description': item.description
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

@csrf_exempt
def api_delete_schedule(request, slot_id):
    """
    Deletes an active scheduled timetabling slot by ID.
    """
    if request.method == 'DELETE':
        if not request.user.is_authenticated or not request.user.profile.is_admin_flag:
            return JsonResponse({'success': False, 'error': 'Admin privileges required.'}, status=403)
        try:
            slot = ScheduleItem.objects.get(id=slot_id)
            slot.delete()
            return JsonResponse({'success': True})
        except ScheduleItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Scheduled slot not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'DELETE required'}, status=400)
