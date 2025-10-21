from django.contrib.auth.models import Group
from allauth.socialaccount.providers.microsoft.views import MicrosoftOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
import requests

def sync_azure_groups(backend, user, response, *args, **kwargs):
    """
    Pipeline to sync Azure AD groups with Django groups
    """
    if backend.name != 'microsoft':
        return

    # Get the access token from the social account
    social_account = user.socialaccount_set.get(provider='microsoft')
    access_token = social_account.socialtoken_set.get().token

    # Get user's groups from Microsoft Graph API
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get user's groups
    groups_response = requests.get(
        'https://graph.microsoft.com/v1.0/me/memberOf',
        headers=headers
    )
    
    if groups_response.status_code != 200:
        return

    azure_groups = groups_response.json().get('value', [])
    
    # Map of Azure AD group IDs to Django group names
    # You can customize this mapping based on your needs
    group_mapping = {
        'your-azure-group-id-1': 'Triage Group',
        'your-azure-group-id-2': 'Scoring Group',
        # Add more mappings as needed
    }

    # Get all existing Django groups
    django_groups = {group.name: group for group in Group.objects.all()}

    # Remove user from all groups first
    user.groups.clear()

    # Add user to corresponding Django groups
    for azure_group in azure_groups:
        if azure_group.get('id') in group_mapping:
            django_group_name = group_mapping[azure_group['id']]
            if django_group_name in django_groups:
                user.groups.add(django_groups[django_group_name])

    return {'user': user} 