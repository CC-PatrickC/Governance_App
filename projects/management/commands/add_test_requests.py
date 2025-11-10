from django.core.management.base import BaseCommand
from django.utils import timezone
from projects.models import Project
from datetime import timedelta
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Add 50 test requests with random dates spanning the last 2 years'

    def handle(self, *args, **options):
        # Sample data for generating realistic test requests
        departments = [
            'Information Technology',
            'Public Works',
            'Finance',
            'Human Resources',
            'Planning and Development',
            'Parks and Recreation',
            'Public Safety',
            'Administration',
            'Legal',
            'Community Development'
        ]

        project_titles = [
            'Network Infrastructure Upgrade',
            'Software License Renewal',
            'Security System Installation',
            'Database Migration',
            'Cloud Service Implementation',
            'Mobile App Development',
            'Website Redesign',
            'Data Backup System',
            'Email System Upgrade',
            'Video Conferencing Setup',
            'Document Management System',
            'GIS Mapping Project',
            'Financial Reporting Tool',
            'HR Management System',
            'Facility Maintenance Tracking',
            'Emergency Response System',
            'Citizen Portal Development',
            'Asset Management System',
            'Compliance Monitoring Tool',
            'Performance Analytics Platform'
        ]

        descriptions = [
            'Upgrade existing infrastructure to improve performance and reliability.',
            'Renew software licenses for critical business applications.',
            'Install new security systems to enhance facility protection.',
            'Migrate legacy database to modern platform.',
            'Implement cloud-based services for improved scalability.',
            'Develop mobile application for citizen engagement.',
            'Redesign website to improve user experience and accessibility.',
            'Implement automated data backup and recovery system.',
            'Upgrade email system to latest version with enhanced features.',
            'Set up video conferencing capabilities for remote work.',
            'Deploy document management system for better organization.',
            'Create GIS mapping solution for planning and development.',
            'Develop financial reporting tool for budget management.',
            'Implement HR management system for employee tracking.',
            'Create facility maintenance tracking system.',
            'Deploy emergency response system for public safety.',
            'Develop citizen portal for online services.',
            'Implement asset management system for inventory tracking.',
            'Create compliance monitoring tool for regulatory requirements.',
            'Deploy performance analytics platform for data insights.'
        ]

        priorities = ['Low', 'Normal', 'High', 'Top']
        statuses = ['pending', 'approved', 'rejected', 'under_review_triage', 'under_review_governance', 'under_review_final_governance', 'completed', 'archived', 'on_hold', 'cancelled']

        # Calculate date range (2 years back from today)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=730)  # 2 years

        self.stdout.write(f'Creating 50 test requests with dates between {start_date} and {end_date}...')

        created_count = 0
        for i in range(50):
            # Generate random date within the 2-year range
            days_back = random.randint(0, 730)
            random_date = end_date - timedelta(days=days_back)
            
            # Ensure the date is a weekday (Monday-Friday)
            while random_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                days_back = random.randint(0, 730)
                random_date = end_date - timedelta(days=days_back)

            # Create project with random data
            project = Project.objects.create(
                title=random.choice(project_titles),
                description=random.choice(descriptions),
                department=random.choice(departments),
                priority=random.choice(priorities),
                status=random.choice(statuses),
                submission_date=random_date,
                technician=f'Test Technician {i+1}',
                contact_email=f'test.contact{i+1}@ccgov.org',
                contact_phone=f'555-{str(random.randint(100, 999))}-{str(random.randint(1000, 9999))}',
                budget=Decimal(str(random.randint(1000, 500000))),
                start_date=random_date + timedelta(days=random.randint(1, 30)),
                end_date=random_date + timedelta(days=random.randint(30, 365)),
                triage_notes=f'Test project {i+1} created for dashboard testing purposes.'
            )
            
            created_count += 1
            if created_count % 10 == 0:
                self.stdout.write(f'Created {created_count} test requests...')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} test requests with random dates spanning the last 2 years!'
            )
        )
        
        # Show some statistics
        total_projects = Project.objects.count()
        self.stdout.write(f'Total projects in database: {total_projects}')
        
        # Show date range of created projects
        oldest_project = Project.objects.order_by('submission_date').first()
        newest_project = Project.objects.order_by('submission_date').last()
        
        if oldest_project and newest_project:
            self.stdout.write(f'Date range: {oldest_project.submission_date} to {newest_project.submission_date}')
        
        # Show status distribution
        status_counts = {}
        for project in Project.objects.all():
            status = project.get_status_display()
            status_counts[status] = status_counts.get(status, 0) + 1
        
        self.stdout.write('Status distribution:')
        for status, count in status_counts.items():
            self.stdout.write(f'  {status}: {count}')
