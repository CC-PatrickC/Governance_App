import logging
from typing import Dict

import requests
from django.conf import settings
from django.contrib.auth.models import Group
from django.dispatch import receiver

from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount, SocialToken

logger = logging.getLogger('projects')


def _get_group_mapping() -> Dict[str, str]:
    """Retrieve the Azure AD group to Django group mapping from settings."""
    return getattr(settings, 'AZURE_AD_GROUP_MAPPING', {}) or {}


def _fetch_azure_groups(access_token: str):
    """Fetch Azure AD groups for the current user via Microsoft Graph."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    try:
        response = requests.get(
            'https://graph.microsoft.com/v1.0/me/memberOf?$select=id,displayName',
            headers=headers,
            timeout=10,
        )
        if response.status_code != 200:
            logger.warning(
                "Azure group fetch failed with status %s: %s",
                response.status_code,
                response.text,
            )
            return []
        return response.json().get('value', [])
    except requests.RequestException as exc:
        logger.exception("Azure group fetch encountered an error: %s", exc)
        return []


@receiver(user_logged_in)
def sync_azure_groups_on_login(sender, request, user, **kwargs):
    """Sync Azure AD groups to Django groups whenever a user logs in via Microsoft."""
    if not getattr(settings, 'ENABLE_AZURE_AD', False):
        return

    try:
        social_account: SocialAccount | None = user.socialaccount_set.filter(provider='microsoft').first()
        if not social_account:
            return

        social_token: SocialToken | None = SocialToken.objects.filter(account=social_account).first()
        if not social_token or not social_token.token:
            logger.warning("No social token available for Azure AD synchronization.")
            return

        azure_groups = _fetch_azure_groups(social_token.token)
        if not azure_groups:
            return

        group_mapping = _get_group_mapping()
        if not group_mapping:
            logger.info("Azure AD group mapping is empty; skipping group synchronization.")
            return

        mapped_group_names = set(group_mapping.values())

        # Remove user from mapped groups before re-adding based on current membership
        if mapped_group_names:
            user.groups.remove(*Group.objects.filter(name__in=mapped_group_names))

        for azure_group in azure_groups:
            mapped_name = group_mapping.get(azure_group.get('id'))
            if not mapped_name:
                continue
            group_obj, _created = Group.objects.get_or_create(name=mapped_name)
            user.groups.add(group_obj)

        logger.info("Synchronized Azure AD groups for user %s", user.username)
    except Exception:
        logger.exception("Unexpected error while synchronizing Azure AD groups for user %s", user.username)

