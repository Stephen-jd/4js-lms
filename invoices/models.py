from django.db import models
from django.contrib.auth.models import User

class TimesheetEntry(models.Model):
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timesheet_entries')
    date = models.DateField()
    subject = models.CharField(max_length=150)
    start_time = models.CharField(max_length=10, blank=True, null=True)
    end_time = models.CharField(max_length=10, blank=True, null=True)
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    rate_applied = models.DecimalField(max_digits=6, decimal_places=2)
    total_pay = models.DecimalField(max_digits=8, decimal_places=2)
    is_custom = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Auto-compute total pay prior to saving database records
        self.total_pay = self.hours * self.rate_applied
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.trainer.get_full_name() or self.trainer.username} - {self.date} - {self.subject} ({self.hours} hrs @ £{self.rate_applied})"
