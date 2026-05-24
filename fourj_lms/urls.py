from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Import views from individual apps
from core import views as core_views
from accounts import views as accounts_views
from dashboard import views as dashboard_views
from resources import views as resources_views
from invoices import views as invoices_views
from parser import views as parser_views
from ai_tutor import views as ai_tutor_views

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Core Landing Page View
    path("", core_views.landing_index, name="landing"),
    
    # API endpoints matching Vite prototype
    path("api/db", core_views.api_db, name="api_db"),
    path("api/config", core_views.update_config, name="update_config"),
    
    # AJAX Authentication API
    path("api/login", accounts_views.ajax_login, name="ajax_login"),
    path("api/logout", accounts_views.ajax_logout, name="ajax_logout"),
    path("api/check-session", accounts_views.check_session, name="check_session"),
    
    # Dashboard Management API
    path("api/trainers", dashboard_views.api_add_trainer, name="add_trainer"),
    path("api/trainers/<str:trainer_id>", dashboard_views.api_delete_trainer, name="delete_trainer"),
    path("api/schedule", dashboard_views.api_add_schedule, name="add_schedule"),
    path("api/schedule/<str:slot_id>", dashboard_views.api_delete_schedule, name="delete_schedule"),
    
    # Syllabus Objectives API
    path("api/syllabus", resources_views.api_update_syllabus, name="update_syllabus"),
    path("api/resources/download", resources_views.api_download_worksheet, name="download_worksheet"),
    path("api/resources/download-all-zip", resources_views.api_download_all_zip, name="download_all_zip"),
    
    # Timesheet & Invoices API
    path("api/timesheets", invoices_views.api_add_timesheet, name="add_timesheet"),
    path("api/timesheets/<str:log_id>", invoices_views.api_delete_timesheet, name="delete_timesheet"),
    
    # Watermark Purifier Upload API
    path("api/clean-document", parser_views.api_clean_document, name="clean_document"),
    
    # Ollama Qwen AI Chatbot Proxy API
    path("api/qwen-ai", ai_tutor_views.api_qwen_ai, name="qwen_ai"),
]

# Enable media uploads & static files in developer environments
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
