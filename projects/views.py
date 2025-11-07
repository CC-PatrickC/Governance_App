from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test, login_not_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.urls import reverse
from django.db import models
from django.db.models import Q
from .models import Project, ProjectFile, ProjectScore, TriageNote, TriageChange, Conversation, SystemNotification
from .forms import ProjectForm
import json
import logging

logger = logging.getLogger('projects')

def sync_status_with_stage(project):
    """
    Synchronize the status field with the stage field.
    The stage field is the primary field that determines workflow progression.
    """
    # Mapping from stage to status
    stage_to_status_mapping = {
        'Pending_Review': 'pending',
        'Under_Review_Triage': 'under_review_triage',
        'Under_Review_governance': 'under_review_scoring',
        'Under_Review_Final_governance': 'under_review_final_scoring',
    }
    
    # Get the expected status based on stage
    expected_status = stage_to_status_mapping.get(project.stage, project.status)
    
    # Only update if the status doesn't match the stage
    if project.status != expected_status:
        project.status = expected_status
        logger.info(f"Synced status from '{project.status}' to '{expected_status}' based on stage '{project.stage}'")
    
    return project

def is_triage_user(user):
    return user.is_staff or user.groups.filter(name='Triage Group').exists()

def is_triage_lead_user(user):
    return user.is_staff or user.groups.filter(name='Triage Group Lead').exists()

def is_ai_governance_user(user):
    return user.is_staff or user.groups.filter(name='AI Governance Group').exists()

def is_ai_governance_lead_user(user):
    return user.is_staff or user.groups.filter(name='AI Governance Group Lead').exists()

def is_erp_governance_user(user):
    return user.is_staff or user.groups.filter(name='ERP Governance Group').exists()

def is_erp_governance_lead_user(user):
    return user.is_staff or user.groups.filter(name='ERP Governance Group Lead').exists()

def is_it_governance_user(user):
    return user.is_staff or user.groups.filter(name='IT Governance Group').exists()

def is_it_governance_lead_user(user):
    return user.is_staff or user.groups.filter(name='IT Governance Group Lead').exists()

def is_process_improvement_user(user):
    return user.is_staff or user.groups.filter(name='Process Improvement Group').exists() or user.groups.filter(name='Process Improvement Governance Group').exists()

def is_process_improvement_lead_user(user):
    return user.is_staff or user.groups.filter(name='Process Improvement Group Lead').exists()

def track_project_changes(project, form_data, user):
    """Track changes made to project fields during triage updates"""
    # Define fields to track with their human-readable labels
    tracked_fields = {
        'title': 'Title',
        'description': 'Description',
        'project_type': 'Request Type',
        'priority': 'Priority',
        'stage': 'Stage',
        'department': 'Department',
        'contact_person': 'Contact Person',
        'contact_email': 'Contact Email',
    }
    
    changes_made = []
    
    for field_name, field_label in tracked_fields.items():
        old_value = getattr(project, field_name, '')
        new_value = form_data.get(field_name, '')
        
        # Convert choice fields to display values
        if field_name == 'project_type' and new_value:
            new_value = dict(Project.PROJECT_TYPE_CHOICES).get(new_value, new_value)
            if old_value:
                old_value = dict(Project.PROJECT_TYPE_CHOICES).get(old_value, old_value)
        elif field_name == 'stage' and new_value:
            new_value = dict(Project.STAGE_CHOICES).get(new_value, new_value)
            if old_value:
                old_value = dict(Project.STAGE_CHOICES).get(old_value, old_value)
        elif field_name == 'status' and new_value:
            new_value = dict(Project.STATUS_CHOICES).get(new_value, new_value)
            if old_value:
                old_value = dict(Project.STATUS_CHOICES).get(old_value, old_value)
        
        # Track the change if values are different
        if str(old_value) != str(new_value):
            TriageChange.objects.create(
                project=project,
                field_name=field_name,
                field_label=field_label,
                old_value=str(old_value) if old_value else '',
                new_value=str(new_value) if new_value else '',
                changed_by=user
            )
            changes_made.append(f"{field_label}: {old_value} → {new_value}")
    
    return changes_made

def is_scoring_user(user):
    return (user.is_superuser or user.is_staff or 
            user.groups.filter(name='AI Governance Group').exists() or 
            user.groups.filter(name='AI Governance Group Lead').exists() or
            user.groups.filter(name='ERP Governance Group').exists() or 
            user.groups.filter(name='ERP Governance Group Lead').exists() or
            user.groups.filter(name='IT Governance Group').exists() or 
            user.groups.filter(name='IT Governance Group Lead').exists() or
            user.groups.filter(name='Process Improvement Group').exists() or 
            user.groups.filter(name='Process Improvement Group Lead').exists() or
            (not user.groups.filter(name='Cabinet Group').exists() and not user.groups.filter(name='Triage Group').exists()))

def can_modify_final_priority(user):
    """Check if user can modify final priority ranks in Under Review - Final Governance section.
    Excludes AI/ERP/IT/Process Improvement Lead groups from modifying final priority."""
    if user.is_superuser or user.is_staff:
        return True
    
    # Allow regular governance group members (not leads) to modify final priority
    return (user.groups.filter(name='AI Governance Group').exists() or 
            user.groups.filter(name='ERP Governance Group').exists() or
            user.groups.filter(name='IT Governance Group').exists() or
            user.groups.filter(name='Process Improvement Group').exists())

def is_it_governance_scoring_user(user):
    return user.is_staff or user.groups.filter(name='IT Governance Scoring').exists()

def is_cabinet_user(user):
    return user.is_staff or user.groups.filter(name='Cabinet Group').exists()

def is_patrick(user):
    """Check if the user is Patrick (for test dashboard access)"""
    return user.username == 'pcondon' or user.email == 'pcondon@ccgov.org'



def get_user_allowed_project_types(user):
    """
    Returns a list of project types that the user is allowed to see based on their groups.
    Staff users can see all project types.
    """
    if user.is_staff:
        return None  # None means no filtering (see all types)
    
    # Map group names to project types
    group_to_project_type = {
        'IT Governance Scoring Group': 'it_governance',
        'ERP Governance Scoring Group': 'erp_governance', 
        'Data Governance Scoring Group': 'data_governance',
        'Process Improvement Scoring Group': 'process_improvement',
    }
    
    allowed_types = []
    user_groups = user.groups.all()
    
    for group in user_groups:
        if group.name in group_to_project_type:
            allowed_types.append(group_to_project_type[group.name])
    
    return allowed_types if allowed_types else None

def custom_login_view(request):
    if request.user.is_authenticated:
        # Redirect based on user permissions
        if request.user.is_staff or request.user.groups.exists():
            return redirect('projects:my_governance')
        else:
            return redirect('projects:project_intake_form')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # All users go to MyGovernance after login
            return redirect('projects:my_governance')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')

@login_required
def project_list(request):
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', 'all')
    type_filter = request.GET.get('type', '')
    priority_filter = request.GET.get('priority', '')
    status_filter = request.GET.get('status', '')
    department_filter = request.GET.get('department', '')

    # Base queryset
    projects = Project.objects.all().select_related('submitted_by').order_by('-submission_date')
    
    # Apply search filter
    if search_query:
        projects = projects.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(department__icontains=search_query) |
            models.Q(submitted_by__username__icontains=search_query)
        )
    
    # Apply my projects filter (only if user is authenticated)
    if filter_type == 'my_projects' and request.user.is_authenticated:
        projects = projects.filter(submitted_by=request.user)
    
    # Apply type filter
    if type_filter:
        projects = projects.filter(project_type=type_filter)
    
    # Apply priority filter
    if priority_filter:
        projects = projects.filter(priority=priority_filter)
    
    # Apply status filter
    if status_filter:
        projects = projects.filter(status=status_filter)

    # Apply department filter
    if department_filter:
        projects = projects.filter(department=department_filter)

    # Get filtered choices based on current selection
    filtered_projects = projects

    # Get available project types
    available_types = filtered_projects.values_list('project_type', flat=True).distinct()
    project_types = [(t[0], t[1]) for t in Project.PROJECT_TYPE_CHOICES if t[0] in available_types]

    # Get available priorities
    available_priorities = filtered_projects.values_list('priority', flat=True).distinct()
    priorities = [p for p in ['Top', 'High', 'Normal', 'Low'] if p in available_priorities]

    # Get available statuses
    available_statuses = filtered_projects.values_list('status', flat=True).distinct()
    status_choices = [(s[0], s[1]) for s in Project.STATUS_CHOICES if s[0] in available_statuses]

    # Get available departments
    departments = filtered_projects.exclude(department='').values_list('department', flat=True).distinct().order_by('department')

    context = {
        'projects': projects,
        'search_query': search_query,
        'filter_type': filter_type,
        'type_filter': type_filter,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'project_types': project_types,
        'priorities': priorities,
        'status_choices': status_choices,
        'departments': departments,
    }
    
    return render(request, 'projects/project_list.html', context)

@login_required
@user_passes_test(lambda u: is_triage_user(u) or is_triage_lead_user(u))
def project_triage(request):
    search_query = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    priority_filter = request.GET.get('priority', '')
    status_filter = request.GET.get('status', '')
    stage_filter = request.GET.get('stage', '')
    department_filter = request.GET.get('department', '')

    # Base queryset - Triage team can see all projects except Governance Closed
    projects = Project.objects.all().exclude(
        stage='Governance_Closure'
    ).select_related('submitted_by').order_by('-submission_date')
    
    # Apply search filter
    if search_query:
        projects = projects.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(department__icontains=search_query) |
            models.Q(submitted_by__username__icontains=search_query)
        )
    
    # Apply type filter
    if type_filter:
        projects = projects.filter(project_type=type_filter)
    
    # Apply priority filter
    if priority_filter:
        projects = projects.filter(priority=priority_filter)
    
    # Apply status filter
    if status_filter:
        projects = projects.filter(status=status_filter)

    # Apply stage filter
    if stage_filter:
        projects = projects.filter(stage=stage_filter)

    # Apply department filter
    if department_filter:
        projects = projects.filter(department=department_filter)

    # Get filtered choices based on current selection
    filtered_projects = projects

    # Get available project types
    available_types = filtered_projects.values_list('project_type', flat=True).distinct()
    project_types = [(t[0], t[1]) for t in Project.PROJECT_TYPE_CHOICES if t[0] in available_types]

    # Get available priorities
    available_priorities = filtered_projects.values_list('priority', flat=True).distinct()
    priorities = [p for p in ['Top', 'High', 'Normal', 'Low'] if p in available_priorities]

    # Get available statuses
    available_statuses = filtered_projects.values_list('status', flat=True).distinct()
    status_choices = [(s[0], s[1]) for s in Project.STATUS_CHOICES if s[0] in available_statuses]

    # Get available stages
    available_stages = filtered_projects.values_list('stage', flat=True).distinct()
    stage_choices = [(s[0], s[1]) for s in Project.STAGE_CHOICES if s[0] in available_stages]

    # Get available departments
    departments = filtered_projects.exclude(department='').values_list('department', flat=True).distinct().order_by('department')

    context = {
        'projects': projects,
        'search_query': search_query,
        'type_filter': type_filter,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'stage_filter': stage_filter,
        'department_filter': department_filter,
        'project_types': project_types,
        'priorities': priorities,
        'status_choices': status_choices,
        'stage_choices': stage_choices,
        'departments': departments,
    }
    
    return render(request, 'projects/triage.html', context)

@login_required
def project_update_ajax(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has permission to edit projects
    # Allow if user is triage user, triage lead user, OR if user is the submitter of the request
    can_edit = (is_triage_user(request.user) or 
                is_triage_lead_user(request.user) or 
                project.submitted_by == request.user)
    
    if not can_edit:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'You do not have permission to edit this request.'})
        else:
            messages.error(request, 'You do not have permission to edit this request.')
            return redirect('projects:project_detail', pk=pk)
    
    logger.info(f"=== Project Update Request ===")
    logger.info(f"Request method: {request.method}")
    logger.info(f"User: {request.user} (Staff: {request.user.is_staff}, Groups: {request.user.groups.all()})")
    logger.info(f"Project ID: {pk}")
    logger.info(f"X-Requested-With header: {request.headers.get('X-Requested-With')}")
    logger.info(f"Is AJAX request: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")
    
    if request.method != 'POST':
        logger.info("Not a POST request, rendering form")
        project = get_object_or_404(Project, pk=pk)
        # Check if request is in Governance Closed stage (cannot be edited)
        if project.stage == 'Governance_Closure':
            return render(request, 'projects/project_detail.html', {
                'project': project,
                'error_message': 'This request is closed and cannot be edited.'
            })
        return render(request, 'projects/project_edit.html', {'project': project})
        
    try:
        
        # Check if request is in Governance Closed stage (cannot be edited)
        if project.stage == 'Governance_Closure':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'This request is closed and cannot be edited.'})
            else:
                messages.error(request, 'This request is closed and cannot be edited.')
                return redirect('projects:project_detail', pk=pk)
        logger.info(f"\nProject details before update:")
        logger.info(f"Title: {project.title}")
        logger.info(f"Status: {project.status}")
        logger.info(f"Description: {project.description}")
        
        # Debug print
        print(f"Updating project {pk} with data: {data}")
        
        # Update project fields
        if 'title' in data:
            project.title = data['title']
        if 'description' in data:
            project.description = data['description']
        if 'priority' in data:
            project.priority = data['priority']
        if 'status' in data:
            project.status = data['status']
        if 'department' in data:
            project.department = data['department']
        
        project.save()
        print(f"Project {pk} updated successfully")
        return JsonResponse({'success': True})
    except Exception as e:
        print(f"Error updating project {pk}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
        
        if len(files) > 5:
            messages.error(request, 'You can upload a maximum of 5 files.')
            return render(request, 'projects/project_form.html', {'form': form})
            
        if form.is_valid():
            project = form.save(commit=False)
            project.submitted_by = request.user
            project.status = 'pending'
            project.priority = 'Normal'
            project.save()
            
            messages.success(request, 'Project submitted successfully!')
            return redirect('projects:project_list')
    else:
        form = ProjectForm()
    
    return render(request, 'projects/project_form.html', {'form': form})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # If user is a triage team member, redirect them to the edit form (unless request is closed)
    if (is_triage_user(request.user) or is_triage_lead_user(request.user)) and project.stage != 'Governance_Closure':
        return redirect('projects:project_update', pk=pk)
    
    return render(request, 'projects/project_detail.html', {'project': project})

@login_required
def project_update(request, pk):
    project = get_object_or_404(Project.objects.prefetch_related('triage_note_history__created_by', 'triage_change_history__changed_by'), pk=pk)
    
    # Check if user has permission to edit projects
    if not (is_triage_user(request.user) or is_triage_lead_user(request.user)):
        messages.error(request, 'You do not have permission to edit this request.')
        return redirect('projects:project_detail', pk=pk)
    
    # Check if request is in Governance Closed stage (cannot be edited)
    if project.stage == 'Governance_Closure':
        messages.error(request, 'This request is closed and cannot be edited.')
        return redirect('projects:project_detail', pk=pk)
    
    print(f"\n=== Project Update Debug ===")
    print(f"Request method: {request.method}")
    print(f"User: {request.user}")
    print(f"User groups: {[g.name for g in request.user.groups.all()]}")
    
    if request.method == 'POST':
        try:
            print(f"\nPOST data: {request.POST}")
            print(f"FILES data: {request.FILES}")
            
            # Get form data
            title = request.POST.get('title')
            if not title:
                raise ValueError("Title is required")
            
            # Get triage notes
            new_triage_notes = request.POST.get('triage_notes', '')
            
            # Track changes before updating
            changes_made = track_project_changes(project, request.POST, request.user)
            
            # Update project fields
            project.title = title
            project.description = request.POST.get('description', '')
            project.project_type = request.POST.get('project_type')
            project.priority = request.POST.get('priority')
            project.department = request.POST.get('department', '')
            project.notes = request.POST.get('notes', '')
            project.contact_person = request.POST.get('contact_person', '')
            
            # Update stage if provided
            new_stage = request.POST.get('stage')
            if new_stage:
                valid_stages = dict(Project.STAGE_CHOICES).keys()
                if new_stage in valid_stages:
                    project.stage = new_stage
                    print(f"Updated stage to: {new_stage}")
            
            # Only create a new TriageNote if the notes have changed and are not empty
            if new_triage_notes and new_triage_notes != project.triage_notes:
                TriageNote.objects.create(
                    project=project,
                    notes=new_triage_notes,
                    created_by=request.user
                )
            
            # Clear the triage notes field after saving to history
            project.triage_notes = ''
            
            # Sync status with stage before saving
            project = sync_status_with_stage(project)
            
            # Auto-assign final priority rank when moving to Under_Review_Final_governance
            if new_stage == 'Under_Review_Final_governance' and project.final_priority is None:
                # Get the highest existing rank
                max_rank = Project.objects.filter(
                    stage='Under_Review_Final_governance',
                    final_priority__isnull=False
                ).aggregate(max_rank=models.Max('final_priority'))['max_rank']
                
                # Set the new rank to be the next available number (append to end)
                new_rank = (max_rank or 0) + 1
                project.final_priority = new_rank
                print(f"Auto-assigned final priority rank {new_rank} for project {pk} (appended to end)")
            
            print(f"\nAbout to save project...")
            print(f"Project status before save: {project.status}")
            
            # Save the project
            project.save()
            
            print(f"Project saved successfully")
            print(f"Project status after save: {project.status}")
            
            # Verify the status was saved
            project.refresh_from_db()
            print(f"Project status after refresh: {project.status}")
            
            # Handle file uploads
            files = request.FILES.getlist('files')
            if files:
                if len(files) > 5:
                    messages.error(request, 'You can upload a maximum of 5 files.')
                    return render(request, 'projects/project_edit.html', {'project': project})
                
                for file in files:
                    ProjectFile.objects.create(project=project, file=file)
            
            messages.success(request, 'Project updated successfully!')
            return redirect('projects:project_triage')
            
        except ValueError as e:
            print(f"\nValidation error: {str(e)}")
            messages.error(request, str(e))
        except Exception as e:
            print(f"\nError updating project: {str(e)}")
            print(f"Error type: {type(e)}")
            print(f"Error args: {e.args}")
            messages.error(request, f'Error updating project: {str(e)}')
    
    return render(request, 'projects/project_edit.html', {'project': project})

@login_required
def project_update_form_ajax(request, pk):
    """AJAX endpoint to get just the edit form content"""
    try:
        logger.info(f"Loading edit form for project {pk}")
        
        # Check if user has permission to edit projects
        # Allow if user is triage user, triage lead user, OR if user is the submitter of the request
        project = get_object_or_404(Project, pk=pk)
        can_edit = (is_triage_user(request.user) or 
                    is_triage_lead_user(request.user) or 
                    project.submitted_by == request.user)
        
        if not can_edit:
            logger.warning(f"User {request.user} lacks permission to edit project {pk}")
            return JsonResponse({'error': 'You do not have permission to edit this request.'}, status=403)
        
        project = Project.objects.prefetch_related('triage_note_history__created_by', 'triage_change_history__changed_by', 'files').get(pk=pk)
        logger.info(f"Project {pk} loaded successfully, has {project.files.count()} files")
        
        # Check if request is in Governance Closed stage (cannot be edited)
        if project.stage == 'Governance_Closure':
            logger.info(f"Project {pk} is in Governance_Closure stage, cannot be edited")
            return JsonResponse({'error': 'This request is closed and cannot be edited.'}, status=403)
        
        # Get all users for the contact person dropdown
        from django.contrib.auth.models import User
        users = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')
        
        context = {
            'project': project,
            'users': users,
        }
        logger.info(f"Rendering edit form template for project {pk}")
        
        # Debug: Log the template context
        logger.info(f"Template context - Project: {project.title}, Files count: {project.files.count()}")
        
        return render(request, 'projects/project_edit_form.html', context)
    except Exception as e:
        logger.error(f"Error loading edit form for project {pk}: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        return JsonResponse({'error': f'Error loading form: {str(e)}'}, status=500)

@login_required
def debug_project_files(request, pk):
    """Debug endpoint to check project files"""
    project = get_object_or_404(Project, pk=pk)
    files = project.files.all()
    
    file_info = []
    for file in files:
        file_info.append({
            'id': file.id,
            'name': file.file.name,
            'url': file.file.url,
            'uploaded_at': file.uploaded_at.isoformat(),
            'exists': file.file.storage.exists(file.file.name)
        })
    
    return JsonResponse({
        'project_id': pk,
        'project_title': project.title,
        'file_count': len(file_info),
        'files': file_info
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def project_update_type(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        project_type = request.POST.get('project_type')
        if project_type in dict(Project.PROJECT_TYPE_CHOICES):
            project.project_type = project_type
            project.save()
            messages.success(request, 'Project type updated successfully!')
        else:
            messages.error(request, 'Invalid project type selected.')
    
    return redirect('projects:project_detail', pk=pk)

@login_required
@user_passes_test(lambda u: u.is_staff)
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        delete_reason = request.POST.get('delete_reason')
        if delete_reason:
            # Store the reason in the project before deleting
            project.delete_reason = delete_reason
            project.save()
            project.delete()
            messages.success(request, 'Project deleted successfully.')
            return redirect('projects:project_list')
        else:
            messages.error(request, 'Please provide a reason for deletion.')
            return redirect('projects:project_detail', pk=pk)
    
    return redirect('projects:project_detail', pk=pk)

@login_required
def delete_attachment(request, project_pk, file_pk):
    project = get_object_or_404(Project, pk=project_pk)
    file = get_object_or_404(ProjectFile, pk=file_pk, project=project)
    
    # Check if user has permission to delete attachments
    # Allow if user is staff, triage user, triage lead user, OR if user is the submitter of the request
    can_delete = (request.user.is_staff or 
                  is_triage_user(request.user) or 
                  is_triage_lead_user(request.user) or 
                  project.submitted_by == request.user)
    
    if not can_delete:
        messages.error(request, 'You do not have permission to delete this attachment.')
        return redirect('projects:project_update', pk=project_pk)
    
    if request.method == 'POST':
        try:
            file.delete()
            messages.success(request, 'Attachment deleted successfully.')
            
            # If this is an AJAX request (from modal), return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Attachment deleted successfully.'})
        except Exception as e:
            messages.error(request, f'Error deleting attachment: {str(e)}')
            
            # If this is an AJAX request (from modal), return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'Error deleting attachment: {str(e)}'})
    
    # For regular page requests, redirect to project update page
    return redirect('projects:project_update', pk=project_pk)

@login_required
@user_passes_test(is_scoring_user)
def project_scoring_list(request):
    search_query = request.GET.get('search', '')
    
    # Get projects that need governance review (stage is Under_Review_governance)
    projects = Project.objects.filter(stage='Under_Review_governance').select_related('submitted_by').order_by('-submission_date')
    
    # Apply group-based filtering
    allowed_types = get_user_allowed_project_types(request.user)
    if allowed_types is not None:
        # Filter projects based on user's allowed project types
        projects = projects.filter(project_type__in=allowed_types)
    
    # Apply search filter
    if search_query:
        projects = projects.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(department__icontains=search_query) |
            models.Q(submitted_by__username__icontains=search_query)
        )
    
    # Get user's allowed project types for template display
    allowed_types = get_user_allowed_project_types(request.user)
    if allowed_types is not None:
        # Convert project type codes to display names
        type_display_names = []
        for project_type in allowed_types:
            for choice in Project.PROJECT_TYPE_CHOICES:
                if choice[0] == project_type:
                    type_display_names.append(choice[1])
                    break
    else:
        type_display_names = None
    
    context = {
        'projects': projects,
        'search_query': search_query,
        'allowed_project_types': type_display_names,
    }
    
    return render(request, 'projects/project_scoring_list.html', context)



@login_required
@user_passes_test(is_scoring_user)
def project_scoring(request, pk):
    """Project scoring view - displays project scoring form"""
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        project.final_priority = request.POST.get('final_priority')
        project.final_score = request.POST.get('final_score')
        project.scoring_notes = request.POST.get('scoring_notes')
        project.strategic_alignment = request.POST.get('strategic_alignment')
        project.cost_benefit = request.POST.get('cost_benefit')
        project.user_impact = request.POST.get('user_impact')
        project.ease_of_implementation = request.POST.get('ease_of_implementation')
        project.vendor_reputation_support = request.POST.get('vendor_reputation_support')
        project.security_compliance = request.POST.get('security_compliance')
        project.student_centered = request.POST.get('student_centered')
        
        try:
            project.save()
            messages.success(request, 'Project scoring updated successfully!')
            return redirect('projects:project_scoring_list')
        except Exception as e:
            messages.error(request, f'Error updating project scoring: {str(e)}')
    
    return render(request, 'projects/project_scoring.html', {'project': project})


@login_required
@user_passes_test(is_scoring_user)
def project_scoring_details_modal(request, pk):
    """Return project details and scoring data for the scoring modal (AJAX)."""
    project = get_object_or_404(
        Project.objects.prefetch_related(
            'files',
            'triage_note_history__created_by',
            'scores__scored_by'
        ),
        pk=pk
    )

    allowed_types = get_user_allowed_project_types(request.user)
    if allowed_types is not None and project.project_type not in allowed_types:
        return JsonResponse({'error': 'You do not have permission to access this project.'}, status=403)

    user_score = None
    if request.user.is_authenticated:
        user_score = project.scores.filter(scored_by=request.user).first()

    triage_notes = project.triage_note_history.all().order_by('-created_at')
    files = project.files.all()

    project_data = {
        'id': project.id,
        'formatted_id': project.formatted_id,
        'title': project.title,
        'description': project.description,
        'project_type': project.project_type,
        'project_type_display': project.get_project_type_display(),
        'priority': project.priority,
        'department': project.department,
        'stage': project.stage,
        'status': project.status,
        'submission_date': project.submission_date.isoformat() if project.submission_date else None,
        'submission_date_formatted': project.submission_date.strftime('%B %d, %Y') if project.submission_date else None,
        'final_score': project.final_score,
        'final_priority': project.final_priority,
        'contact_person': project.contact_person,
        'contact_email': project.contact_email,
        'contact_phone': project.contact_phone,
        'sdp_ticket_number': project.sdp_ticket_number,
        'sdp_link': project.sdp_link,
        'submitted_by_name': project.submitted_by.get_full_name() if project.submitted_by and (project.submitted_by.first_name or project.submitted_by.last_name) else (project.submitted_by.username if project.submitted_by else 'N/A'),
        'submitted_by_email': project.submitted_by.email if project.submitted_by else None,
        'files': [
            {
                'id': file.id,
                'name': file.file.name.split('/')[-1],
                'url': file.file.url,
            }
            for file in files
        ],
        'triage_notes': [
            {
                'notes': note.notes,
                'created_at': note.created_at.isoformat() if note.created_at else None,
                'created_at_formatted': note.created_at.strftime('%B %d, %Y at %I:%M %p') if note.created_at else None,
                'created_by': note.created_by.get_full_name() if note.created_by and (note.created_by.first_name or note.created_by.last_name) else (note.created_by.username if note.created_by else 'Unknown'),
            }
            for note in triage_notes
        ],
    }

    user_score_data = None
    if user_score:
        user_score_data = {
            'final_score': user_score.final_score,
            'scoring_notes': user_score.scoring_notes,
            'strategic_alignment': user_score.strategic_alignment,
            'cost_benefit': user_score.cost_benefit,
            'user_impact': user_score.user_impact,
            'ease_of_implementation': user_score.ease_of_implementation,
            'vendor_reputation_support': user_score.vendor_reputation_support,
            'security_compliance': user_score.security_compliance,
            'student_centered': user_score.student_centered,
        }

    condensed_scores = []
    group_to_check = None
    if is_ai_governance_lead_user(request.user) and project.project_type == 'ai_governance':
        group_to_check = 'AI Governance Group'
    elif is_erp_governance_lead_user(request.user) and project.project_type == 'erp_governance':
        group_to_check = 'ERP Governance Group'
    elif is_it_governance_lead_user(request.user) and project.project_type == 'it_governance':
        group_to_check = 'IT Governance Group'
    elif is_process_improvement_lead_user(request.user) and project.project_type == 'process_improvement':
        group_to_check = 'Process Improvement Group'

    if group_to_check:
        governance_group = Group.objects.filter(name=group_to_check).first()
        if governance_group:
            group_scores = project.scores.filter(scored_by__in=governance_group.user_set.all()).select_related('scored_by')
            for score in group_scores:
                condensed_scores.append({
                    'scored_by': score.scored_by.get_full_name() or score.scored_by.username,
                    'final_score': score.final_score,
                    'strategic_alignment': score.strategic_alignment,
                    'cost_benefit': score.cost_benefit,
                    'user_impact': score.user_impact,
                    'ease_of_implementation': score.ease_of_implementation,
                    'vendor_reputation_support': score.vendor_reputation_support,
                    'security_compliance': score.security_compliance,
                    'student_centered': score.student_centered,
                    'scoring_notes': score.scoring_notes,
                })

    response_payload = {
        'project': project_data,
        'user_score': user_score_data,
        'condensed_scores': condensed_scores,
    }

    return JsonResponse(response_payload)


@login_required
@user_passes_test(is_scoring_user)
def project_final_scoring_list(request):
    """List view for projects in the final governance stage."""
    search_query = request.GET.get('search', '').strip()

    projects = Project.objects.filter(
        stage='Under_Review_Final_governance'
    ).select_related('submitted_by')

    allowed_types = get_user_allowed_project_types(request.user)
    if allowed_types is not None:
        projects = projects.filter(project_type__in=allowed_types)

    if search_query:
        projects = projects.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(department__icontains=search_query) |
            models.Q(submitted_by__username__icontains=search_query) |
            models.Q(submitted_by__first_name__icontains=search_query) |
            models.Q(submitted_by__last_name__icontains=search_query)
        )

    projects = projects.order_by(
        models.F('final_priority').asc(nulls_last=True),
        '-submission_date'
    )

    context = {
        'projects': projects,
        'search_query': search_query,
    }

    return render(request, 'projects/project_final_scoring_list.html', context)


@login_required
@user_passes_test(is_scoring_user)
def project_final_scoring(request, pk):
    """Detail view for managing final scoring of a project."""
    project = get_object_or_404(
        Project.objects.prefetch_related(
            'files',
            'triage_note_history__created_by',
            'scores__scored_by'
        ),
        pk=pk
    )

    if request.method == 'POST':
        final_priority = request.POST.get('final_priority')
        final_score = request.POST.get('final_score')
        scoring_notes = request.POST.get('scoring_notes', '')

        errors = False

        if final_priority:
            try:
                project.final_priority = int(final_priority)
            except (ValueError, TypeError):
                messages.error(request, 'Final priority must be a whole number.')
                errors = True

        if final_score:
            try:
                project.final_score = float(final_score)
            except (ValueError, TypeError):
                messages.error(request, 'Final score must be a numeric value.')
                errors = True

        project.scoring_notes = scoring_notes

        if not errors:
            try:
                project.save(update_fields=['final_priority', 'final_score', 'scoring_notes'])
                messages.success(request, 'Final scoring updated successfully!')
                return redirect('projects:project_final_scoring_list')
            except Exception as exc:
                messages.error(request, f'Error updating final scoring: {exc}')

    scores = project.scores.select_related('scored_by').order_by('-created_at')

    context = {
        'project': project,
        'scores': scores,
    }

    return render(request, 'projects/project_final_scoring.html', context)


@login_required
@user_passes_test(is_scoring_user)
def project_final_scoring_details(request, pk):
    """Full-page read-only view of final scoring details for a project."""
    project = get_object_or_404(
        Project.objects.prefetch_related(
            'files',
            'triage_note_history__created_by',
            'scores__scored_by'
        ),
        pk=pk
    )

    scores = project.scores.select_related('scored_by').order_by('-created_at')

    context = {
        'project': project,
        'scores': scores,
    }

    return render(request, 'projects/project_final_scoring_details.html', context)


@login_required
@user_passes_test(is_scoring_user)
def project_final_scoring_details_modal(request, pk):
    """Render final scoring details for use inside modal dialogs."""
    project = get_object_or_404(
        Project.objects.prefetch_related(
            'files',
            'triage_note_history__created_by',
            'scores__scored_by'
        ),
        pk=pk
    )

    scores = project.scores.select_related('scored_by').order_by('-created_at')
    triage_notes = project.triage_note_history.all().select_related('created_by').order_by('-created_at')

    context = {
        'project': project,
        'scores': scores,
        'triage_notes': triage_notes,
    }

    return render(request, 'projects/project_final_scoring_details_modal.html', context)


@login_required
@user_passes_test(is_scoring_user)
@require_POST
def update_final_priority(request, pk):
    """AJAX endpoint to update the final priority ranking for a project."""
    if not can_modify_final_priority(request.user):
        return JsonResponse({'success': False, 'error': 'You do not have permission to modify final priority ranks.'}, status=403)

    project = get_object_or_404(Project, pk=pk)

    try:
        data = json.loads(request.body or '{}')
        new_priority = data.get('final_priority')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request payload.'}, status=400)

    if new_priority is None:
        return JsonResponse({'success': False, 'error': 'No priority value provided.'}, status=400)

    try:
        new_priority = int(new_priority)
        if new_priority < 1:
            raise ValueError
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Final priority must be a positive integer.'}, status=400)

    old_priority = project.final_priority

    if old_priority == new_priority:
        return JsonResponse({'success': True})

    queryset = Project.objects.filter(
        stage='Under_Review_Final_governance',
        final_priority__isnull=False
    ).exclude(pk=project.pk)

    try:
        if old_priority is not None:
            if new_priority < old_priority:
                queryset.filter(
                    final_priority__gte=new_priority,
                    final_priority__lt=old_priority
                ).update(final_priority=models.F('final_priority') + 1)
            else:
                queryset.filter(
                    final_priority__gt=old_priority,
                    final_priority__lte=new_priority
                ).update(final_priority=models.F('final_priority') - 1)
        else:
            queryset.filter(final_priority__gte=new_priority).update(final_priority=models.F('final_priority') + 1)

        project.final_priority = new_priority
        project.save(update_fields=['final_priority'])
    except Exception as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=500)

    return JsonResponse({'success': True})


@login_required
@user_passes_test(lambda u: u.is_staff)
def cabinet_dashboard(request):
    # Get all projects for statistics
    projects = Project.objects.all()
    
    # Calculate statistics by stage
    stage_counts = {
        'Pending_Review': projects.filter(stage='Pending_Review').count(),
        'Under_Review_Triage': projects.filter(stage='Under_Review_Triage').count(),
        'Under_Review_governance': projects.filter(stage='Under_Review_governance').count(),
        'Under_Review_Final_governance': projects.filter(stage='Under_Review_Final_governance').count(),
        'Governance_Closure': projects.filter(stage='Governance_Closure').count(),
    }
    
    # Calculate statistics by status using STATUS_CHOICES from model
    status_counts = {}
    for status_code, status_label in Project.STATUS_CHOICES:
        count = projects.filter(status=status_code).count()
        if count > 0:  # Only include statuses that have projects
            status_counts[status_label] = count
    
    # Get projects by stage for display
    projects_by_stage = {
        'Pending Review': projects.filter(stage='Pending_Review').order_by('-submission_date')[:5],
        'Under Review - Triage': projects.filter(stage='Under_Review_Triage').order_by('-submission_date')[:5],
        'Under Review - Governance': projects.filter(stage='Under_Review_governance').order_by('-submission_date')[:5],
        'Under Review - Final Governance': projects.filter(stage='Under_Review_Final_governance').order_by('-submission_date')[:5],
        'Governance Closure': projects.filter(stage='Governance_Closure').order_by('-submission_date')[:5],
    }
    
    # Get recent projects (get at least 20 for the Latest Requests buttons)
    recent_projects = projects.order_by('-submission_date')[:20]
    
    # Get projects sorted by priority (Top, High, Normal, Low)
    priority_sorted_projects = projects.extra(
        select={'priority_order': "CASE WHEN priority = 'Top' THEN 1 WHEN priority = 'High' THEN 2 WHEN priority = 'Normal' THEN 3 WHEN priority = 'Low' THEN 4 ELSE 5 END"}
    ).order_by('priority_order', '-submission_date')
    
    # Get high priority projects
    high_priority_projects = projects.filter(priority__in=['Top', 'High']).order_by('-submission_date')[:5]
    
    # Get top priority projects
    top_priority_projects = projects.filter(priority='Top').order_by('-submission_date')[:5]
    
    # Get projects by status for charts
    projects_by_status = []
    for status, count in status_counts.items():
        if count > 0:
            projects_by_status.append({'status': status, 'count': count})
    
    # Get projects by priority for charts
    projects_by_priority = []
    for priority in ['Top', 'High', 'Normal', 'Low']:
        count = projects.filter(priority=priority).count()
        if count > 0:
            projects_by_priority.append({'priority': priority, 'count': count})
    
    # Calculate priority counts for display
    priority_counts = {
        'Top': projects.filter(priority='Top').count(),
        'High': projects.filter(priority='High').count(),
        'Normal': projects.filter(priority='Normal').count(),
        'Low': projects.filter(priority='Low').count(),
    }
    
    # Calculate requests per department (all requests, not just active)
    department_counts = {}
    for project in projects:
        if project.department:
            if project.department in department_counts:
                department_counts[project.department] += 1
            else:
                department_counts[project.department] = 1
    
    # Sort departments by count (descending)
    department_counts = dict(sorted(department_counts.items(), key=lambda x: x[1], reverse=True))
    
    # Calculate daily request data for the last 12 months
    from datetime import datetime, timedelta
    from django.db.models import Count
    from django.utils import timezone
    
    # Get the date range (12 months back from today)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    # Get daily counts for the last 12 months
    daily_counts = projects.filter(
        submission_date__gte=start_date,
        submission_date__lte=end_date
    ).extra(
        select={'date': 'DATE(submission_date)'}
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    # Convert to a format suitable for Chart.js
    daily_data = {}
    for entry in daily_counts:
        # The date is already a string from the SQL DATE() function
        date_str = entry['date']
        daily_data[date_str] = entry['count']
    
    context = {
        'stage_counts': stage_counts,
        'status_counts': status_counts,
        'projects_by_stage': projects_by_stage,
        'recent_projects': recent_projects,
        'priority_sorted_projects': priority_sorted_projects,
        'high_priority_projects': high_priority_projects,
        'top_priority_projects': top_priority_projects,
        'projects_by_status': projects_by_status,
        'projects_by_priority': projects_by_priority,
        'priority_counts': priority_counts,
        'department_counts': department_counts,
        'daily_data': daily_data,
    }
    
    return render(request, 'projects/dashboard.html', context)


@login_required
@user_passes_test(is_patrick)
def test_dashboard(request):
    """Test dashboard - identical to main dashboard but only accessible to Patrick"""
    # Get all projects
    projects = Project.objects.all().order_by('-submission_date')
    
    # Get recent projects (get at least 20 for the Latest Requests buttons)
    recent_projects = projects[:20]
    
    # Get projects sorted by priority
    priority_sorted_projects = projects.order_by('-priority', '-submission_date')[:5]
    
    # Get high priority projects
    high_priority_projects = projects.filter(priority='High')[:5]
    
    # Get top priority projects
    top_priority_projects = projects.filter(priority='Top')[:5]
    
    # Calculate status counts
    status_counts = {}
    for status, _ in Project.STATUS_CHOICES:
        count = projects.filter(status=status).count()
        if count > 0:
            status_counts[status] = count
    
    # Calculate stage counts
    stage_counts = {}
    for stage, _ in Project.STAGE_CHOICES:
        count = projects.filter(stage=stage).count()
        if count > 0:
            stage_counts[stage] = count
    
    # Calculate projects by stage
    projects_by_stage = []
    for stage, _ in Project.STAGE_CHOICES:
        count = projects.filter(stage=stage).count()
        if count > 0:
            projects_by_stage.append({'stage': stage, 'count': count})
    
    # Calculate projects by status
    projects_by_status = []
    for status, _ in Project.STATUS_CHOICES:
        count = projects.filter(status=status).count()
        if count > 0:
            projects_by_status.append({'status': status, 'count': count})
    
    # Calculate projects by priority
    projects_by_priority = []
    for priority, _ in Project.PRIORITY_CHOICES:
        count = projects.filter(priority=priority).count()
        if count > 0:
            projects_by_priority.append({'priority': priority, 'count': count})
    
    # Calculate priority counts for display
    priority_counts = {
        'Top': projects.filter(priority='Top').count(),
        'High': projects.filter(priority='High').count(),
        'Normal': projects.filter(priority='Normal').count(),
        'Low': projects.filter(priority='Low').count(),
    }
    
    # Calculate requests per department (all requests, not just active)
    department_counts = {}
    for project in projects:
        if project.department:
            if project.department in department_counts:
                department_counts[project.department] += 1
            else:
                department_counts[project.department] = 1
    
    # Sort departments by count (descending)
    department_counts = dict(sorted(department_counts.items(), key=lambda x: x[1], reverse=True))
    
    # Calculate daily request data for the last 12 months
    from datetime import datetime, timedelta
    from django.db.models import Count
    from django.utils import timezone
    
    # Get the date range (12 months back from today)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    # Get daily counts for the last 12 months
    daily_counts = projects.filter(
        submission_date__gte=start_date,
        submission_date__lte=end_date
    ).extra(
        select={'date': 'DATE(submission_date)'}
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    # Convert to a format suitable for Chart.js
    daily_data = {}
    for entry in daily_counts:
        # The date is already a string from the SQL DATE() function
        date_str = entry['date']
        daily_data[date_str] = entry['count']
    
    # Calculate department requests by year for stacked bar chart
    from django.db.models.functions import ExtractYear
    
    # Get all projects with their submission year and department
    projects_with_year = projects.annotate(
        year=ExtractYear('submission_date')
    ).values('year', 'department').annotate(
        count=Count('id')
    ).order_by('year', 'department')
    
    # Organize data for stacked bar chart
    department_year_data = {}
    years = set()
    departments = set()
    
    for entry in projects_with_year:
        year = entry['year']
        department = entry['department'] if entry['department'] else 'Unknown'
        count = entry['count']
        
        years.add(year)
        departments.add(department)
        
        if year not in department_year_data:
            department_year_data[year] = {}
        department_year_data[year][department] = count
    
    # Sort years and departments
    years = sorted(list(years))
    departments = sorted(list(departments))
    
    # Create datasets for each department
    department_datasets = []
    department_colors = ['#D09B2C']  # CC Gold for all departments
    
    for i, department in enumerate(departments):
        data = []
        for year in years:
            count = department_year_data.get(year, {}).get(department, 0)
            data.append(count)
        
        department_datasets.append({
            'label': department,
            'data': data,
            'backgroundColor': department_colors[i % len(department_colors)],
            'borderColor': '#ffffff',  # White border for separation
            'borderWidth': 2  # Thicker border lines
        })
    
    context = {
        'stage_counts': stage_counts,
        'status_counts': status_counts,
        'projects_by_stage': projects_by_stage,
        'recent_projects': recent_projects,
        'priority_sorted_projects': priority_sorted_projects,
        'high_priority_projects': high_priority_projects,
        'top_priority_projects': top_priority_projects,
        'projects_by_status': projects_by_status,
        'projects_by_priority': projects_by_priority,
        'priority_counts': priority_counts,
        'department_counts': department_counts,
        'daily_data': daily_data,
        'department_year_labels': years,
        'department_year_datasets': department_datasets,
    }
    
    return render(request, 'projects/test_dashboard.html', context)


@login_required
@user_passes_test(lambda u: is_triage_user(u) or is_triage_lead_user(u))
def project_update_status(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Project.STATUS_CHOICES):
            project.status = new_status
            project.save()
            messages.success(request, 'Project status updated successfully!')
        else:
            messages.error(request, 'Invalid status selected.')
    
    return redirect('projects:project_update', pk=pk)

@login_required
def logout_view(request):
    """Simple logout view that logs out the user and redirects to home page"""
    from django.contrib.auth import logout as django_logout
    from django.contrib.sessions.models import Session
    
    # Force logout by clearing the session
    if request.user.is_authenticated:
        # Clear all sessions for this user
        Session.objects.filter(expire_date__gte=timezone.now()).delete()
        # Logout the user
        django_logout(request)
        # Clear the session
        request.session.flush()
    
    # Redirect to home with logout parameter instead of using messages
    return HttpResponseRedirect(reverse('projects:home') + '?logged_out=true')

@login_required
def project_intake_form(request):
    """Intake form for new project requests"""
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description')
            contact_person = request.POST.get('contact_person')
            contact_email = request.POST.get('contact_email')
            contact_phone = request.POST.get('contact_phone')
            same_as_requestor = request.POST.get('same_as_requestor') == 'on'
            
            # If "same as requestor" is checked, use the current user's information
            if same_as_requestor:
                # Use the user's full name if available, otherwise username
                user_full_name = f"{request.user.first_name} {request.user.last_name}".strip()
                contact_person = user_full_name if user_full_name else request.user.username
                contact_email = request.user.email
            
            # Validate required fields
            if not title:
                raise ValueError("Title is required")
            if not description:
                raise ValueError("Description is required")
            if not contact_person:
                raise ValueError("Contact person is required")
            if not contact_email:
                raise ValueError("Contact email is required")
            
            # Create new project
            project = Project.objects.create(
                title=title,
                description=description,
                contact_person=contact_person,
                contact_email=contact_email,
                contact_phone=contact_phone,
                submitted_by=request.user,
                status='pending',
                stage='Pending_Review'
            )
            
            # Handle file uploads
            files = request.FILES.getlist('files')
            if files:
                if len(files) > 5:
                    messages.error(request, 'You can upload a maximum of 5 files.')
                    return render(request, 'projects/intake_form.html')
                
                for file in files:
                    ProjectFile.objects.create(project=project, file=file)
            
            messages.success(request, f'Request "{project.title}" submitted successfully! Your request ID is {project.formatted_id}.')
            return redirect('projects:my_governance')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error submitting request: {str(e)}')
    
    return render(request, 'projects/intake_form.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def my_governance_superuser(request):
    """MyGovernance page specifically for SuperUsers - test page"""
    # Get all projects for SuperUser dashboard
    all_projects = Project.objects.all().order_by('-submission_date')
    
    # Get statistics
    total_projects = all_projects.count()
    pending_projects = all_projects.filter(stage='Pending_Review').count()
    triage_projects = all_projects.filter(stage='Under_Review_Triage').count()
    governance_projects = all_projects.filter(stage='Under_Review_governance').count()
    final_governance_projects = all_projects.filter(stage='Under_Review_Final_governance').count()
    closed_projects = all_projects.filter(stage='Governance_Closure').count()
    
    # Get recent projects
    recent_projects = all_projects[:10]
    
    # Get projects by priority
    priority_stats = {
        'Top': all_projects.filter(priority='Top').count(),
        'High': all_projects.filter(priority='High').count(),
        'Normal': all_projects.filter(priority='Normal').count(),
        'Low': all_projects.filter(priority='Low').count(),
    }
    
    # Get projects by type
    type_stats = {}
    for type_code, type_name in Project.PROJECT_TYPE_CHOICES:
        count = all_projects.filter(project_type=type_code).count()
        if count > 0:
            type_stats[type_name] = count
    
    # Get active system notifications
    notifications = SystemNotification.objects.filter(is_active=True).order_by('-created_at')
    
    context = {
        'total_projects': total_projects,
        'pending_projects': pending_projects,
        'triage_projects': triage_projects,
        'governance_projects': governance_projects,
        'final_governance_projects': final_governance_projects,
        'closed_projects': closed_projects,
        'recent_projects': recent_projects,
        'priority_stats': priority_stats,
        'type_stats': type_stats,
        'all_projects': all_projects,
        'notifications': notifications,
    }
    
    return render(request, 'projects/my_governance_superuser.html', context)

def my_governance(request):
    """My Governance page - shows user's submitted requests and contact requests"""
    # Handle anonymous users
    if not request.user.is_authenticated:
        user_projects = Project.objects.none()
        contact_projects = Project.objects.none()
        triage_projects = None
        governance_projects = None
        final_governance_projects = None
    else:
        # Get all projects submitted by the current user
        user_projects = Project.objects.filter(submitted_by=request.user).order_by('-submission_date')
        
        # Get all projects where the user is the contact person
        # Check by full name first, then by username if no match
        user_full_name = request.user.get_full_name()
        user_username = request.user.username
        
        contact_projects = Project.objects.filter(
            Q(contact_person=user_full_name) | 
            Q(contact_person=user_username)
        ).exclude(submitted_by=request.user).order_by('-submission_date')
    
        # Get triage projects for users in Triage Group or Triage Group Lead, or superusers
        triage_projects = None
        if request.user.is_superuser or is_triage_user(request.user) or is_triage_lead_user(request.user):
            # Get projects in triage stages only (excluding deleted and user's own projects)
            triage_projects = Project.objects.filter(
                stage__in=['Pending_Review', 'Under_Review_Triage']
            ).exclude(
                submitted_by=request.user
            ).exclude(
                stage='Deleted'
            ).order_by('-submission_date')
        
        # Get governance projects for users in governance groups or superusers
        governance_projects = None
        if (request.user.is_superuser or 
            is_ai_governance_user(request.user) or is_ai_governance_lead_user(request.user) or 
            is_erp_governance_user(request.user) or is_erp_governance_lead_user(request.user) or
            is_it_governance_user(request.user) or is_it_governance_lead_user(request.user) or
            is_process_improvement_user(request.user) or is_process_improvement_lead_user(request.user)):
            # Get all projects that are in governance review stage
            governance_projects = Project.objects.filter(
                stage='Under_Review_governance'
            )
            
            # Filter by project type based on user's group (superusers see all types)
            if not request.user.is_superuser:
                allowed_types = []
                if is_ai_governance_user(request.user) or is_ai_governance_lead_user(request.user):
                    allowed_types.append('ai_governance')
                if is_erp_governance_user(request.user) or is_erp_governance_lead_user(request.user):
                    allowed_types.append('erp_governance')
                if is_it_governance_user(request.user) or is_it_governance_lead_user(request.user):
                    allowed_types.append('it_governance')
                if is_process_improvement_user(request.user) or is_process_improvement_lead_user(request.user):
                    allowed_types.append('process_improvement')
                
                if allowed_types:
                    # Governance groups see only their specific project types
                    governance_projects = governance_projects.filter(project_type__in=allowed_types)
            
            governance_projects = governance_projects.order_by('-submission_date')
        
        # Get final governance projects for scoring users, superusers, or triage users
        final_governance_projects = None
        if request.user.is_superuser or is_scoring_user(request.user) or is_triage_user(request.user) or is_triage_lead_user(request.user):
            # Get projects in final governance review stage
            final_governance_projects = Project.objects.filter(
                stage='Under_Review_Final_governance'
            )
            
            # Apply group-based filtering if user is not staff or superuser
            if not request.user.is_staff and not request.user.is_superuser:
                allowed_types = get_user_allowed_project_types(request.user)
                if allowed_types is not None:
                    final_governance_projects = final_governance_projects.filter(project_type__in=allowed_types)
            
            final_governance_projects = final_governance_projects.order_by(
                models.F('final_priority').asc(nulls_last=True), 
                '-submission_date'
            )
    
    # Determine user's committee/role for display
    def get_user_committee_display(user):
        if user.is_superuser:
            return "SuperUser"
        
        committees = []
        if is_triage_lead_user(user):
            committees.append("Triage Lead")
        elif is_triage_user(user):
            committees.append("Triage")
            
        if is_ai_governance_lead_user(user):
            committees.append("AI Governance Lead")
        elif is_ai_governance_user(user):
            committees.append("AI Governance")
            
        if is_erp_governance_lead_user(user):
            committees.append("ERP Governance Lead")
        elif is_erp_governance_user(user):
            committees.append("ERP Governance")
            
        if is_it_governance_lead_user(user):
            committees.append("IT Governance Lead")
        elif is_it_governance_user(user):
            committees.append("IT Governance")
            
        if is_process_improvement_lead_user(user):
            committees.append("Process Improvement Lead")
        elif is_process_improvement_user(user):
            committees.append("Process Improvement")
        
        return " | ".join(committees) if committees else "User"
    
    context = {
        'user_projects': user_projects,
        'contact_projects': contact_projects,
        'triage_projects': triage_projects,
        'governance_projects': governance_projects,
        'final_governance_projects': final_governance_projects,
        'is_triage_user': is_triage_user(request.user),
        'is_triage_lead_user': is_triage_lead_user(request.user),
        'is_ai_governance_user': is_ai_governance_user(request.user),
        'is_ai_governance_lead_user': is_ai_governance_lead_user(request.user),
        'is_erp_governance_user': is_erp_governance_user(request.user),
        'is_erp_governance_lead_user': is_erp_governance_lead_user(request.user),
        'is_it_governance_user': is_it_governance_user(request.user),
        'is_it_governance_lead_user': is_it_governance_lead_user(request.user),
        'is_process_improvement_user': is_process_improvement_user(request.user),
        'is_process_improvement_lead_user': is_process_improvement_lead_user(request.user),
        'is_scoring_user': is_scoring_user(request.user),
        'is_superuser': request.user.is_superuser,
        'can_modify_final_priority': can_modify_final_priority(request.user),
        'user_committee_display': get_user_committee_display(request.user),
    }
    return render(request, 'projects/my_governance.html', context)

@login_required
def project_details_readonly(request, pk):
    """API endpoint to get project details for superuser read-only view"""
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        project.final_priority = request.POST.get('final_priority')
        project.final_score = request.POST.get('final_score')
        project.scoring_notes = request.POST.get('scoring_notes')
        
        try:
            project.save()
            messages.success(request, 'Project final scoring updated successfully!')
            return redirect('projects:project_final_scoring_list')
        except Exception as e:
            messages.error(request, f'Error updating project final scoring: {str(e)}')
    
    # Prepare project data for read-only display
    project_data = {
        'id': project.id,
        'title': project.title,
        'description': project.description,
        'formatted_id': project.formatted_id,
        'project_type_display': project.get_project_type_display(),
        'priority_display': project.get_priority_display(),
        'department': project.department,
        'stage_display': project.get_stage_display(),
        'status_display': project.get_status_display(),
        'submitted_by_name': project.submitted_by.get_full_name() if project.submitted_by else project.submitted_by.username if project.submitted_by else 'Unknown',
        'submission_date_formatted': project.submission_date.strftime('%B %d, %Y') if project.submission_date else 'N/A',
        'final_score': project.final_score,
        'final_priority': project.final_priority,
        'triage_notes': project.triage_notes,
    }
    
    return JsonResponse({'project': project_data})

@login_required
def api_users(request):
    """API endpoint to get all users for autocomplete"""
    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')
    
    user_data = []
    for user in users:
        full_name = user.get_full_name() if user.first_name and user.last_name else user.username
        user_data.append({
            'id': user.id,
            'username': user.username,
            'full_name': full_name,
            'email': user.email
        })
    
    return JsonResponse({'users': user_data})

@login_required
@user_passes_test(lambda u: is_triage_user(u) or is_triage_lead_user(u))
@require_POST
def project_delete_request(request, pk):
    """
    Mark a project as deleted with a reason.
    Only triage users can delete projects.
    """
    try:
        project = get_object_or_404(Project, pk=pk)
        reason = request.POST.get('reason', '').strip()
        
        if not reason:
            return JsonResponse({
                'success': False,
                'message': 'A reason for deletion is required.'
            })
        
        # Capture old stage value before changing
        old_stage = project.stage
        
        # Update the project stage to 'Deleted'
        project.stage = 'Deleted'
        project.save()
        
        # Create a triage note with the deletion reason
        TriageNote.objects.create(
            project=project,
            notes=f"Request deleted by {request.user.get_full_name() or request.user.username}. Reason: {reason}",
            created_by=request.user
        )
        
        # Create a triage change record
        TriageChange.objects.create(
            project=project,
            changed_by=request.user,
            field_name='stage',
            field_label='Stage',
            old_value=old_stage,
            new_value='Deleted'
        )
        
        logger.info(f"Project {project.id} ({project.title}) deleted by {request.user.username}. Reason: {reason}")
        
        return JsonResponse({
            'success': True,
            'message': 'Request has been marked as deleted successfully.'
        })
        
    except Exception as e:
        logger.error(f"Error deleting project {pk}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while deleting the request.'
        })

@login_required
def debug_project_files(request, pk):
    """Debugging endpoint to list files for a specific project"""
    project = get_object_or_404(Project, pk=pk)
    files = project.projectfile_set.all()
    
    file_data = []
    for file in files:
        file_data.append({
            'id': file.id,
            'name': file.file.name,
            'size': file.file.size,
            'upload_date': file.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return JsonResponse({'files': file_data})

@login_required
def get_project_conversations(request, pk):
    """Get all conversations for a specific project"""
    try:
        project = get_object_or_404(Project, pk=pk)
        conversations = project.conversations.all()
        
        data = [{
            'id': conv.id,
            'message': conv.message,
            'created_by': conv.created_by.get_full_name() or conv.created_by.username,
            'created_at': conv.created_at.isoformat(),
            'is_internal': conv.is_internal,
        } for conv in conversations]
        
        return JsonResponse({'conversations': data, 'success': True})
    except Exception as e:
        logger.error(f"Error fetching conversations for project {pk}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def add_project_conversation(request, pk):
    """Add a new conversation/note to a project"""
    try:
        project = get_object_or_404(Project, pk=pk)
        message = request.POST.get('message', '').strip()
        
        if not message:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'}, status=400)
        
        conversation = Conversation.objects.create(
            project=project,
            message=message,
            created_by=request.user,
            is_internal=True
        )
        
        return JsonResponse({
            'success': True,
            'conversation': {
                'id': conversation.id,
                'message': conversation.message,
                'created_by': conversation.created_by.get_full_name() or conversation.created_by.username,
                'created_at': conversation.created_at.isoformat(),
                'is_internal': conversation.is_internal,
            }
        })
    except Exception as e:
        logger.error(f"Error adding conversation to project {pk}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_notifications(request):
    """Manage system notifications (superuser only)"""
    notifications = SystemNotification.objects.all()
    return render(request, 'projects/manage_notifications.html', {
        'notifications': notifications
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_POST
def add_notification(request):
    """Add a new system notification"""
    try:
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        notification_type = request.POST.get('notification_type', 'info')
        is_active = request.POST.get('is_active') == 'true'
        
        if not title or not message:
            return JsonResponse({'success': False, 'error': 'Title and message are required'}, status=400)
        
        notification = SystemNotification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            is_active=is_active,
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'notification': {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.get_notification_type_display(),
                'is_active': notification.is_active,
                'created_at': notification.created_at.strftime('%b %d, %Y %I:%M %p')
            }
        })
    except Exception as e:
        logger.error(f"Error adding notification: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_POST
def update_notification(request, pk):
    """Update an existing notification"""
    try:
        notification = get_object_or_404(SystemNotification, pk=pk)
        
        notification.title = request.POST.get('title', notification.title).strip()
        notification.message = request.POST.get('message', notification.message).strip()
        notification.notification_type = request.POST.get('notification_type', notification.notification_type)
        notification.is_active = request.POST.get('is_active') == 'true'
        notification.save()
        
        return JsonResponse({
            'success': True,
            'notification': {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.get_notification_type_display(),
                'is_active': notification.is_active,
                'updated_at': notification.updated_at.strftime('%b %d, %Y %I:%M %p')
            }
        })
    except Exception as e:
        logger.error(f"Error updating notification {pk}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(lambda u: u.is_superuser)
@require_POST
def delete_notification(request, pk):
    """Delete a notification"""
    try:
        notification = get_object_or_404(SystemNotification, pk=pk)
        notification.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error deleting notification {pk}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
