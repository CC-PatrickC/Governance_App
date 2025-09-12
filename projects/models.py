from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('under_review_triage', 'Under Review - Triage'),
        ('under_review_governance', 'Under Review - Governance'),
        ('under_review_final_governance', 'Under Review - Final Governance'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]

    STAGE_CHOICES = [
        ('Pending_Review', 'Pending Review'),
        ('Under_Review_Triage', 'Under Review - Triage'),
        ('Under_Review_governance', 'Under Review - Governance'),
        ('Under_Review_Final_governance', 'Under Review - Final Governance'),
        ('Governance_Closure', 'Governance Closed'),
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
        ('ai_governance', 'AI Governance'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    project_type = models.CharField(
        max_length=20, 
        choices=PROJECT_TYPE_CHOICES, 
        default='not_yet_decided', 
        verbose_name="Request Type",
        help_text="Type of request submission"
    )
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    submission_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='Pending_Review', help_text="Current stage of the project")
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
    final_priority = models.IntegerField(null=True, blank=True, help_text="Project ranking (lower number = higher priority)")
    final_score = models.FloatField(null=True, blank=True, help_text="Final score")
    strategic_alignment = models.IntegerField(null=True, blank=True, help_text="Strategic alignment score (1-5)")
    cost_benefit = models.IntegerField(null=True, blank=True, help_text="Cost benefit score (1-5)")
    user_impact = models.IntegerField(null=True, blank=True, help_text="User impact and adoption score (1-5)")
    ease_of_implementation = models.IntegerField(null=True, blank=True, help_text="Ease of implementation score (1-5)")
    vendor_reputation_support = models.IntegerField(null=True, blank=True, help_text="Vendor reputation and support score (1-5)")
    security_compliance = models.IntegerField(null=True, blank=True, help_text="Security and compliance score (1-5)")
    student_centered = models.IntegerField(null=True, blank=True, help_text="Student-centered score (1-5)")

    def __str__(self):
        return self.title

    @property
    def formatted_id(self):
        return f"PRJ-{self.id:03d}"

    @property
    def average_score(self):
        """Calculate the average of individual criteria scores from all ProjectScore instances."""
        scores = self.scores.all()
        if not scores:
            return None
        
        # Calculate the average of individual criteria scores
        total_score = 0
        count = 0
        
        for score in scores:
            if score.calculate_final_score() is not None:
                total_score += score.calculate_final_score()
                count += 1
        
        if count == 0:
            return None
            
        return total_score / count

    @property
    def average_final_score(self):
        """Calculate the average of weighted final scores from all users."""
        scores = self.scores.all()
        if not scores:
            return None
        
        # Calculate the average of weighted final scores
        total_score = 0
        count = 0
        
        for score in scores:
            if score.final_score is not None:
                total_score += score.final_score
                count += 1
        
        if count == 0:
            return None
            
        return total_score / count

    def update_final_score(self):
        """Update the project's final score based on the average of individual scores"""
        avg_score = self.average_final_score
        if avg_score is not None:
            # Store the raw final score value
            self.final_score = avg_score
            self.save(update_fields=['final_score'])

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

class ProjectScore(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='scores')
    scored_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    strategic_alignment = models.IntegerField(null=True, blank=True, help_text="Strategic alignment score (1-5)")
    cost_benefit = models.IntegerField(null=True, blank=True, help_text="Cost benefit score (1-5)")
    user_impact = models.IntegerField(null=True, blank=True, help_text="User impact and adoption score (1-5)")
    ease_of_implementation = models.IntegerField(null=True, blank=True, help_text="Ease of implementation score (1-5)")
    vendor_reputation_support = models.IntegerField(null=True, blank=True, help_text="Vendor reputation and support score (1-5)")
    security_compliance = models.IntegerField(null=True, blank=True, help_text="Security and compliance score (1-5)")
    student_centered = models.IntegerField(null=True, blank=True, help_text="Student-centered score (1-5)")
    scoring_notes = models.TextField(blank=True, null=True)
    final_score = models.FloatField(null=True, blank=True, help_text="Calculated final score for this user")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['project', 'scored_by']
        ordering = ['-created_at']

    def __str__(self):
        return f"Score for {self.project.title} by {self.scored_by.username}"

    def calculate_final_score(self):
        """Calculate the weighted final score based on individual criteria scores"""
        try:
            if not all([
                self.strategic_alignment,
                self.cost_benefit,
                self.user_impact,
                self.ease_of_implementation,
                self.vendor_reputation_support,
                self.security_compliance,
                self.student_centered
            ]):
                return None

            # Convert all values to float to ensure proper calculation
            strategic_alignment = float(self.strategic_alignment)
            cost_benefit = float(self.cost_benefit)
            user_impact = float(self.user_impact)
            ease_of_implementation = float(self.ease_of_implementation)
            vendor_reputation_support = float(self.vendor_reputation_support)
            security_compliance = float(self.security_compliance)
            student_centered = float(self.student_centered)

            # Calculate weighted score
            return (
                strategic_alignment * 0.2 +
                cost_benefit * 0.15 +
                user_impact * 0.2 +
                ease_of_implementation * 0.15 +
                vendor_reputation_support * 0.10 +
                security_compliance * 0.10 +
                student_centered * 0.10
            )
        except (ValueError, TypeError, AttributeError):
            return None
    
    def save(self, *args, **kwargs):
        # Calculate and save the final score before saving
        self.final_score = self.calculate_final_score()
        super().save(*args, **kwargs)

class TriageNote(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='triage_note_history')
    notes = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Triage note for {self.project.title} by {self.created_by.username} on {self.created_at}"
