from django.urls import path
from . import views

urlpatterns = [

    path('', views.mainAppDemo, name='mainAppDemo'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('register_user', views.register_user, name='register_user'),
    path('login_user', views.login_user, name='login_user'),
    path('check_auth', views.check_auth, name='check_auth'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('points', views.points_view, name='points'),
    path('buy-points', views.buy_points, name='buy_points'),
    path('sell-points', views.sell_points, name='sell_points'),
    path('share-points', views.share_points, name='share_points'),
    path('transaction-history', views.transaction_history,
         name='transaction_history'),
    path('user-profile', views.user_profile, name='user_profile'),
    path('delete-account', views.delete_account, name='delete_account'),


]
