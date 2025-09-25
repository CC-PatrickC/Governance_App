"""
Context processors for the projects app.
These add variables to all template contexts.
"""
from .views import is_cabinet_user, is_triage_user, is_triage_lead_user

def user_permissions(request):
    """Add user permission checks to template context."""
    if request.user.is_authenticated:
        return {
            'is_cabinet_user': is_cabinet_user(request.user),
            'is_triage_user': is_triage_user(request.user),
            'is_triage_lead_user': is_triage_lead_user(request.user),
        }
    return {
        'is_cabinet_user': False,
        'is_triage_user': False,
        'is_triage_lead_user': False,
    }