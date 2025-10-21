from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
<<<<<<< Updated upstream
from .models import Project, ProjectFile
=======
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import AuthenticationForm
from .models import Project, ProjectFile, ProjectScore, TriageNote, TriageChange, Conversation, SystemNotification
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
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
            
            # Handle file uploads
            files = request.FILES.getlist('files')
            if files:
                if len(files) > 5:
                    messages.error(request, 'You can upload a maximum of 5 files.')
                    return render(request, 'projects/project_edit.html', {'project': project})
                
                for file in files:
                    ProjectFile.objects.create(project=project, file=file)
                messages.success(request, 'Files uploaded successfully!')
            
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
    projects = Project.objects.all().select_related('submitted_by').order_by('-submission_date')
    return render(request, 'projects/project_scoring_list.html', {'projects': projects})

@login_required
@user_passes_test(lambda u: u.is_staff)
<<<<<<< Updated upstream
def project_scoring(request, pk):
=======
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

@login_not_required
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
>>>>>>> Stashed changes
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
            return redirect('projects:project_scoring', pk=pk)
        except Exception as e:
            messages.error(request, f'Error updating project scoring: {str(e)}')
    
<<<<<<< Updated upstream
    return render(request, 'projects/project_scoring.html', {'project': project})
=======
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
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
