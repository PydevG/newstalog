from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.timezone import now
import uuid
from ckeditor.fields import RichTextField
import os
from django.db.models.signals import pre_save
from django.dispatch import receiver
from PIL import Image
import os
from django.core.files import File
from io import BytesIO
from django.core.files.base import ContentFile


# User = get_user_model()

# Create your models here.
CATEGORY_CHOICES = [
        ('TECH', 'Technology'),
        ('SCIENCE', 'Science'),
        ('BUSINESS', 'Business'),
        ('FINANCE', 'Finance'),
        ('HEALTH', 'Health & Wellness'),
        ('EDUCATION', 'Education'),
        ('LIFESTYLE', 'Lifestyle'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('SPORTS', 'Sports'),
        ('TRAVEL', 'Travel'),
        ('FOOD', 'Food & Cooking'),
        ('PERSONAL', 'Personal Development'),
        ('CAREER', 'Career & Work'),
        ('NEWS', 'News & Current Affairs'),
        ('OPINION', 'Opinion & Commentary'),
        ('OTHER', 'Other'),
    ]


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'
    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    



class Blog(models.Model):
    title = models.CharField(max_length=150)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='blogs', default='', blank=True)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField('Tag', related_name='blogs', blank=True)
    is_published = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_headline = models.BooleanField(default=False)
    to_slide = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_updated = models.BooleanField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            count = 1
            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug

        # Ensure that self.pk exists before checking previous data
        if self.pk:
            original = Blog.objects.filter(pk=self.pk).first()
            if original:
                if original.content != self.content or original.title != self.title:
                    self.is_published = False
                    self.is_approved = False
                    self.rejection_reason = None  # Clear rejection reason on update

        # Handle image conversion only if a new image is uploaded
        if self.image and not self.image.name.endswith(".webp"):
            img_path = self.image.path

            try:
                img = Image.open(img_path)

                # Convert to WEBP
                webp_io = BytesIO()
                img.save(webp_io, "WEBP", quality=80)

                # Generate new filename
                webp_filename = os.path.splitext(self.image.name)[0] + ".webp"

                # Replace the image in the model
                self.image.save(webp_filename, ContentFile(webp_io.getvalue()), save=False)

                # Delete the original image
                if os.path.exists(img_path):
                    os.remove(img_path)

            except FileNotFoundError:
                print(f"File {img_path} not found, skipping conversion.")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



        
class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('blog', 'author')  # Ensures one comment per user per blog
    

    def __str__(self):
        return f'Comment by {self.author} on {self.blog}'
    
    
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    x = models.CharField(max_length=100, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)   
    tiktok = models.CharField(max_length=100, blank=True, null=True)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    


    def __str__(self):
        return f'{self.user.username} Profile'


    
# Auto-delete old profile picture when a new one is uploaded
@receiver(pre_save, sender=Profile)
def delete_old_profile_picture(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_profile = Profile.objects.get(pk=instance.pk)
            if old_profile.profile_picture and old_profile.profile_picture != instance.profile_picture:
                if os.path.isfile(old_profile.profile_picture.path):
                    os.remove(old_profile.profile_picture.path)
        except Profile.DoesNotExist:
            pass




class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    replied_status = models.BooleanField(default=False)

    def __str__(self):
        return f'Message from {self.name}'




class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=8, unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_premium = models.BooleanField(default=False)  # New field for premium status
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set', 
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',
        blank=True
    )

    def __str__(self):
        return self.username
    
    
class PageVisit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    url = models.CharField(max_length=500)
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(null=True, blank=True)

    def time_spent(self):
        """Calculate time spent on the page"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def __str__(self):
        user_info = self.user.username if self.user else f"Anonymous ({self.ip_address})"
        return f"{user_info} visited {self.url}"

    class Meta:
        ordering = ['-start_time']


class EmailVerification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(unique=True)

    def __str__(self):
        return f"Verification for {self.user.email}"
    
    
class PasswordReset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"password reset for {self.user.username} at {self.created}"
    
    
class UpdatedPost(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    original_post = models.OneToOneField(Blog, on_delete=models.CASCADE, related_name='updated_version')
    title = models.CharField(max_length=255)
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"Updated: {self.title}"
