from django.shortcuts import render
from django.views import View
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from .models import *

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
    all_posts = Blog.objects.all()
    trending_posts = Blog.objects.filter(is_trending=True, is_approved=True)
    headline_posts = Blog.objects.filter(is_headline=True, is_approved=True)
    slide_posts = Blog.objects.filter(to_slide=True, is_approved=True)
    context = {
        'featured_posts':featured_posts,
        'all_posts':all_posts,
        'trending_posts':trending_posts,
        'slide posts':slide_posts,
        'headline_posts':headline_posts,
    }
    return render(request, 'blogs/index.html', context)

def singlepostview(request):
    return render(request, 'blogs/single-post.html')

def registrationview(request):
    return render(request, 'blogs/registration.html')

def loginview(request):
    return render(request, 'blogs/login.html')


def categoryview(request):
    return render(request, 'blogs/category.html')

def aboutview(request):
    return render(request, 'blogs/about.html')

def contactview(request):
    return render(request, 'blogs/contact.html')

# def dashboard(request):
#     return render(request, 'blogs/dashboard.html')