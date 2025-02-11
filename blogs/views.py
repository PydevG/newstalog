from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from .models import *
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.timezone import now
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
import requests
from .models import EmailVerification
import uuid
from django.core.mail import send_mail
from .utils import send_verification_email
from django.utils.crypto import get_random_string
from django.contrib.sites.shortcuts import get_current_site
from .forms import *
from django.utils.text import slugify




User = get_user_model()

def analytics_dashboard(request):
    """Display analytics of page visits"""

    most_visited = PageVisit.objects.values('url').annotate(visits=Count('id')).order_by('-visits')[:5]

    avg_time_spent = PageVisit.objects.exclude(end_time=None).annotate(
        time_spent=ExpressionWrapper(F('end_time') - F('start_time'), output_field=fields.DurationField())
    ).aggregate(Avg('time_spent'))

    unique_visitors = PageVisit.objects.values('ip_address').distinct().count()

    context = {
        'most_visited': most_visited,
        'avg_time_spent': avg_time_spent['time_spent__avg'],
        'unique_visitors': unique_visitors
    }
    return render(request, 'blogs/analytics_dashboard.html', context)


def homeview(request):
    featured_posts = Blog.objects.filter(is_published=True, is_approved=True)
    all_posts = Blog.objects.filter(is_approved=True, is_published=True).order_by('-created_at')
    trending_posts = Blog.objects.filter(is_trending=True, is_approved=True, is_published=True)[:5]
    categories = Category.objects.all()
    headline_posts = Blog.objects.filter(is_headline=True, is_approved=True, is_published=True)
    slide_posts = Blog.objects.filter(to_slide=True, is_approved=True, is_published=True)[:3]
    latest_posts = Blog.objects.filter(is_published=True, is_approved=True).order_by('-created_at')[:5] 
    paginator = Paginator(all_posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'featured_posts':featured_posts,
        'trending_posts':trending_posts,
        'slide_posts':slide_posts,
        'headline_posts':headline_posts,
        'page_obj':page_obj,
        'categories':categories,
        'latest_posts':latest_posts
    }
    return render(request, 'blogs/index.html', context)

def singlepostview(request, slug):
    if request.method == 'POST':
        if request.user.is_authenticated:
            message = request.POST.get('message')
            blog = get_object_or_404(Blog, slug=slug, is_approved=True, is_published=True)
            if Comment.objects.filter(blog=blog, author=request.user).exists():
                messages.error(request, "You have already commented on this post.")
            else:
                # Save the comment
                Comment.objects.create(blog=blog, author=request.user, content=message)
                messages.success(request, "Your comment has been posted.")
        else:
            messages.error(request, "You need to be logged in to comment.")

        return redirect("blogs:single-post", slug=slug)  

    post = get_object_or_404(Blog, slug=slug, is_approved=True, is_published=True)

    categories = Category.objects.all()
    trending_posts = Blog.objects.filter(is_trending=True, is_approved=True, is_published=True)[:5]
    latest_posts = Blog.objects.filter(is_published=True, is_approved=True).order_by('-created_at')[:5]
    comments = Comment.objects.filter(blog=post)[:4]

    context = {
        "post": post,
        'categories': categories,
        'trending_posts': trending_posts,
        'latest_posts': latest_posts,
        'comments': comments,
    }
    return render(request, 'blogs/single-post.html', context)




def tagview(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Blog.objects.filter(tags__slug=slug).select_related('author', 'category').prefetch_related('tags')
    headline_posts = Blog.objects.filter(is_headline=True, is_approved=True, is_published=True)
    trending_posts = Blog.objects.filter(is_trending=True, is_approved=True)[:5]
    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "posts": posts, 
        "tag": tag,
        "page_obj":page_obj,
        "headline_posts":headline_posts,
        "trending_posts":trending_posts,
    }
    return render(request, 'blogs/tag.html', context)


def loginview(request):
    return render(request, 'blogs/login.html')


def categoryview(request, slug):
    category = Category.objects.filter(slug=slug)
    slug = slug
    all_categories = Category.objects.all()
    category_posts = Blog.objects.filter(category__slug=slug)
    trending_posts = Blog.objects.filter(is_trending=True, is_approved=True)[:5]
    latest_posts = Blog.objects.all().order_by('-created_at')[:5]
    paginator = Paginator(category_posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "category":category,
        "category_posts":category_posts,
        'trending_posts':trending_posts,
        'latest_posts':latest_posts,
        'all_categories':all_categories,
        'page_obj':page_obj,
        'slug':slug,
    }
    return render(request, 'blogs/category.html', context)

def aboutview(request):
    return render(request, 'blogs/about.html')

def contactview(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            name = request.user.username
            email = request.user.email
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            
        else:
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
        contact = ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
        messages.success(request, "Thankyou for contacting. We will get back shortly")
        return redirect('blogs:contact')
    return render(request, 'blogs/contact.html')

# def dashboard(request):
#     return render(request, 'blogs/dashboard.html')

def registerview(request):
    if request.method == "POST":
        full_name = request.POST["full_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirmpassword"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("blogs:register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect("blogs:register")

        # Create User
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = full_name
        user.is_active = False  # User must verify email before login
        user.save()

        # Generate a unique verification token
        verification_token = get_random_string(50)


        # Generate email verification link
        current_site = get_current_site(request)
        verification_link = f"http://{current_site.domain}{reverse('blogs:verify_email', args=[verification_token])}"

        # Send email verification
        email_sent = send_verification_email(email, verification_link)

        if email_sent:
            messages.success(request, "Account created! Check your email to verify your account.")
        else:
            messages.error(request, "Failed to send verification email. Try again.")

        return redirect("blogs:login")

    return render(request, "blogs/signup.html")



def userlogin(request):
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')

		user = authenticate(request, email=email, password=password)

		if user is not None:
			login(request, user)
			return redirect('blogs:Home')

		else:
			messages.error(request, "Invalid credentials")
			return redirect('blogs:login')


	return render(request, 'blogs/login.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            new_password_reset = PasswordReset.objects.create(user=user)

            password_reset_url = reverse('blogs:reset', kwargs={'reset_id': new_password_reset.reset_id})
            full_password_reset_url = f"{request.scheme}://{request.get_host()}{password_reset_url}"

            email_subject = "Reset Your Password"
            email_body = f"""Hello {user.username},

        You requested a password reset. Click the link below to reset your password:

            {full_password_reset_url}

            If you did not request this, ignore this email.

            Best,
            Your Website Team
            """

            send_mail(
                subject=email_subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,  # Set to False for debugging
            )

            return redirect('blogs:reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with the email '{email}' found!")
            return redirect('blogs:forgot')

    return render(request, 'blogs/forgot-password.html')

def password_reset_sent(request, reset_id):
	if PasswordReset.objects.filter(reset_id=reset_id).exists():
		return render(request, 'blogs/password-reset-sent.html')
	else:
		messages.error(request, "Invalid reset ID")
		return redirect('blogs:forgot')

def reset_password(request, reset_id):
    try:
        # Retrieve the PasswordReset object
        password_reset = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == 'POST':
            newPassword = request.POST.get('newpassword')
            confirmPassword = request.POST.get('confirmpassword')

            passwords_have_error = False

            if newPassword != confirmPassword:
                passwords_have_error = True
                messages.error(request, "Passwords do not match")
            if len(newPassword) < 5:
                passwords_have_error = True
                messages.error(request, "Password must be 5 or more characters long")

            expiration_time = password_reset.created + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                password_reset.delete()
                passwords_have_error = True
                messages.error(request, "Link expired")

            if not passwords_have_error:
                user = password_reset.user
                user.set_password(newPassword)
                user.save()

                password_reset.delete()
                messages.success(request, "Password reset successfully, proceed to login")
                return redirect('blogs:login')
            else:
                # Redirect back to the reset form with error messages
                return redirect('blogs:reset', reset_id=reset_id)

    except PasswordReset.DoesNotExist:
        messages.error(request, "Invalid reset ID")
        return redirect('blogs:forgot')

    return render(request, 'blogs/reset-password.html')

def logout_view(request):
	logout(request)
	return redirect('blogs:login')


def categoriesview2(request):
    all_categories = Category.objects.all()

    context = {
        'all_categories':all_categories,
    }
    
    return render(request, 'blogs/cats.html', context)


def verify_email(request, token):
    try:
        profile = Profile.objects.get(verification_token=token)
        user = profile.user
        user.is_active = True  # Activate user
        user.save()
        profile.verification_token = ""  # Clear token after verification
        profile.save()
        messages.success(request, "Email verified successfully! You can now log in.")
    except Profile.DoesNotExist:
        messages.error(request, "Invalid verification link.")

    return redirect("blogs:login")

@login_required(login_url='blogs:login')
def user_posts(request):
    posts = Blog.objects.filter(author=request.user)
    return render(request, 'blogs/user_posts.html', {'posts': posts})

@login_required
def delete_post(request, id):  # id is from the URL
    if request.method == "POST":
        post_id = request.POST.get("post_id")

        # Debugging: Print post_id to check if it's being received
        print(f"Deleting post with ID: {post_id}")

        post = get_object_or_404(Blog, id=id, author=request.user)  # Use 'id' from URL
        post.delete()
        messages.success(request, "Post deleted successfully.")

    return redirect("blogs:my-posts")  # Redirect to user's posts


@login_required(login_url='blogs:login')
def create_post(request):
    # Count the number of posts the user has created today
    today_posts_count = Blog.objects.filter(author=request.user, created_at__date=now().date()).count()

    if request.method == "POST":
        if today_posts_count >= 3:
            messages.error(request, "You have reached the daily limit of 3 posts. Try again tomorrow!")
            return redirect("blogs:my-posts")

        title = request.POST.get("title")
        content = request.POST.get("content")
        category_id = request.POST.get("category")
        tags_ids = request.POST.getlist("tags")
        image = request.FILES.get("image")

        category = Category.objects.get(id=category_id) if category_id else None
        post = Blog.objects.create(
            title=title,
            author=request.user,
            content=content,
            category=category,
            image=image,
            is_published=False,
            is_trending=False,
            is_approved=False,
            is_headline=False,
            to_slide=False
        )

        # Add selected tags
        if tags_ids:
            post.tags.set(Tag.objects.filter(id__in=tags_ids))

        messages.success(request, "Post created successfully!")
        return redirect("blogs:my-posts")

    categories = Category.objects.all()
    tags = Tag.objects.all()
    form = BlogForm()
    
    return render(request, "blogs/create_post.html", {
        "categories": categories,
        "tags": tags,
        "form": form,
        "today_post_count": today_posts_count,  # Send count to template
    })


@login_required
def edit_post(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    if request.user != blog.author:
        return redirect('blog_list')

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)

        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            # Ensure the UpdatedPost is linked properly
            updated_post, created = UpdatedPost.objects.get_or_create(original_post=blog, defaults={'blog': blog})
            updated_post.blog = blog  # Assign the related Blog post
            updated_post.title = title
            updated_post.content = content
            updated_post.save()

            # Mark original post as under review
            blog.is_approved = False
            blog.is_published = False
            blog.save()

            messages.success(request, "Your post update has been submitted for review.")
            return redirect('blogs:my-posts')

    else:
        form = BlogForm(instance=blog)

    categories = Category.objects.all()
    tags = Tag.objects.all()

    return render(request, 'blogs/update_post.html', {
        'form': form,
        'blog': blog,
        'categories': categories,
        'tags': tags
    })

@login_required
def update_profile(request):
    profile = request.user.profile  # Get the profile instance

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            if 'profile_picture' in request.FILES:  # Check if a new file was uploaded
                profile.profile_picture.delete(save=False)  # Delete old image manually
                profile.profile_picture = request.FILES['profile_picture']  # Assign new image
            
            profile.save()  # Save changes
            messages.success(request, "Profile updated successfully!")
        else:
            messages.error(request, "Error updating profile. Please check your inputs.")
    
    return redirect(request.META.get('HTTP_REFERER', 'blogs:Home'))


def privacyview(request):
    return render(request, "blogs/privacy-policy.html")

def guidelinesview(request):
    return render(request, "blogs/content-guidelines.html")
