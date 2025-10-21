from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Create IT Governance and IT Governance Lead groups'

    def handle(self, *args, **options):
        # Create IT Governance Group
        it_governance_group, created = Group.objects.get_or_create(name='IT Governance Group')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created "IT Governance Group"')
            )
        else:
            self.stdout.write(
                self.style.WARNING('"IT Governance Group" already exists')
            )

        # Create IT Governance Group Lead
        it_governance_lead_group, created = Group.objects.get_or_create(name='IT Governance Group Lead')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created "IT Governance Group Lead"')
            )
        else:
            self.stdout.write(
                self.style.WARNING('"IT Governance Group Lead" already exists')
            )

        self.stdout.write(
            self.style.SUCCESS('IT Governance groups setup completed!')
        )
