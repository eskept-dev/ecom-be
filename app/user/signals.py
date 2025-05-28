from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from app.user.models import UserProfile, BusinessProfile


User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        if instance.is_business:
            BusinessProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
        
    try:
        if instance.is_business:
            instance.businessprofile.save()
    except BusinessProfile.DoesNotExist:
        BusinessProfile.objects.create(user=instance)


@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.delete()
    except UserProfile.DoesNotExist:
        pass

    try:
        if instance.is_business:    
            instance.businessprofile.delete()
    except BusinessProfile.DoesNotExist:
        pass
