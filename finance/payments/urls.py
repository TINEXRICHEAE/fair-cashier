from django.urls import path
from . import views

urlpatterns = [

    path('', views.mainAppDemo, name='mainAppDemo'),
    path('dashboard', views.dashboard, name='dashboard'),

]
