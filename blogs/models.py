from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings

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




class Blog(models.Model):
    title = models.CharField(max_length=150)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='blogs', default='')
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=25, choices= CATEGORY_CHOICES, default='OTHER')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            count = 1
            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)
        
        def __str__(self):
            return self.title


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=8, unique=True)
    profile_photo = models.ImageField(upload_to='profiles')
    date_of_birth = models.DateField(blank=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # ✅ Avoids clash
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',  # ✅ Avoids clash
        blank=True
    )
    
    def __str__(self):
        return self.username
    