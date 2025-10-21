from django.core.management.base import BaseCommand
from projects.models import ProjectScore

class Command(BaseCommand):
    help = 'Updates all final scores in the database to use the new calculation method'

    def handle(self, *args, **options):
        scores = ProjectScore.objects.all()
        updated_count = 0
        
        for score in scores:
            # Save the score to trigger the new calculation method
            score.save()
            updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} final scores')
        ) 