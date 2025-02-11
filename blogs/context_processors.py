from .models import Category, Blog

def categories_processor(request):
    base_categories = Category.objects.filter()
    return {'base_categories': base_categories}

def posts_processor(request):
    recent_posts = Blog.objects.filter(is_published=True, is_approved=True).order_by('-created_at')[:5]
    return {'recent_posts':recent_posts}