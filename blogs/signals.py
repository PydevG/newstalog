from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile, Blog, Badge, UserBadge, Comment

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
    if instance.image:
        instance.image.delete(save=False)  # Ensure safe deletion


@receiver(post_save, sender=Blog)
def check_post_badges(sender, instance, created, **kwargs):
    if created:
        user = instance.author
        post_count = Post.objects.filter(author=user).count()

        for badge in Badge.objects.filter(criteria="posts"):
            if post_count >= badge.threshold:
                UserBadge.objects.get_or_create(user=user, badge=badge)

@receiver(post_save, sender=Comment)
def check_comment_badges(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        comment_count = Comment.objects.filter(user=user).count()

        for badge in Badge.objects.filter(criteria="comments"):
            if comment_count >= badge.threshold:
                UserBadge.objects.get_or_create(user=user, badge=badge)