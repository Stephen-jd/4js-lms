from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def ajax_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            password = data.get('password', '')

            if not email or not password:
                return JsonResponse({'success': False, 'error': 'Please provide email and password.'}, status=400)

            # Find standard User by email field
            try:
                user_obj = User.objects.get(email__iexact=email)
                username = user_obj.username
            except User.DoesNotExist:
                # If no matching email, try username match
                username = email

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': user.username,
                        'name': user.get_full_name() or user.username,
                        'email': user.email,
                        'role': 'admin' if user.profile.is_admin_flag else 'trainer',
                        'hourlyRate': float(user.profile.hourly_rate),
                        'subjects': user.profile.subjects
                    }
                })
            else:
                return JsonResponse({'success': False, 'error': 'Invalid credentials.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

def ajax_logout(request):
    logout(request)
    return JsonResponse({'success': True})

def check_session(request):
    """
    Checks if a user is currently logged in, and returns user metadata.
    """
    if request.user.is_authenticated:
        user = request.user
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': user.username,
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'role': 'admin' if user.profile.is_admin_flag else 'trainer',
                'hourlyRate': float(user.profile.hourly_rate),
                'subjects': user.profile.subjects
            }
        })
    return JsonResponse({'authenticated': False})
