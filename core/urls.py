from django.urls import path
from . import views

urlpatterns = [
    # contoh CRUD routes (ikut apa member B buat)
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
]