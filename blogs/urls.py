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
    path('reset/<uuid:reset_id>/', views.reset_password, name='reset'),
    path('link-sent/<uuid:reset_id>/', views.password_reset_sent, name='reset-sent'),
    path('logout/', views.logout_view, name='logout'),
    path("verify-email/<str:token>/", views.verify_email, name="verify_email"),
    path('my-posts/', views.user_posts, name='my-posts'),
    path('delete/<int:id>', views.delete_post, name='delete_post'),
    path('create-post/', views.create_post, name='create-post'),
    path('edit/<slug:slug>/', views.edit_post, name='edit_post'),





    # path('dashboard/', views.dashboard, name='dashboard')
]