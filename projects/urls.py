from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('triage/', views.project_triage, name='project_triage'),
    path('new/', views.project_create, name='project_create'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/edit/', views.project_update, name='project_update'),
    path('<int:pk>/update/', views.project_update_ajax, name='project_update_ajax'),
    path('<int:pk>/update-type/', views.project_update_type, name='project_update_type'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
] 