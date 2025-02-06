from django.urls import path
from . import views
# from django_plotly_dash.views import show

urlpatterns = [
    path('', views.homeview, name='Home'),
    path('about/', views.aboutview, name='about'),
    path('contact/', views.contactview, name='contact'),
    path('register/', views.registrationview, name='register'),
    path('login/', views.loginview, name='login'),
    path('post/', views.singlepostview, name='single-post'),
    path('category/', views.categoryview, name='category'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    # path('dashboard/', views.dashboard, name='dashboard')
]