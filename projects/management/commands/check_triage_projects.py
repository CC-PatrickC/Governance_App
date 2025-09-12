from django.core.management.base import BaseCommand
from projects.models import Project

class Command(BaseCommand):
    help = 'Check for projects with Under Review - Triage stage'

    def handle(self, *args, **options):
        # Find all projects with Under_Review_Triage stage
        triage_projects = Project.objects.filter(stage='Under_Review_Triage')
        
        self.stdout.write(f'Found {triage_projects.count()} projects with Under_Review_Triage stage:')
        
        for project in triage_projects:
            self.stdout.write(f'  - Project #{project.id}: {project.title} (Stage: {project.stage})')
        
        # Check excluding project #60
        triage_projects_excluding_60 = triage_projects.exclude(id=60)
        
        self.stdout.write(f'\nExcluding project #60: {triage_projects_excluding_60.count()} projects would be updated:')
        
        for project in triage_projects_excluding_60:
            self.stdout.write(f'  - Project #{project.id}: {project.title} (Stage: {project.stage})')
