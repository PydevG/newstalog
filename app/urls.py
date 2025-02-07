from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blogs/', include('blogs.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls', namespace='the_django_plotly_dash')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
