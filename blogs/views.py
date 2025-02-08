from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from .models import *
from django.core.paginator import Paginator
from django.contrib import messages

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
    all_posts = Blog.objects.all().order_by('-created_at')
    trending_posts = Blog.objects.filter(is_trending=True, is_approved=True)[:5]
    headline_posts = Blog.objects.filter(is_headline=True, is_approved=True)
    categories = Category.objects.all()
    latest_posts = Blog.objects.all().order_by('-created_at')[:5]
    slide_posts = Blog.objects.filter(to_slide=True, is_approved=True)[:3]
    paginator = Paginator(all_posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'featured_posts':featured_posts,
        'all_posts':all_posts,
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
            blog = get_object_or_404(Blog, slug=slug)
            if Comment.objects.filter(blog=blog, author=request.user).exists():
                messages.error(request, "You have already commented on this post.")
            else:
                blog = get_object_or_404(Blog, slug=slug)
                # Save the comment
                content = request.POST.get("message")
                Comment.objects.create(blog=blog, author=request.user, content=message)
                messages.success(request, "Your comment has been posted.")
        else:
            messages.error(request, "You need to be logged in to comment.")

        return redirect("blogs:single-post", slug=blog.slug)  # Redirect to the post page

    post = get_object_or_404(Blog, slug=slug)
    categories = Category.objects.all()
    trending_posts = Blog.objects.filter(is_trending=True, is_approved=True)[:5]
    latest_posts = Blog.objects.all().order_by('-created_at')[:5]
    comments = Comment.objects.filter(blog__slug=slug)[:4]
    context = {
        "post":post,
        'categories':categories,
        'trending_posts':trending_posts,
        'latest_posts':latest_posts,
        'comments':comments,
    }
    return render(request, 'blogs/single-post.html', context)

def tagview(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Blog.objects.filter(tags__slug=slug).select_related('author', 'category').prefetch_related('tags')
    headline_posts = Blog.objects.filter(is_headline=True, is_approved=True)
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


def registrationview(request):
    return render(request, 'blogs/registration.html')

def loginview(request):
    return render(request, 'blogs/login.html')


def categoryview(request, slug):
    category = Category.objects.filter(slug=slug)
    all_categories = Category.objects.all()
    category_posts = Blog.objects.filter(category__slug=slug)
    trending_posts = Blog.objects.filter(is_trending=True, is_approved=True)[:5]
    latest_posts = Blog.objects.all().order_by('-created_at')[:5]
    paginator = Paginator(category_posts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "category":category,
        "category_posts":category_posts,
        'trending_posts':trending_posts,
        'latest_posts':latest_posts,
        'all_categories':all_categories,
        'page_obj':page_obj,
    }
    return render(request, 'blogs/category.html', context)

def aboutview(request):
    return render(request, 'blogs/about.html')

def contactview(request):
    return render(request, 'blogs/contact.html')

# def dashboard(request):
#     return render(request, 'blogs/dashboard.html')