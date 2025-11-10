from django.urls import path
from django.http import HttpResponseRedirect
from django.conf import settings

from . import views

app_name = 'projects'

def redirect_home(request):
    """Redirect visitors to the appropriate landing page based on auth and CAS status."""
    if request.user.is_authenticated:
        return HttpResponseRedirect('/requests/')

    if getattr(settings, "ENABLE_CAS", False):
        return HttpResponseRedirect('/cas-login/')

    if getattr(settings, "ENABLE_AZURE_AD", False):
        return HttpResponseRedirect('/accounts/microsoft/login/')

    return HttpResponseRedirect('/login/')

urlpatterns = [
    path('', redirect_home, name='home'),
    path('requests/', views.project_list, name='project_list'),
    path('archive/', views.archive, name='archive'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('triage/', views.project_triage, name='project_triage'),
    path('governance/', views.project_scoring_list, name='project_scoring_list'),

    path('final-governance/', views.project_final_scoring_list, name='project_final_scoring_list'),
    path('dashboard/', views.cabinet_dashboard, name='dashboard'),
    path('test-dashboard/', views.test_dashboard, name='test_dashboard'),

    path('new/', views.project_create, name='project_create'),
    path('intake/', views.project_intake_form, name='project_intake_form'),
    path('my-governance/', views.my_governance, name='my_governance'),
    path('my-governance-superuser/', views.my_governance_superuser, name='my_governance_superuser'),
    path('<int:pk>/edit/', views.project_update, name='project_update'),
    path('<int:pk>/edit-form/', views.project_update_form_ajax, name='project_update_form_ajax'),
    path('<int:pk>/update/', views.project_update_ajax, name='project_update_ajax'),
    path('<int:pk>/update-ajax/', views.project_update_ajax, name='project_update_ajax_alt'),
    path('<int:pk>/update-status/', views.project_update_status, name='project_update_status'),
    path('<int:pk>/update-type/', views.project_update_type, name='project_update_type'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('<int:pk>/delete-request/', views.project_delete_request, name='project_delete_request'),
    path('<int:pk>/score/', views.project_scoring, name='project_scoring'),
    path('<int:pk>/final-score/', views.project_final_scoring, name='project_final_scoring'),
    path('<int:pk>/final-score-details/', views.project_final_scoring_details, name='project_final_scoring_details'),
    path('<int:pk>/scoring-details-modal/', views.project_scoring_details_modal, name='project_scoring_details_modal'),
    path('<int:pk>/final-scoring-details-modal/', views.project_final_scoring_details_modal, name='project_final_scoring_details_modal'),
    path('<int:pk>/update-final-priority/', views.update_final_priority, name='update_final_priority'),
    path('<int:pk>/project-details-readonly/', views.project_details_readonly, name='project_details_readonly'),
    path('<int:pk>/project-details-modal/', views.project_details_modal, name='project_details_modal'),
    path('<int:project_pk>/attachment/<int:file_pk>/delete/', views.delete_attachment, name='delete_attachment'),
    path('<int:pk>/debug-files/', views.debug_project_files, name='debug_project_files'),
    path('test-ajax/', views.test_ajax_endpoint, name='test_ajax_endpoint'),
    path('archived/', views.archived_requests, name='archived_requests'),
    path('api/users/', views.api_users, name='api_users'),
    path('<int:pk>/conversations/', views.get_project_conversations, name='get_project_conversations'),
    path('<int:pk>/conversations/add/', views.add_project_conversation, name='add_project_conversation'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
] 