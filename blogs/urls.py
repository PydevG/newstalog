from django.urls import path
from . import views
from django.views import View

urlpatterns = [
    path('', views.homeview, name='Home'),
]