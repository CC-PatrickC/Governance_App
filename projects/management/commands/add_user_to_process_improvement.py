from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Add a user to the Process Improvement Group'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to add to Process Improvement Group')

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
            group = Group.objects.get(name='Process Improvement Group')
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Process Improvement Group does not exist. Please run create_process_improvement_groups first.')
            )
            return

        if user.groups.filter(name='Process Improvement Group').exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" is already in the Process Improvement Group')
            )
        else:
            user.groups.add(group)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully added user "{username}" to Process Improvement Group')
            )
