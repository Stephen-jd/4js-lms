import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fourj_lms.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import TrainerProfile
from core.models import ConfigItem, Announcement
from dashboard.models import ScheduleItem
from resources.models import SyllabusTracker, ResourceItem
from invoices.models import TimesheetEntry
import datetime

def seed():
    print("Starting 4J LMS Database Seeding...")

    # 1. Clear Existing Data to prevent duplicate items
    print("Clearing existing data...")
    User.objects.exclude(username='admin').delete()
    ConfigItem.objects.all().delete()
    Announcement.objects.all().delete()
    ScheduleItem.objects.all().delete()
    SyllabusTracker.objects.all().delete()
    ResourceItem.objects.all().delete()
    TimesheetEntry.objects.all().delete()

    # Create Admin user if not exists
    admin_user, created = User.objects.get_or_create(username='admin')
    if created or not admin_user.is_superuser:
        admin_user.email = 'admin@4j.com'
        admin_user.set_password('admin')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print("Admin user created.")

    # Configure Admin profile
    admin_profile = admin_user.profile
    admin_profile.is_admin_flag = True
    admin_profile.hourly_rate = 0.00
    admin_profile.subjects = []
    admin_profile.save()

    # 2. Create Trainer Users
    trainers_data = [
        {
            'username': 'stephen',
            'first_name': 'Stephen',
            'last_name': 'Jebadurai G',
            'email': 'stephenjdurai@gmail.com',
            'password': 'stephen',
            'hourly_rate': 45.00,
            'subjects': ["Maths", "Biology", "Physics", "Chemistry", "English", "Mechanics"]
        },
        {
            'username': 'riaz',
            'first_name': 'Riaz',
            'last_name': 'G',
            'email': 'riaz@4j.com',
            'password': 'password123',
            'hourly_rate': 40.00,
            'subjects': ["Maths", "English"]
        },
        {
            'username': 'alex',
            'first_name': 'Alex',
            'last_name': 'Turner',
            'email': 'alex@4j.com',
            'password': 'password123',
            'hourly_rate': 42.00,
            'subjects': ["Maths", "Physics", "Mechanics"]
        }
    ]

    trainer_objects = {}
    for trainer_info in trainers_data:
        user = User.objects.create_user(
            username=trainer_info['username'],
            email=trainer_info['email'],
            password=trainer_info['password'],
            first_name=trainer_info['first_name'],
            last_name=trainer_info['last_name']
        )
        profile = user.profile
        profile.hourly_rate = trainer_info['hourly_rate']
        profile.subjects = trainer_info['subjects']
        profile.is_admin_flag = False
        profile.save()
        trainer_objects[trainer_info['username']] = user
        print(f"Trainer created: {user.get_full_name()}")

    # 3. Create Configurations
    ConfigItem.objects.create(key='total_students', value='148')
    ConfigItem.objects.create(
        key='about_academy_text',
        value="Welcome to 4J's Educational Academy. We are structured to offer absolute dedication in high-standard tuition, specializing in the UK National Curriculum boards including GCSE, Edexcel, AQA, and OCR. Utilizing fully tested syllabus tracking guides alongside top-tier curated resources, our experienced trainers ensure that Year 3 to Year 13 students reach maximum academic heights."
    )
    print("Configurations seeded.")

    # 4. Create Announcements
    Announcement.objects.create(text="New resource folder matching Edexcel Maths Year 12 Mechanics is now active.")
    Announcement.objects.create(text="Trainer invoicing cycle reminder: Invoices automatically compiled from 26th of previous month to 25th of current month.")
    print("Announcements seeded.")

    # 5. Create Schedules (Stephen's Exact Calendar)
    schedules_data = [
        # Monday
        { 'trainer_key': 'stephen', 'day': 'Monday', 'start': '18:00', 'end': '19:00', 'subj': 'Maths', 'year': 'Year 7', 'desc': 'Year 7 Maths' },
        # Tuesday
        { 'trainer_key': 'stephen', 'day': 'Tuesday', 'start': '16:30', 'end': '18:00', 'subj': 'Biology', 'year': 'Year 8', 'desc': 'Year 8 Biology' },
        { 'trainer_key': 'stephen', 'day': 'Tuesday', 'start': '18:00', 'end': '19:00', 'subj': 'Maths', 'year': 'Year 7', 'desc': 'Year 7 Maths' },
        { 'trainer_key': 'stephen', 'day': 'Tuesday', 'start': '19:30', 'end': '21:00', 'subj': 'Mechanics Maths', 'year': 'Year 12', 'desc': 'Year 12 Mechanic Maths' },
        # Wednesday
        { 'trainer_key': 'stephen', 'day': 'Wednesday', 'start': '16:30', 'end': '18:00', 'subj': 'English', 'year': 'Year 4', 'desc': 'Year 4 English' },
        { 'trainer_key': 'stephen', 'day': 'Wednesday', 'start': '18:00', 'end': '19:00', 'subj': 'Maths', 'year': 'Year 7', 'desc': 'Year 7 Maths' },
        # Thursday
        { 'trainer_key': 'stephen', 'day': 'Thursday', 'start': '16:30', 'end': '18:00', 'subj': 'English', 'year': 'Year 4', 'desc': 'Year 4 English' },
        { 'trainer_key': 'stephen', 'day': 'Thursday', 'start': '18:00', 'end': '19:00', 'subj': 'Maths', 'year': 'Year 7', 'desc': 'Year 7 Maths' },
        # Friday
        { 'trainer_key': 'stephen', 'day': 'Friday', 'start': '16:30', 'end': '18:00', 'subj': 'Physics', 'year': 'Year 8', 'desc': 'Year 8 Physics' },
        # Saturday
        { 'trainer_key': 'stephen', 'day': 'Saturday', 'start': '08:30', 'end': '10:00', 'subj': 'Physics', 'year': 'Year 12', 'desc': 'Year 12 Physics' },
        { 'trainer_key': 'stephen', 'day': 'Saturday', 'start': '10:00', 'end': '11:00', 'subj': 'Maths', 'year': 'Year 4', 'desc': 'Year 4 Maths' },
        # Sunday
        { 'trainer_key': 'stephen', 'day': 'Sunday', 'start': '11:00', 'end': '12:00', 'subj': 'Maths', 'year': 'Year 4', 'desc': 'Year 4 Maths' }
    ]

    for slot in schedules_data:
        ScheduleItem.objects.create(
            trainer=trainer_objects[slot['trainer_key']],
            day_of_week=slot['day'],
            start_time=slot['start'],
            end_time=slot['end'],
            subject=slot['subj'],
            class_year=slot['year'],
            description=slot['desc']
        )
    print("Schedules seeded successfully.")

    # 6. Create Syllabus Trackers
    syllabus_data = [
        { 'board': 'Edexcel', 'year': 'Year 7', 'subj': 'Maths', 'topic': 'Algebra Foundation', 'sub': 'Simplifying Expressions & Equations', 'status': 'Completed', 'by': 'Stephen Jebadurai G' },
        { 'board': 'GCSE', 'year': 'Year 8', 'subj': 'Biology', 'topic': 'Organisms', 'sub': 'Digestive and Respiratory systems', 'status': 'In Progress', 'by': 'Stephen Jebadurai G' },
        { 'board': 'GCSE', 'year': 'Year 8', 'subj': 'Physics', 'topic': 'Force Interactions', 'sub': 'Resultant forces and Friction Work', 'status': 'In Progress', 'by': 'Stephen Jebadurai G' },
        { 'board': 'Edexcel', 'year': 'Year 12', 'subj': 'Mechanics Maths', 'topic': 'Kinematics', 'sub': 'Constant Acceleration (SUVAT equations)', 'status': 'In Progress', 'by': 'Stephen Jebadurai G' },
        { 'board': 'GCSE', 'year': 'Year 4', 'subj': 'Maths', 'topic': 'Number & Fractions', 'sub': 'Decimals and Equivalence Fractions', 'status': 'Completed', 'by': 'Stephen Jebadurai G' },
        { 'board': 'GCSE', 'year': 'Year 4', 'subj': 'English', 'topic': 'Reading & Grammar', 'sub': 'Punctuation alignment & sentence stress', 'status': 'In Progress', 'by': 'Stephen Jebadurai G' }
    ]

    syllabus_objects = []
    for item in syllabus_data:
        tracker = SyllabusTracker.objects.create(
            board=item['board'],
            year_level=item['year'],
            subject=item['subj'],
            topic=item['topic'],
            subtopic=item['sub'],
            status=item['status'],
            covered_by=item['by']
        )
        syllabus_objects.append(tracker)
    print("Syllabus tracking sheets seeded.")

    # 7. Create Resource items and match with Syllabus
    resources_data = [
        { 'year': 'Year 4', 'subj': 'Maths', 'topic': 'Fractions & Decimals', 'file': 'Y4_Maths_Fractions_GuidedClasswork.pdf', 'type': 'pdf', 'week': 21 },
        { 'year': 'Year 7', 'subj': 'Maths', 'topic': 'Linear Equations', 'file': 'Y7_Algebra_LinearEquations_Exercises.docx', 'type': 'docx', 'week': 21 },
        { 'year': 'Year 8', 'subj': 'Biology', 'topic': 'Digestive System Structure', 'file': 'Y8_Biology_Digestive_Slides.pptx', 'type': 'pptx', 'week': 21 },
        { 'year': 'Year 8', 'subj': 'Chemistry', 'topic': 'Atomic Structure & Elements', 'file': 'Y8_Chemistry_AtomicSpecSheet.pdf', 'type': 'pdf', 'week': 21 },
        { 'year': 'Year 8', 'subj': 'Physics', 'topic': 'Energy Conservation & Flow', 'file': 'Y8_Physics_EnergyEfficiency.pdf', 'type': 'pdf', 'week': 21 },
        { 'year': 'Year 12', 'subj': 'Physics', 'topic': 'Mechanic forces & Vectors', 'file': 'Y12_Forces_VectorResolutions.pdf', 'type': 'pdf', 'week': 21 },
        { 'year': 'Year 12', 'subj': 'Mechanics Maths', 'topic': 'Static Equilibriums', 'file': 'Y12_Mech_Statics_Guide.pdf', 'type': 'pdf', 'week': 21 }
    ]

    drive_base_url = "https://drive.google.com/drive/folders/1A448PqDCSgx0D09MjoBN7pmhs9vTS1eq"

    for r_item in resources_data:
        # Try to find a matching syllabus item
        match = None
        for s in syllabus_objects:
            if s.year_level == r_item['year'] and s.subject.lower() in r_item['subj'].lower():
                match = s
                break

        ResourceItem.objects.create(
            syllabus_match=match,
            year=r_item['year'],
            subject=r_item['subj'],
            topic=r_item['topic'],
            file_name=r_item['file'],
            file_type=r_item['type'],
            drive_url=drive_base_url,
            week_number=r_item['week']
        )
    print("Resources folder references seeded.")

    # 8. Create Timesheet Entries
    timesheets_data = [
        { 'date': '2026-05-04', 'subj': 'Year 7 Maths', 'hrs': 1.0, 'is_custom': False },
        { 'date': '2026-05-05', 'subj': 'Year 8 Biology', 'hrs': 1.5, 'is_custom': False },
        { 'date': '2026-05-05', 'subj': 'Year 7 Maths', 'hrs': 1.0, 'is_custom': False },
        { 'date': '2026-05-05', 'subj': 'Year 12 Mechanics Maths', 'hrs': 1.5, 'is_custom': False },
        { 'date': '2026-05-06', 'subj': 'Year 4 English', 'hrs': 1.5, 'is_custom': False },
        { 'date': '2026-05-06', 'subj': 'Year 7 English', 'hrs': 1.0, 'is_custom': False }
    ]

    stephen_user = trainer_objects['stephen']
    for t_entry in timesheets_data:
        date_obj = datetime.datetime.strptime(t_entry['date'], '%Y-%m-%d').date()
        TimesheetEntry.objects.create(
            trainer=stephen_user,
            date=date_obj,
            subject=t_entry['subj'],
            hours=t_entry['hrs'],
            rate_applied=stephen_user.profile.hourly_rate,
            is_custom=t_entry['is_custom']
        )
    print("Timesheet entries seeded successfully.")
    print("Database seeding completed successfully! All 4J LMS data is active.")

if __name__ == '__main__':
    seed()
