from django.core.management.base import BaseCommand
from projects.models import Project

class Command(BaseCommand):
    help = 'Update all Under Review - Triage requests to Governance Closed (excluding project #60)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find all projects with Under_Review_Triage stage, excluding project #60
        projects_to_update = Project.objects.filter(
            stage='Under_Review_Triage'
        ).exclude(
            id=60
        )
        
        count = projects_to_update.count()
        
        if count == 0:
            self.stdout.write(
                self.style.WARNING('No projects found with Under Review - Triage stage (excluding #60)')
            )
            return
        
        self.stdout.write(f'Found {count} projects to update:')
        
        # Show which projects will be updated
        for project in projects_to_update:
            self.stdout.write(f'  - Project #{project.id}: {project.title}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\nDRY RUN: Would update {count} projects to Governance Closed stage')
            )
            return
        
        # Confirm the update
        confirm = input(f'\nAre you sure you want to update {count} projects to "Governance Closed"? (yes/no): ')
        
        if confirm.lower() != 'yes':
            self.stdout.write(
                self.style.WARNING('Update cancelled by user')
            )
            return
        
        # Perform the update
        updated_count = projects_to_update.update(stage='Governance_Closure')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} projects to Governance Closed stage')
        )
        
        # Show the updated projects
        self.stdout.write('\nUpdated projects:')
        for project in Project.objects.filter(id__in=projects_to_update.values_list('id', flat=True)):
            self.stdout.write(f'  - Project #{project.id}: {project.title} (Stage: {project.get_stage_display()})')
