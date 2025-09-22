from django.core.management.base import BaseCommand
from projects.models import Project

class Command(BaseCommand):
    help = 'Check what stages are being used in projects'

    def handle(self, *args, **options):
        self.stdout.write("Checking project stages...")
        
        # Get all unique stages
        stages = Project.objects.values_list('stage', flat=True).distinct()
        
        self.stdout.write(f"Found {len(stages)} unique stages:")
        for stage in stages:
            count = Project.objects.filter(stage=stage).count()
            self.stdout.write(f"  - {stage}: {count} projects")
        
        # Check triage stages specifically
        triage_stages = ['Pending_Review', 'Under_Review_Triage']
        self.stdout.write(f"\nChecking triage stages: {triage_stages}")
        
        for stage in triage_stages:
            count = Project.objects.filter(stage=stage).count()
            self.stdout.write(f"  - {stage}: {count} projects")
        
        # Show first few projects with their stages
        self.stdout.write(f"\nFirst 10 projects with their stages:")
        projects = Project.objects.all()[:10]
        for project in projects:
            self.stdout.write(f"  - Project {project.id}: {project.title} - Stage: {project.stage}")









