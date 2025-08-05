#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_intake.settings')
django.setup()

from django.contrib.auth.models import User, Group
from projects.models import Project
from projects.views import is_it_governance_scoring_user

def test_group_filtering():
    print("Testing Group-Based Filtering for IT Governance Scoring")
    print("=" * 60)
    
    # Check if the group exists
    try:
        it_governance_group = Group.objects.get(name='IT Governance Scoring')
        print(f"✓ IT Governance Scoring group exists")
    except Group.DoesNotExist:
        print("✗ IT Governance Scoring group does not exist")
        return
    
    # Get all projects
    all_projects = Project.objects.all()
    it_governance_projects = Project.objects.filter(project_type='it_governance')
    
    print(f"\nProject Statistics:")
    print(f"  Total projects: {all_projects.count()}")
    print(f"  IT Governance projects: {it_governance_projects.count()}")
    
    # Test with different user types
    print(f"\nTesting User Access:")
    
    # Test with staff user
    staff_user = User.objects.filter(is_staff=True).first()
    if staff_user:
        print(f"  Staff user '{staff_user.username}':")
        print(f"    - Is IT Governance Scoring user: {is_it_governance_scoring_user(staff_user)}")
        print(f"    - Should see all projects: {staff_user.is_staff}")
    
    # Test with regular scoring user
    scoring_user = User.objects.filter(groups__name='Scoring Group').first()
    if scoring_user:
        print(f"  Regular scoring user '{scoring_user.username}':")
        print(f"    - Is IT Governance Scoring user: {is_it_governance_scoring_user(scoring_user)}")
        print(f"    - Should see all projects: {not is_it_governance_scoring_user(scoring_user) or scoring_user.is_staff}")
    
    # Test with IT Governance Scoring user
    it_governance_user = User.objects.filter(groups__name='IT Governance Scoring').first()
    if it_governance_user:
        print(f"  IT Governance Scoring user '{it_governance_user.username}':")
        print(f"    - Is IT Governance Scoring user: {is_it_governance_scoring_user(it_governance_user)}")
        print(f"    - Should see only IT Governance projects: {is_it_governance_scoring_user(it_governance_user) and not it_governance_user.is_staff}")
    else:
        print(f"  No IT Governance Scoring users found")
        print(f"    - Use: python manage.py add_user_to_it_governance <username>")
    
    print(f"\nTo add a user to IT Governance Scoring group:")
    print(f"  python manage.py add_user_to_it_governance <username>")
    print(f"\nTo list users in IT Governance Scoring group:")
    print(f"  python manage.py list_it_governance_users")

if __name__ == '__main__':
    test_group_filtering() 