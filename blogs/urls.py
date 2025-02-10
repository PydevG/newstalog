from django.urls import path
from . import views
# from django_plotly_dash.views import show

app_name = 'blogs'

urlpatterns = [
    path('', views.homeview, name='Home'),
    path('about/', views.aboutview, name='about'),
    path('contact/', views.contactview, name='contact'),
    path('register/', views.registerview, name='register'),
    path('post/<slug:slug>/', views.singlepostview, name='single-post'),
    path('category/<slug:slug>/', views.categoryview, name='category'),
    path('categories/', views.categoriesview2, name="categories"),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('tag/<slug:slug>/', views.tagview, name='tag-posts'),
    path('login/', views.userlogin, name='login'),
    path('forgot/', views.forgot_password, name='forgot'),
    path('reset/', views.reset_password, name='reset'),
    path('link-sent/', views.password_reset_sent, name='reset-sent'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify-email'),





    # path('dashboard/', views.dashboard, name='dashboard')
]