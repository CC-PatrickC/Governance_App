from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User

class Command(BaseCommand):
    help = 'Add a user to the Triage Group Lead group'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to add to the group')

    def handle(self, *args, **options):
        username = options['username']
        group_name = 'Triage Group Lead'
        
        try:
            # Get the user
            user = User.objects.get(username=username)
            
            # Get the group
            group, created = Group.objects.get_or_create(name=group_name)
            
            # Add user to group
            if user.groups.filter(name=group_name).exists():
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" is already in group "{group_name}"')
                )
            else:
                user.groups.add(group)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully added user "{username}" to group "{group_name}"')
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
