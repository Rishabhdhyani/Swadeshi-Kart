from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('activate/<uidb64>/<token>/',views.activate,name='activate'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('',views.dashboard,name='dashboard'),
    path('forgotPassword/',views.forgotPassword,name='forgotPassword'),
    path('change_password/<uidb64>/<token>/',views.change_password,name='change_password'),
    path('password_reset_temp/',views.password_reset_temp,name='password_reset_temp'),
    ]
