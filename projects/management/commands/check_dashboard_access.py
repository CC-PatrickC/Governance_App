from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'Check user groups and permissions for dashboard access'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Check specific user by username')

    def handle(self, *args, **options):
        username = options.get('username')
        
        if username:
            try:
                user = User.objects.get(username=username)
                self.check_user_permissions(user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
        else:
            # Show all superusers and staff
            superusers = User.objects.filter(is_superuser=True)
            staff_users = User.objects.filter(is_staff=True)
            cabinet_users = User.objects.filter(groups__name='Cabinet Group')
            
            self.stdout.write(self.style.SUCCESS('=== DASHBOARD ACCESS ANALYSIS ==='))
            
            self.stdout.write('\n--- Superusers ---')
            for user in superusers:
                self.check_user_permissions(user)
            
            self.stdout.write('\n--- Staff Users ---')
            for user in staff_users:
                if not user.is_superuser:  # Don't duplicate
                    self.check_user_permissions(user)
            
            self.stdout.write('\n--- Cabinet Group Members ---')
            for user in cabinet_users:
                if not (user.is_superuser or user.is_staff):  # Don't duplicate
                    self.check_user_permissions(user)

    def check_user_permissions(self, user):
        from projects.views import is_cabinet_user
        
        groups = [group.name for group in user.groups.all()]
        has_dashboard_access = is_cabinet_user(user)
        
        self.stdout.write(f"User: {user.username}")
        self.stdout.write(f"  - Is superuser: {user.is_superuser}")
        self.stdout.write(f"  - Is staff: {user.is_staff}")
        self.stdout.write(f"  - Groups: {groups}")
        
        if has_dashboard_access:
            self.stdout.write(self.style.SUCCESS(f"  - Dashboard access: YES"))
        else:
            self.stdout.write(self.style.ERROR(f"  - Dashboard access: NO"))
        self.stdout.write("")