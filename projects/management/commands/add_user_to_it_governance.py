from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Add a user to the IT Governance Group'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to add to IT Governance Group')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
            return

        try:
            group = Group.objects.get(name='IT Governance Group')
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('IT Governance Group does not exist. Please run create_it_governance_groups first.')
            )
            return

        if user.groups.filter(name='IT Governance Group').exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" is already in the IT Governance Group')
            )
        else:
            user.groups.add(group)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully added user "{username}" to IT Governance Group')
            )