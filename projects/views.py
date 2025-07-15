from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from .models import Project, ProjectFile, ProjectScore, TriageNote
from .forms import ProjectForm
import json
from django.utils import timezone
from django.db import models
import logging

logger = logging.getLogger('projects')

def is_triage_user(user):
    return user.is_staff or user.groups.filter(name='Triage Group').exists()

def is_scoring_user(user):
    return user.is_staff or user.groups.filter(name='Scoring Group').exists()

def is_cabinet_user(user):
    return user.is_staff or user.groups.filter(name='Cabinet Group').exists()

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
@user_passes_test(is_triage_user)
def project_triage(request):
    search_query = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    priority_filter = request.GET.get('priority', '')
    status_filter = request.GET.get('status', '')
    stage_filter = request.GET.get('stage', '')
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
@user_passes_test(lambda u: u.is_staff or u.groups.filter(name='Triage Group').exists())
def project_update_ajax(request, pk):
    logger.info(f"=== Project Update Request ===")
    logger.info(f"Request method: {request.method}")
    logger.info(f"User: {request.user} (Staff: {request.user.is_staff}, Groups: {request.user.groups.all()})")
    logger.info(f"Project ID: {pk}")
    
    if request.method != 'POST':
        logger.info("Not a POST request, rendering form")
        return render(request, 'projects/project_edit.html', {'project': get_object_or_404(Project, pk=pk)})
        
    try:
        project = get_object_or_404(Project, pk=pk)
        logger.info(f"\nProject details before update:")
        logger.info(f"Title: {project.title}")
        logger.info(f"Status: {project.status}")
        logger.info(f"Description: {project.description}")
        
        # Debug print
        logger.info(f"\nForm data received:")
        logger.info(f"POST data: {dict(request.POST)}")
        logger.info(f"FILES data: {dict(request.FILES)}")
        
        # Update project fields
        title = request.POST.get('title')
        if not title:
            logger.error("Error: Title is missing")
            raise ValueError("Title is required")
        
        # Debug status update
        new_status = request.POST.get('status')
        logger.info(f"\nStatus update:")
        logger.info(f"New status from form: {new_status}")
        logger.info(f"Current project status: {project.status}")
        logger.info(f"Valid status choices: {dict(Project.STATUS_CHOICES)}")
        
        # Validate status
        valid_statuses = dict(Project.STATUS_CHOICES).keys()
        if not new_status or new_status not in valid_statuses:
            logger.warning(f"Warning: Invalid status '{new_status}', defaulting to 'pending'")
            new_status = 'pending'
        
        # Update project fields
        project.title = title
        project.description = request.POST.get('description', '')
        project.project_type = request.POST.get('project_type')
        project.priority = request.POST.get('priority')
        
        # Explicitly update status
        logger.info(f"\nSetting status to: {new_status}")
        project.status = new_status
        logger.info(f"Status after setting: {project.status}")
        
        project.department = request.POST.get('department', '')
        project.notes = request.POST.get('notes', '')
        
        # Update triage information
        project.triage_notes = request.POST.get('triage_notes', '')
        project.triaged_by = request.user
        project.triage_date = timezone.now()
        
        # Update contact information
        project.contact_person = request.POST.get('contact_person', '')
        project.contact_email = request.POST.get('contact_email', '')
        
        logger.info("\nAbout to save project...")
        logger.info(f"Project status before save: {project.status}")
        try:
            # Save the project
            project.save()
            logger.info(f"\nProject {pk} updated successfully")
            logger.info(f"Project status after save: {project.status}")
            
            # Verify the status was saved
            project.refresh_from_db()
            logger.info(f"Project status after refresh: {project.status}")
            
        except Exception as e:
            logger.error(f"\nError saving project:")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error message: {str(e)}")
            logger.error(f"Project fields before save: {project.__dict__}")
            raise
        
        # Handle file uploads
        files = request.FILES.getlist('files')
        if files:
            logger.info(f"\nProcessing {len(files)} files")
            if len(files) > 5:
                messages.error(request, 'You can upload a maximum of 5 files.')
                return render(request, 'projects/project_edit.html', {'project': project})
            
            for file in files:
                ProjectFile.objects.create(project=project, file=file)
        
        messages.success(request, 'Project updated successfully!')
        return redirect('projects:project_triage')
    except ValueError as e:
        logger.error(f"\nValidation error: {str(e)}")
        messages.error(request, str(e))
        return render(request, 'projects/project_edit.html', {'project': project})
    except Exception as e:
        logger.error(f"\nError updating project {pk}:")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Error args: {e.args}")
        messages.error(request, f'Error updating project: {str(e)}')
        return render(request, 'projects/project_edit.html', {'project': project})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
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
    return render(request, 'projects/project_detail.html', {'project': project})

@login_required
@user_passes_test(is_triage_user)
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
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
            
            # Get and validate status
            new_status = request.POST.get('status')
            print(f"\nStatus update:")
            print(f"New status: {new_status}")
            print(f"Current status: {project.status}")
            print(f"Valid statuses: {dict(Project.STATUS_CHOICES)}")
            
            if not new_status:
                raise ValueError("Status is required")
            
            valid_statuses = dict(Project.STATUS_CHOICES).keys()
            if new_status not in valid_statuses:
                raise ValueError(f"Invalid status: {new_status}")
            
            # Get triage notes
            new_triage_notes = request.POST.get('triage_notes', '')
            
            # Update project fields
            project.title = title
            project.description = request.POST.get('description', '')
            project.project_type = request.POST.get('project_type')
            project.priority = request.POST.get('priority')
            project.status = new_status
            project.department = request.POST.get('department', '')
            project.notes = request.POST.get('notes', '')
            project.contact_person = request.POST.get('contact_person', '')
            
            # Only create a new TriageNote if the notes have changed
            if new_triage_notes != project.triage_notes:
                project.triage_notes = new_triage_notes
                TriageNote.objects.create(
                    project=project,
                    notes=new_triage_notes,
                    created_by=request.user
                )
            
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
@user_passes_test(is_triage_user)
def project_update_form_ajax(request, pk):
    """AJAX endpoint to get just the edit form content"""
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project_edit_form.html', {'project': project})

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
@user_passes_test(lambda u: u.is_staff)
def delete_attachment(request, project_pk, file_pk):
    project = get_object_or_404(Project, pk=project_pk)
    file = get_object_or_404(ProjectFile, pk=file_pk, project=project)
    
    if request.method == 'POST':
        try:
            file.delete()
            messages.success(request, 'Attachment deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting attachment: {str(e)}')
    
    return redirect('projects:project_update', pk=project_pk)

@login_required
@user_passes_test(is_scoring_user)
def project_scoring_list(request):
    search_query = request.GET.get('search', '')
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
        'type_filter': type_filter,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'project_types': project_types,
        'priorities': priorities,
        'status_choices': status_choices,
        'departments': departments,
    }
    
    return render(request, 'projects/project_scoring_list.html', context)

@login_required
@user_passes_test(is_scoring_user)
def project_scoring(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        try:
            # Convert form data to integers
            strategic_alignment = int(request.POST.get('strategic_alignment', 1))
            cost_benefit = int(request.POST.get('cost_benefit', 1))
            user_impact = int(request.POST.get('user_impact', 1))
            ease_of_implementation = int(request.POST.get('ease_of_implementation', 1))
            vendor_reputation_support = int(request.POST.get('vendor_reputation_support', 1))
            security_compliance = int(request.POST.get('security_compliance', 1))
            student_centered = int(request.POST.get('student_centered', 1))
            
            # Get or create the ProjectScore instance for this user and project
            score, created = ProjectScore.objects.get_or_create(
                project=project,
                scored_by=request.user,
                defaults={
                    'strategic_alignment': strategic_alignment,
                    'cost_benefit': cost_benefit,
                    'user_impact': user_impact,
                    'ease_of_implementation': ease_of_implementation,
                    'vendor_reputation_support': vendor_reputation_support,
                    'security_compliance': security_compliance,
                    'student_centered': student_centered,
                    'scoring_notes': request.POST.get('scoring_notes')
                }
            )
            
            if not created:
                # Update existing score
                score.strategic_alignment = strategic_alignment
                score.cost_benefit = cost_benefit
                score.user_impact = user_impact
                score.ease_of_implementation = ease_of_implementation
                score.vendor_reputation_support = vendor_reputation_support
                score.security_compliance = security_compliance
                score.student_centered = student_centered
                score.scoring_notes = request.POST.get('scoring_notes')
            
            # Save the score - this will automatically calculate and save the final_score
            score.save()
            
            # Update the project's final score based on the average of all scores
            project.update_final_score()
            
            messages.success(request, 'Project scoring updated successfully!')
            return redirect('projects:project_scoring', pk=pk)
        except ValueError as e:
            messages.error(request, f'Error updating project scoring: Invalid score value. Please ensure all scores are numbers between 1 and 5.')
            return redirect('projects:project_scoring', pk=pk)
        except Exception as e:
            messages.error(request, f'Error updating project scoring: {str(e)}')
            return redirect('projects:project_scoring', pk=pk)
    
    # Get the user's existing score if it exists
    user_score = ProjectScore.objects.filter(project=project, scored_by=request.user).first()
    
    return render(request, 'projects/project_scoring.html', {
        'project': project,
        'user_score': user_score
    })

@login_required
@user_passes_test(is_scoring_user)
def project_final_scoring_list(request):
    search_query = request.GET.get('search', '')
    projects = Project.objects.all().select_related('submitted_by').order_by('-final_priority', '-submission_date')
    
    if search_query:
        projects = projects.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(department__icontains=search_query) |
            models.Q(submitted_by__username__icontains=search_query)
        )
    
    return render(request, 'projects/project_final_scoring_list.html', {'projects': projects, 'search_query': search_query})

@login_required
@user_passes_test(is_scoring_user)
def project_final_scoring(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        project.final_priority = request.POST.get('final_priority')
        # Store the raw final score value
        final_score = request.POST.get('final_score')
        if final_score:
            try:
                # Store the raw final score value as a float
                project.final_score = float(final_score)
            except (ValueError, TypeError):
                # If conversion fails, use the sum of all scores
                project.final_score = project.average_final_score
        else:
            # If no final score provided, use the sum of all scores
            project.final_score = project.average_final_score
            
        project.scoring_notes = request.POST.get('scoring_notes')
        
        try:
            project.save()
            messages.success(request, 'Project final scoring updated successfully!')
            return redirect('projects:project_final_scoring_list')
        except Exception as e:
            messages.error(request, f'Error updating project final scoring: {str(e)}')
    
    # Ensure the final score is set to the sum of all scores before rendering
    if project.final_score is None:
        project.final_score = project.average_final_score
        project.save()
        
    return render(request, 'projects/project_final_scoring.html', {
        'project': project,
        'scores': project.projectscore_set.all().order_by('-created_at')
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
@csrf_exempt
def update_final_priority(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    try:
        data = json.loads(request.body)
        final_priority = data.get('final_priority')
        
        if final_priority is not None:
            # Convert to integer and save
            project.final_priority = int(final_priority)
            project.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'No priority value provided'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_scoring_user)
def project_final_scoring_details(request, pk):
    project = get_object_or_404(Project, pk=pk)
    scores = project.scores.all().order_by('-created_at')
    
    return render(request, 'projects/project_final_scoring_details.html', {
        'project': project,
        'scores': scores
    })

@login_required
@user_passes_test(is_cabinet_user)
def cabinet_dashboard(request):
    # Get all projects for statistics
    projects = Project.objects.all()
    
    # Calculate statistics
    stage_counts = {
        'Triage': projects.filter(status='Pending').count(),
        'Scoring': projects.filter(status='In Progress').count(),
        'Final Scoring': projects.filter(status='Final Review').count(),
        'Complete': projects.filter(status__in=['Approved', 'Rejected']).count()
    }
    
    status_counts = {
        'Pending': projects.filter(status='Pending').count(),
        'In Progress': projects.filter(status='In Progress').count(),
        'Final Review': projects.filter(status='Final Review').count(),
        'Approved': projects.filter(status='Approved').count(),
        'Rejected': projects.filter(status='Rejected').count()
    }
    
    # Get recent projects
    recent_projects = projects.order_by('-submission_date')[:5]
    
    # Get high priority projects
    high_priority_projects = projects.filter(priority__in=['Top', 'High']).order_by('-submission_date')
    
    context = {
        'stage_counts': stage_counts,
        'status_counts': status_counts,
        'recent_projects': recent_projects,
        'high_priority_projects': high_priority_projects,
    }
    
    return render(request, 'projects/dashboard.html', context)

@login_required
@user_passes_test(is_triage_user)
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
def cc_theme_home(request):
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
    
    # Apply my projects filter
    if filter_type == 'my_projects':
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
    
    return render(request, 'projects/cc_theme_home.html', context)
