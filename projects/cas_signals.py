from django.dispatch import receiver
from django_cas_ng.signals import cas_user_authenticated
import logging

# Set up logging
logger = logging.getLogger(__name__)

@receiver(cas_user_authenticated)
def cas_user_login(sender, **kwargs):
    """
    Signal handler to debug CAS login and update user attributes
    """
    user = kwargs.get('user')
    attributes = kwargs.get('attributes', {})
    
    logger.info(f"=== CAS LOGIN DEBUG ===")
    logger.info(f"Username: {user.username}")
    logger.info(f"CAS Attributes received: {attributes}")
    
    # Try to update user fields with CAS attributes
    updated = False
    
    # Map email
    if 'mail' in attributes:
        user.email = attributes['mail']
        logger.info(f"Updated email: {user.email}")
        updated = True
    
    # Map first name
    if 'givenName' in attributes:
        user.first_name = attributes['givenName']
        logger.info(f"Updated first_name: {user.first_name}")
        updated = True
    
    # Map last name  
    if 'sn' in attributes:
        user.last_name = attributes['sn']
        logger.info(f"Updated last_name: {user.last_name}")
        updated = True
    
    if updated:
        user.save()
        logger.info(f"User {user.username} saved with updated attributes")
    else:
        logger.warning(f"No attributes found to update for user {user.username}")
    
    logger.info(f"=== END CAS DEBUG ===")