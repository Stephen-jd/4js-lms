from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class TrainerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, default=45.00)
    subjects = models.JSONField(default=list, blank=True)
    is_admin_flag = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({'Admin' if self.is_admin_flag else 'Trainer'})"

# Signal handlers to ensure a profile is created alongside every User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        TrainerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Ensure profile exists before saving
    if not hasattr(instance, 'profile'):
        TrainerProfile.objects.create(user=instance)
    instance.profile.save()
