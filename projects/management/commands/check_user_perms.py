from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check user permissions'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to check')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"\n=== User Information for: {user.username} ===")
            self.stdout.write(f"First Name: {user.first_name}")
            self.stdout.write(f"Last Name: {user.last_name}")
            self.stdout.write(f"Email: {user.email}")
            self.stdout.write(f"Is Staff: {user.is_staff}")
            self.stdout.write(f"Is Superuser: {user.is_superuser}")
            self.stdout.write(f"Is Active: {user.is_active}")
            self.stdout.write(f"\nGroups:")
            groups = user.groups.all()
            if groups:
                for group in groups:
                    self.stdout.write(f"  - {group.name}")
            else:
                self.stdout.write(f"  (No groups)")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))


