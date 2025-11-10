from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q
from projects.models import Project

class Command(BaseCommand):
    help = 'Check technician data for debugging'

    def handle(self, *args, **options):
        # Check if rredington user exists
        user = User.objects.filter(username='rredington').first()
        if user:
            self.stdout.write(f"User found: {user.username}")
            self.stdout.write(f"Full name: '{user.get_full_name()}'")
            self.stdout.write(f"First name: '{user.first_name}'")
            self.stdout.write(f"Last name: '{user.last_name}'")
        else:
            self.stdout.write("User 'rredington' not found")
        
        # Check projects with rredington in technician
        projects = Project.objects.filter(technician__icontains='rredington')
        self.stdout.write(f"\nProjects with 'rredington' in technician: {projects.count()}")
        for p in projects:
            self.stdout.write(f"  Project {p.id}: technician='{p.technician}'")
        
        # Check all unique technician values
        all_contacts = Project.objects.values_list('technician', flat=True).distinct()
        self.stdout.write(f"\nAll unique technician values:")
        for contact in sorted(all_contacts):
            if contact and 'rredington' in contact.lower():
                self.stdout.write(f"  '{contact}' (contains rredington)")
            elif contact:
                self.stdout.write(f"  '{contact}'")
        
        # Test the exact query used in my_governance view
        if user:
            user_full_name = user.get_full_name()
            user_username = user.username
            
            technician_projects = Project.objects.filter(
                Q(technician=user_full_name) | 
                Q(technician=user_username)
            ).exclude(submitted_by=user)
            
            self.stdout.write(f"\nTechnician projects for {user.username}: {technician_projects.count()}")
            for p in technician_projects:
                self.stdout.write(f"  Project {p.id}: technician='{p.technician}'")
