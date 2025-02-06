from django.shortcuts import render
from django.views import View
# Create your views here.

def homeview(request):
    return render(request, 'blogs/index.html')

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