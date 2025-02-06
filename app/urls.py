from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blogs/', include('blogs.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls', namespace='the_django_plotly_dash')),
]
