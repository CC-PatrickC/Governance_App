from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('triage/', views.project_triage, name='project_triage'),
    path('scoring/', views.project_scoring_list, name='project_scoring_list'),
    path('new/', views.project_create, name='project_create'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/edit/', views.project_update, name='project_update'),
    path('<int:pk>/update/', views.project_update_ajax, name='project_update_ajax'),
    path('<int:pk>/update-type/', views.project_update_type, name='project_update_type'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('<int:pk>/score/', views.project_scoring, name='project_scoring'),
    path('<int:project_pk>/attachment/<int:file_pk>/delete/', views.delete_attachment, name='delete_attachment'),
<<<<<<< Updated upstream
=======
    path('<int:pk>/debug-files/', views.debug_project_files, name='debug_project_files'),
    path('api/users/', views.api_users, name='api_users'),
    path('<int:pk>/conversations/', views.get_project_conversations, name='get_project_conversations'),
    path('<int:pk>/conversations/add/', views.add_project_conversation, name='add_project_conversation'),
    path('notifications/manage/', views.manage_notifications, name='manage_notifications'),
    path('notifications/add/', views.add_notification, name='add_notification'),
    path('notifications/<int:pk>/update/', views.update_notification, name='update_notification'),
    path('notifications/<int:pk>/delete/', views.delete_notification, name='delete_notification'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
>>>>>>> Stashed changes
] 