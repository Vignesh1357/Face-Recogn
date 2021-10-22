from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.mainHome, name='home'),
    path('app-home/', views.home, name='app-home'),
    path('register/',views.register, name='register'),
    path('rcognize/', views.recognize, name='recognize'),
    path('login/',auth_views.LoginView.as_view(template_name='facedetect/login.html'), name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='facedetect/logout.html'), name='logout')
]