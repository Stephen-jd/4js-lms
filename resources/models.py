from django.db import models

class SyllabusTracker(models.Model):
    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('In Progress', 'In Progress'),
        ('Backlog', 'Backlog'),
    ]
    board = models.CharField(max_length=50) # e.g. "Edexcel", "GCSE", "AQA"
    year_level = models.CharField(max_length=50) # e.g. "Year 7", "Year 12"
    subject = models.CharField(max_length=100)
    topic = models.CharField(max_length=150)
    subtopic = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Backlog')
    last_updated = models.DateField(auto_now=True)
    covered_by = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.board} {self.year_level} {self.subject} - {self.topic} ({self.status})"

class ResourceItem(models.Model):
    syllabus_match = models.ForeignKey(SyllabusTracker, on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')
    year = models.CharField(max_length=50) # e.g. "Year 4"
    subject = models.CharField(max_length=100)
    topic = models.CharField(max_length=150)
    file_name = models.CharField(max_length=200)
    file_type = models.CharField(max_length=20) # e.g. "pdf", "docx", "pptx"
    drive_url = models.URLField(max_length=500)
    week_number = models.IntegerField(default=21)
    month = models.CharField(max_length=50, blank=True, null=True)
    week_string = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.file_name} ({self.year} {self.subject} Week {self.week_number})"

