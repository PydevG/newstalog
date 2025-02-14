from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from .models import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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
import uuid
from django.core.mail import send_mail
from .utils import send_verification_email, get_pesapal_token
from django.utils.crypto import get_random_string
from django.contrib.sites.shortcuts import get_current_site
from .forms import *
from django.utils.text import slugify
from django.views.generic import ListView
from django.db.models import Q
import json
from django.http import JsonResponse
import time





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

@login_required(login_url='blogs:login')
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
    
    slug=slug

    categories = Category.objects.all()
    trending_posts = Blog.objects.filter(is_trending=True, is_approved=True, is_published=True)[:5]
    latest_posts = Blog.objects.filter(is_published=True, is_approved=True).order_by('-created_at')[:5]
    comments = Comment.objects.filter(blog=post).order_by('-created_at')[:5]
    all_comments = Comment.objects.filter(blog__slug=slug)

    context = {
        "post": post,
        'categories': categories,
        'trending_posts': trending_posts,
        'latest_posts': latest_posts,
        'comments': comments,
        'all_comments': all_comments,
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


User = get_user_model()


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

        # Get or create profile
        profile, created = Profile.objects.get_or_create(user=user)

        # Generate and save new verification token
        profile.generate_verification_token()

        # Generate email verification link
        verification_link = f"{request.scheme}://{request.get_host()}{reverse('blogs:verify_email', args=[profile.verification_token])}"

        # Send email verification
        email_sent = send_verification_email(email, verification_link)

        if email_sent:
            messages.success(request, "Account created! Check your email to activate your account.")
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
			return redirect('blogs:update_profile')

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
            newPassword = request.POST.get('password')
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
    updated_posts = Blog.objects.filter(is_approved=False, author=request.user, is_updated=True)
    no_of_posts = Blog.objects.filter(author=request.user).count()
    return render(request, 'blogs/user_posts.html', {'posts': posts, 'updated_posts':updated_posts, 'no_of_posts':no_of_posts,})

@login_required(login_url='blogs:login')
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
        if today_posts_count >= 2:
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
            to_slide=False,
            is_updated=True,
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


@login_required(login_url='blogs:login')
def edit_post(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    if request.user != blog.author:
        messages.error(request, "You dont have permissions to edit this post")
        return redirect('blogs:Home')

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
            blog.is_updated = True
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

@login_required(login_url='blogs:login')
def update_profile(request):
    user_profile = request.user.profile  # Fetch the user's profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('blogs:Home')

    else:
        form = ProfileForm(instance=user_profile)

    # Social media links with user data
    social_links = {
        "Facebook": {"prefix": "https://www.facebook.com/", "value": user_profile.facebook if user_profile.facebook else ""},
        "Twitter": {"prefix": "https://www.twitter.com/", "value": user_profile.twitter if user_profile.twitter else ""},
        "X": {"prefix": "https://www.x.com/", "value": user_profile.x if user_profile.x else ""},
        "Instagram": {"prefix": "https://www.instagram.com/", "value": user_profile.instagram if user_profile.instagram else ""},
        "TikTok": {"prefix": "https://www.tiktok.com/@", "value": user_profile.tiktok if user_profile.tiktok else ""}
    }

    return render(request, 'blogs/update_profile.html', {"form": form, "social_links": social_links})



def privacyview(request):
    return render(request, "blogs/privacy-policy.html")

def guidelinesview(request):
    return render(request, "blogs/content-guidelines.html")

class BlogSearchView(ListView):
    model = Blog
    template_name = 'blogs/search_results.html'
    context_object_name = 'posts'
    paginate_by = 4  # Define pagination limit

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Blog.objects.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(category__name__icontains=query) |
                Q(tags__name__icontains=query),
                is_published=True  # Only show published posts
            ).distinct()
        return Blog.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        posts_list = self.get_queryset()

        # Pagination handling
        paginator = Paginator(posts_list, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context['page_obj'] = posts  # Ensure the page_obj is set correctly
        context['posts'] = posts  # Ensure posts is updated for iteration in template
        context['query'] = query  # Pass search query for pagination links
        return context



@login_required(login_url='blogs:login')
def upgrade_to_premium(request):
    return render(request, "blogs/upgrade.html")


def leaderboard(request):
    users = User.objects.all()

    ranked_users = sorted(users, key=lambda u: (
        u.blog_set.count(),  # Number of blogs
        sum(blog.likes.count() for blog in u.blog_set.all()),  # Total likes on blogs
    ), reverse=True)

    user_stats = []
    for user in ranked_users[:10]:  # Get only the top 10 users
        total_likes = sum(blog.likes.count() for blog in user.blog_set.all())
        user_stats.append({
            'user': user,
            'blog_count': user.blog_set.count(),
            'total_likes': total_likes
        })

    return render(request, 'blogs/leaderboard.html', {'users': user_stats})


@login_required(login_url='blogs:login')
def like_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)  # Handle invalid requests

    post = get_object_or_404(Blog, id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({"liked": liked, "likes_count": post.likes.count()})


def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "twitter": user.profile.twitter,  # Assuming you have a Profile model
        "x":user.profile.x,
        "tiktok": user.profile.tiktok,
        "instagram":user.profile.instagram,
    })
    
def author_profile(request, username):
    author = get_object_or_404(User, username=username)
    user_profile = author.profile  # Fetch the user's profile
    no_of_posts = Blog.objects.filter(author=author).count()


    # Attach social links inside the profile object
    user_profile.social_links = {
        "Facebook": f"{user_profile.facebook}" if user_profile.facebook else "",
        "Twitter": f"{user_profile.twitter}" if user_profile.twitter else "",
        "X": f"{user_profile.x}" if user_profile.x else "",
        "Instagram": f"{user_profile.instagram}" if user_profile.instagram else "",
        "TikTok": f"{user_profile.tiktok}" if user_profile.tiktok else ""
    }

    return render(request, 'blogs/author_profile.html', {'author': author, 'no_of_posts':no_of_posts,})


def authorposts(request, username):
    author_posts = Blog.objects.filter(author__username=username)
    user = get_object_or_404(User, username=username)
    paginator = Paginator(author_posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    no_of_posts = Blog.objects.filter(author=user).count()


    context = {
        "author_posts":author_posts,
        'page_obj':page_obj,
        'user':user,
        'no_of_posts':no_of_posts,

    }
    return render(request, 'blogs/author_posts.html', context)
