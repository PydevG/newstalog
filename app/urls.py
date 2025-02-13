from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blogs/', include('blogs.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls', namespace='the_django_plotly_dash')),
    path('accounts/', include('allauth.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# from django.conf.urls import handler404, handler500
# from django.shortcuts import render

# # Custom error views
# def custom_404(request, exception):
#     return render(request, 'errors/404.html', status=404)

# def custom_500(request):
#     return render(request, 'errors/500.html', status=500)

# # Assign error handlers
# handler404 = 'app.urls.custom_404'
# handler500 = 'app.urls.custom_500'
