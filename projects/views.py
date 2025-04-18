from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Project, ProjectFile
from .forms import ProjectForm
import json

def project_list(request):
    projects = Project.objects.all().select_related('submitted_by')
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
@user_passes_test(lambda u: u.is_staff)
def project_triage(request):
    projects = Project.objects.all().select_related('submitted_by').order_by('-submission_date')
    return render(request, 'projects/triage.html', {'projects': projects})

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
@csrf_exempt
def project_update_ajax(request, pk):
    try:
        project = get_object_or_404(Project, pk=pk)
        data = json.loads(request.body)
        
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
            project.submitted_by = request.user if request.user.is_authenticated else None
            project.priority = 'Normal'  # Set default priority
            project.save()
            
            # Handle file uploads
            for file in files:
                ProjectFile.objects.create(project=project, file=file)
            
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
    
    if request.method == 'POST':
        # Update project fields
        project.title = request.POST.get('title')
        project.description = request.POST.get('description')
        project.project_type = request.POST.get('project_type')
        project.priority = request.POST.get('priority')
        project.status = request.POST.get('status')
        project.department = request.POST.get('department')
        project.notes = request.POST.get('notes')
        
        try:
            project.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('projects:project_triage')
        except Exception as e:
            messages.error(request, f'Error updating project: {str(e)}')
    
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
