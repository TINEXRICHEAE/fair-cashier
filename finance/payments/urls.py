from django.urls import path
from . import views

urlpatterns = [

    path('', views.mainAppDemo, name='mainAppDemo'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('register_user', views.register_user, name='register_user'),
    path('login_user', views.login_user, name='login_user'),
    path('check_auth', views.check_auth, name='check_auth'),
    path('logout_user', views.logout_user, name='logout_user'),


]
