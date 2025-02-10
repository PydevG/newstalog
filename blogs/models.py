from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.timezone import now

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
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='blogs', default='')
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField('Tag', related_name='blogs', blank=True)
    is_published = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_headline = models.BooleanField(default=False)
    to_slide = models.BooleanField(default=False)
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

    def __str__(self):
        return f'{self.user.username} Profile'



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