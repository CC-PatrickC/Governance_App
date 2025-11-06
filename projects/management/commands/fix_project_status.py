from django.core.management.base import BaseCommand
from projects.models import Project


class Command(BaseCommand):
    help = 'Fix project status values to match the new stage system'

    def handle(self, *args, **options):
        # Update old status values to new ones
        updates = {
            'under_review': 'under_review_scoring',  # Old value to new value
        }
        
        updated_count = 0
        
        for old_status, new_status in updates.items():
            projects = Project.objects.filter(status=old_status)
            count = projects.count()
            if count > 0:
                projects.update(status=new_status)
                updated_count += count
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated {count} projects from status "{old_status}" to "{new_status}"'
                    )
                )
        
        if updated_count == 0:
            self.stdout.write(
                self.style.WARNING('No projects found with old status values to update')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated_count} projects total')
            ) 