from django.db import models
from django.contrib.auth.models import User

class ScheduleItem(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule_slots')
    day_of_week = models.CharField(max_length=15, choices=DAYS_OF_WEEK)
    start_time = models.CharField(max_length=10) # e.g. "18:00" or "04:30 pm"
    end_time = models.CharField(max_length=10)   # e.g. "19:00" or "6:00 pm"
    subject = models.CharField(max_length=100)
    class_year = models.CharField(max_length=50) # e.g. "Year 7"
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.trainer.get_full_name() or self.trainer.username} - {self.day_of_week} ({self.start_time} - {self.end_time}) {self.class_year} {self.subject}"
