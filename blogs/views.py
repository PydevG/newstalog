from django.shortcuts import render
from django.views import View
# Create your views here.

def homeview(request):
    return render(request, 'blogs/index.html')