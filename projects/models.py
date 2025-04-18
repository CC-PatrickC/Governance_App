from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Top', 'Top'),
    ]

    FINAL_PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    ]

    PROJECT_TYPE_CHOICES = [
        ('not_yet_decided', 'Not Yet Decided'),
        ('process_improvement', 'Process Improvement'),
        ('it_governance', 'IT Governance'),
        ('erp_governance', 'ERP Governance'),
        ('data_governance', 'Data Governance'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='not_yet_decided', help_text="Type of project submission")
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    submission_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    triage_notes = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Normal')
    scoring_notes = models.TextField(blank=True, null=True, help_text="Notes related to project scoring or evaluation")
    final_priority = models.IntegerField(choices=FINAL_PRIORITY_CHOICES, null=True, blank=True, help_text="Final priority score (1=Low, 2=Medium, 3=High)")
    final_score = models.IntegerField(null=True, blank=True, help_text="Final score (0-100)")

    def __str__(self):
        return self.title

    @property
    def formatted_id(self):
        return f"PRJ-{self.id:03d}"

    class Meta:
        ordering = ['-submission_date']
        db_table = 'project_requests'

class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='project_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.title} - {self.file.name}"

    class Meta:
        ordering = ['-uploaded_at']
