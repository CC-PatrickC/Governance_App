from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Create ERP Governance and ERP Governance Lead groups'

    def handle(self, *args, **options):
        # Create ERP Governance Group
        erp_governance_group, created = Group.objects.get_or_create(name='ERP Governance Group')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created "ERP Governance Group"')
            )
        else:
            self.stdout.write(
                self.style.WARNING('"ERP Governance Group" already exists')
            )

        # Create ERP Governance Group Lead
        erp_governance_lead_group, created = Group.objects.get_or_create(name='ERP Governance Group Lead')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created "ERP Governance Group Lead"')
            )
        else:
            self.stdout.write(
                self.style.WARNING('"ERP Governance Group Lead" already exists')
            )

        self.stdout.write(
            self.style.SUCCESS('ERP Governance groups setup completed!')
        )
