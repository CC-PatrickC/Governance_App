from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q
from projects.models import Project

class Command(BaseCommand):
    help = 'Check contact person data for debugging'

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
        
        # Check projects with rredington in contact_person
        projects = Project.objects.filter(contact_person__icontains='rredington')
        self.stdout.write(f"\nProjects with 'rredington' in contact_person: {projects.count()}")
        for p in projects:
            self.stdout.write(f"  Project {p.id}: contact_person='{p.contact_person}'")
        
        # Check all unique contact_person values
        all_contacts = Project.objects.values_list('contact_person', flat=True).distinct()
        self.stdout.write(f"\nAll unique contact_person values:")
        for contact in sorted(all_contacts):
            if contact and 'rredington' in contact.lower():
                self.stdout.write(f"  '{contact}' (contains rredington)")
            elif contact:
                self.stdout.write(f"  '{contact}'")
        
        # Test the exact query used in my_governance view
        if user:
            user_full_name = user.get_full_name()
            user_username = user.username
            
            contact_projects = Project.objects.filter(
                Q(contact_person=user_full_name) | 
                Q(contact_person=user_username)
            ).exclude(submitted_by=user)
            
            self.stdout.write(f"\nContact projects for {user.username}: {contact_projects.count()}")
            for p in contact_projects:
                self.stdout.write(f"  Project {p.id}: contact_person='{p.contact_person}'")
