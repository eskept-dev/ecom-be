from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from app.auth.tasks import send_activation_email_task


User = get_user_model()


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        send_activation_email_task.delay(instance.id)
