from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-logs/', views.admin_page, name='admin_page'),
    path('logout/', views.logout_view, name='logout'),
]