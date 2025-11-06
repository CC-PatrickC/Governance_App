from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Create Process Improvement and Process Improvement Lead groups'

    def handle(self, *args, **options):
        # Create Process Improvement Group
        process_improvement_group, created = Group.objects.get_or_create(name='Process Improvement Group')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created "Process Improvement Group"')
            )
        else:
            self.stdout.write(
                self.style.WARNING('"Process Improvement Group" already exists')
            )

        # Create Process Improvement Group Lead
        process_improvement_lead_group, created = Group.objects.get_or_create(name='Process Improvement Group Lead')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created "Process Improvement Group Lead"')
            )
        else:
            self.stdout.write(
                self.style.WARNING('"Process Improvement Group Lead" already exists')
            )

        self.stdout.write(
            self.style.SUCCESS('Process Improvement groups setup completed!')
        )
