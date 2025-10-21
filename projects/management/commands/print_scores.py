from django.core.management.base import BaseCommand
from projects.models import Project, ProjectScore

class Command(BaseCommand):
    help = 'Prints out the current score values in the database'

    def handle(self, *args, **options):
        projects = Project.objects.all()
        
        for project in projects:
            self.stdout.write(f"\nProject: {project.title} (ID: {project.id})")
            self.stdout.write(f"Final Score: {project.final_score}")
            self.stdout.write(f"Average Final Score: {project.average_final_score}")
            
            scores = project.scores.all()
            self.stdout.write(f"Number of scores: {scores.count()}")
            
            for score in scores:
                self.stdout.write(f"  Score by {score.scored_by.username}:")
                self.stdout.write(f"    Strategic Alignment: {score.strategic_alignment}")
                self.stdout.write(f"    Cost Benefit: {score.cost_benefit}")
                self.stdout.write(f"    User Impact: {score.user_impact}")
                self.stdout.write(f"    Ease of Implementation: {score.ease_of_implementation}")
                self.stdout.write(f"    Vendor Reputation: {score.vendor_reputation_support}")
                self.stdout.write(f"    Security Compliance: {score.security_compliance}")
                self.stdout.write(f"    Student Centered: {score.student_centered}")
                self.stdout.write(f"    Final Score: {score.final_score}")
                self.stdout.write(f"    Calculated Final Score: {score.calculate_final_score()}") 