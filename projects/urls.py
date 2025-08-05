from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('triage/', views.project_triage, name='project_triage'),
    path('scoring/', views.project_scoring_list, name='project_scoring_list'),
    path('scoring-test/', views.project_scoring_list_test, name='project_scoring_list_test'),
    path('final-scoring/', views.project_final_scoring_list, name='project_final_scoring_list'),
    path('dashboard/', views.cabinet_dashboard, name='dashboard'),
    path('new/', views.project_create, name='project_create'),
    path('<int:pk>/edit/', views.project_update, name='project_update'),
    path('<int:pk>/edit-form/', views.project_update_form_ajax, name='project_update_form_ajax'),
    path('<int:pk>/update/', views.project_update_ajax, name='project_update_ajax'),
    path('<int:pk>/update-status/', views.project_update_status, name='project_update_status'),
    path('<int:pk>/update-type/', views.project_update_type, name='project_update_type'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('<int:pk>/score/', views.project_scoring, name='project_scoring'),
    path('<int:pk>/final-score/', views.project_final_scoring, name='project_final_scoring'),
    path('<int:pk>/final-score-details/', views.project_final_scoring_details, name='project_final_scoring_details'),
    path('<int:pk>/scoring-details-modal/', views.project_scoring_details_modal, name='project_scoring_details_modal'),
    path('<int:pk>/update-final-priority/', views.update_final_priority, name='update_final_priority'),
    path('<int:project_pk>/attachment/<int:file_pk>/delete/', views.delete_attachment, name='delete_attachment'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
] 