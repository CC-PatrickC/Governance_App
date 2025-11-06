from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'List all users in the IT Governance Scoring group'

    def handle(self, *args, **options):
        group_name = 'IT Governance Scoring'
        
        try:
            group = Group.objects.get(name=group_name)
            users = group.user_set.all()
            
            if users:
                self.stdout.write(f'Users in group "{group_name}":')
                for user in users:
                    self.stdout.write(f'  - {user.username} ({user.get_full_name() or "No name"})')
            else:
                self.stdout.write(f'No users found in group "{group_name}"')
                
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Group "{group_name}" does not exist')
            ) 