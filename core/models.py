from django.db import models

class ConfigItem(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()

    def __str__(self):
        return f"{self.key}: {self.value[:50]}..."

class Announcement(models.Model):
    date = models.DateField(auto_now_add=True)
    text = models.TextField()

    def __str__(self):
        return f"[{self.date}] {self.text[:50]}"
