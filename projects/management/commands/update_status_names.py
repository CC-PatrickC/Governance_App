from django.core.management.base import BaseCommand
from projects.models import Project

class Command(BaseCommand):
    help = 'Update old status values to new naming convention'

    def handle(self, *args, **options):
        # Update under_review_scoring to under_review_governance
        updated_scoring = Project.objects.filter(status='under_review_scoring').update(status='under_review_governance')
        
        # Update under_review_final_scoring to under_review_final_governance
        updated_final = Project.objects.filter(status='under_review_final_scoring').update(status='under_review_final_governance')
        
        total_updated = updated_scoring + updated_final
        
        if total_updated > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {total_updated} project(s) status values:\n'
                    f'  - {updated_scoring} project(s): under_review_scoring -> under_review_governance\n'
                    f'  - {updated_final} project(s): under_review_final_scoring -> under_review_final_governance'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No projects needed status updates - all statuses are correct!')
            )

