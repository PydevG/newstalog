from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile, Blog

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        print(f"Profile created for {instance.username}")

# Signal to delete a profile when a user is deleted
@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.delete()
        print(f"Profile deleted for {instance.username}")
    except Profile.DoesNotExist:
        print(f"No profile found for {instance.username}")
        
        
@receiver(post_delete, sender=Blog)
def delete_post_image(sender, instance, **kwargs):
    try:
        instance.image.delete()
        print(f"image deleted")
    except Profile.DoesNotExist:
        print(f"No image found")


