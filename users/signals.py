"""
AgriConnect Users Signals
Automatic profile creation based on user roles
"""

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from authentication.models import UserRole
from .models import (
    ExtendedUserProfile,
    FarmerProfile,
    ConsumerProfile,
    InstitutionProfile,
    AgentProfile,
    FinancialPartnerProfile,
    GovernmentOfficialProfile
)

User = get_user_model()


@receiver(post_save, sender=User)
def create_extended_user_profile(sender, instance, created, **kwargs):
    """Create an extended user profile for every new user"""
    if created:
        ExtendedUserProfile.objects.get_or_create(user=instance)


def create_role_specific_profile(sender, instance, action, pk_set, **kwargs):
    """Create role-specific profiles when users are assigned roles"""
    if action == 'post_add' and pk_set:
        for role_pk in pk_set:
            try:
                role = UserRole.objects.get(pk=role_pk)
                role_name = role.name
                
                # Create appropriate profile based on role
                if role_name == 'FARMER':
                    FarmerProfile.objects.get_or_create(user=instance)
                    
                elif role_name == 'CONSUMER':
                    ConsumerProfile.objects.get_or_create(user=instance)
                    
                elif role_name == 'INSTITUTION':
                    InstitutionProfile.objects.get_or_create(
                        user=instance,
                        defaults={'organization_name': f"{instance.get_full_name()}'s Organization"}
                    )
                    
                elif role_name == 'AGENT':
                    AgentProfile.objects.get_or_create(user=instance)
                    
                elif role_name == 'FINANCIAL_PARTNER':
                    FinancialPartnerProfile.objects.get_or_create(
                        user=instance,
                        defaults={'institution_name': f"{instance.get_full_name()}'s Financial Institution"}
                    )
                    
                elif role_name == 'GOVERNMENT_OFFICIAL':
                    GovernmentOfficialProfile.objects.get_or_create(
                        user=instance,
                        defaults={
                            'official_title': 'Agricultural Officer',
                            'department': 'Agricultural Development'
                        }
                    )
                    
            except UserRole.DoesNotExist:
                continue


# Connect the m2m_changed signal for User.roles
m2m_changed.connect(create_role_specific_profile, sender=User.roles.through)
