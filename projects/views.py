from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Project, ProjectFile, ProjectScore
from .forms import ProjectForm
import json
from django.utils import timezone
from django.db import models

def project_list(request):
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', '')
    projects = Project.objects.all().select_related('submitted_by')
    
    # Filter for user's projects if requested
    if filter_type == 'my_projects' and request.user.is_authenticated:
        projects = projects.filter(submitted_by=request.user)
    
    if search_query:
        projects = projects.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(department__icontains=search_query) |
            models.Q(submitted_by__username__icontains=search_query)
        )
    
    return render(request, 'projects/project_list.html', {
        'projects': projects, 
        'search_query': search_query,
        'filter_type': filter_type
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def project_triage(request):
    search_query = request.GET.get('search', '')
    projects = Project.objects.all().select_related('submitted_by').order_by('-submission_date')
    
    if search_query:
        projects = projects.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(department__icontains=search_query) |
            models.Q(submitted_by__username__icontains=search_query)
        )
    
    return render(request, 'projects/triage.html', {'projects': projects, 'search_query': search_query})

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
@csrf_exempt
def project_update_ajax(request, pk):
    try:
        project = get_object_or_404(Project, pk=pk)
        
        # Debug print
        print(f"Updating project {pk}")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        
        # Update project fields
        title = request.POST.get('title')
        if not title:
            raise ValueError("Title is required")
        
        print(f"Title: {title}")
        print(f"Current project title: {project.title}")
        
        project.title = title
        project.description = request.POST.get('description', '')
        project.project_type = request.POST.get('project_type')
        project.priority = request.POST.get('priority')
        project.status = request.POST.get('status')
        project.department = request.POST.get('department', '')
        project.notes = request.POST.get('notes', '')
        
        # Update triage information
        project.triage_notes = request.POST.get('triage_notes', '')
        project.triaged_by = request.user
        project.triage_date = timezone.now()
        
        # Update contact information
        project.contact_person = request.POST.get('contact_person', '')
        project.contact_email = request.POST.get('contact_email', '')
        
        # Handle submitted_by field
        submitted_by_username = request.POST.get('submitted_by')
        if submitted_by_username:
            try:
                # Try to find the user by username
                user = User.objects.get(username=submitted_by_username)
                project.submitted_by = user
            except User.DoesNotExist:
                # If user doesn't exist, keep the current submitted_by
                pass
        
        print("About to save project...")
        try:
            # Save the project
            project.save()
            print(f"Project {pk} updated successfully")
            print(f"Contact person: {project.contact_person}")  # Debug log for contact person
        except Exception as e:
            print(f"Error saving project: {str(e)}")
            print(f"Project fields before save: {project.__dict__}")
            raise
        
        # Handle file uploads
        files = request.FILES.getlist('files')
        if files:
            print(f"Processing {len(files)} files")
            if len(files) > 5:
                return JsonResponse({'success': False, 'error': 'You can upload a maximum of 5 files.'})
            
            for file in files:
                ProjectFile.objects.create(project=project, file=file)
        
        return JsonResponse({'success': True})
    except ValueError as e:
        print(f"Validation error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        print(f"Error updating project {pk}: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error args: {e.args}")
        return JsonResponse({'success': False, 'error': str(e)})

def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.submitted_by = request.user if request.user.is_authenticated else None
            project.status = 'pending'
            project.priority = 'Normal'
            project.save()
            
            messages.success(request, 'Project submitted successfully!')
            return redirect('projects:project_list')
    else:
        form = ProjectForm()
    
    return render(request, 'projects/project_form.html', {'form': form})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project_detail.html', {'project': project})

@login_required
@user_passes_test(lambda u: u.is_staff)
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    print(f"Project update view called for project {pk}")
    print(f"Request method: {request.method}")
    print(f"Request path: {request.path}")
    print(f"Request POST data: {request.POST}")
    print(f"Request FILES data: {request.FILES}")
    
    if request.method == 'POST':
        print("POST request received")  # Debug log
        print(f"POST data: {request.POST}")  # Debug log
        print(f"FILES data: {request.FILES}")  # Debug log
        
        try:
            # Update project fields
            title = request.POST.get('title')
            if not title:
                raise ValueError("Title is required")
            
            project.title = title
            project.description = request.POST.get('description', '')
            project.project_type = request.POST.get('project_type')
            project.priority = request.POST.get('priority')
            project.status = request.POST.get('status')
            project.department = request.POST.get('department', '')
            project.notes = request.POST.get('notes', '')
            project.triage_notes = request.POST.get('triage_notes', '')
            project.contact_person = request.POST.get('contact_person', '')
            
            # Save the project
            project.save()
            print("Project saved successfully")  # Debug log
            print(f"Contact person: {project.contact_person}")  # Debug log for contact person
            
            # Handle file uploads
            files = request.FILES.getlist('files')
            if files:
                print(f"Processing {len(files)} files")  # Debug log
                if len(files) > 5:
                    messages.error(request, 'You can upload a maximum of 5 files.')
                    return render(request, 'projects/project_edit.html', {'project': project})
                
                for file in files:
                    ProjectFile.objects.create(project=project, file=file)
                messages.success(request, 'Files uploaded successfully!')
            
            messages.success(request, 'Project updated successfully!')
            return redirect('projects:project_detail', pk=pk)
            
        except ValueError as e:
            print(f"Validation error: {str(e)}")  # Debug log
            messages.error(request, f'Error updating project: {str(e)}')
            return render(request, 'projects/project_edit.html', {'project': project})
        except Exception as e:
            print(f"Error saving project: {str(e)}")  # Debug log
            messages.error(request, f'Error updating project: {str(e)}')
            return render(request, 'projects/project_edit.html', {'project': project})
    
    return render(request, 'projects/project_edit.html', {'project': project})

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
@user_passes_test(lambda u: u.is_staff)
def project_scoring_list(request):
    search_query = request.GET.get('search', '')
    projects = Project.objects.all().select_related('submitted_by').order_by('-submission_date')
    
    if search_query:
        projects = projects.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(department__icontains=search_query) |
            models.Q(submitted_by__username__icontains=search_query)
        )
    
    return render(request, 'projects/project_scoring_list.html', {'projects': projects, 'search_query': search_query})

@login_required
@user_passes_test(lambda u: u.is_staff)
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
@user_passes_test(lambda u: u.is_staff)
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
@user_passes_test(lambda u: u.is_staff)
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
@user_passes_test(lambda u: u.is_staff)
def project_final_scoring_details(request, pk):
    project = get_object_or_404(Project, pk=pk)
    scores = project.scores.all().order_by('-created_at')
    
    return render(request, 'projects/project_final_scoring_details.html', {
        'project': project,
        'scores': scores
    })
