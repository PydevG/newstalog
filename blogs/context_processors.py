from .models import Category, Blog

def categories_processor(request):
    base_categories = Category.objects.all()
    return {'base_categories': base_categories}

def posts_processor(request):
    recent_posts = Blog.objects.all().order_by('-created_at')[:5]
    return {'recent_posts':recent_posts}