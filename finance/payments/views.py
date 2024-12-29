from django.shortcuts import render

# Create your views here.


def dashboard(request):
    return render(request, 'dashboard.html')


def mainAppDemo(request):
    return render(request, 'mainAppDemo.html')
