"""
AgriConnect Users Serializers
Comprehensive user profile management serializers
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ExtendedUserProfile,
    FarmerProfile,
    ConsumerProfile,
    InstitutionProfile,
    AgentProfile,
    FinancialPartnerProfile,
    GovernmentOfficialProfile
)
from authentication.models import UserRole

User = get_user_model()


class ExtendedUserProfileSerializer(serializers.ModelSerializer):
    """Serializer for extended user profile"""
    
    class Meta:
        model = ExtendedUserProfile
        fields = [
            'bio', 'date_of_birth', 'gender', 'address_line_1',
            'city', 'postal_code', 'newsletter_subscription'
        ]


class FarmerProfileSerializer(serializers.ModelSerializer):
    """Serializer for farmer profile"""
    
    class Meta:
        model = FarmerProfile
        fields = [
            'farm_size', 'organic_certified', 'years_of_experience',
            'production_capacity', 'farm_name', 'farm_type', 'primary_crops'
        ]


class ConsumerProfileSerializer(serializers.ModelSerializer):
    """Serializer for consumer profile"""
    
    class Meta:
        model = ConsumerProfile
        fields = [
            'delivery_address', 'budget_range', 'dietary_restrictions',
            'preferred_categories'
        ]


class InstitutionProfileSerializer(serializers.ModelSerializer):
    """Serializer for institution profile"""
    
    class Meta:
        model = InstitutionProfile
        fields = [
            'organization_name', 'organization_type', 'tax_id',
            'business_license', 'annual_volume'
        ]


class AgentProfileSerializer(serializers.ModelSerializer):
    """Serializer for agent profile"""
    
    class Meta:
        model = AgentProfile
        fields = [
            'employee_id', 'agent_type', 'assigned_regions', 'target_farmers',
            'farmers_registered', 'commission_rate', 'performance_rating',
            'hire_date', 'is_active'
        ]
        read_only_fields = ['employee_id']


class FinancialPartnerProfileSerializer(serializers.ModelSerializer):
    """Serializer for financial partner profile"""
    
    class Meta:
        model = FinancialPartnerProfile
        fields = [
            'institution_name', 'institution_type', 'registration_number',
            'services_offered', 'supported_currencies', 'minimum_transaction',
            'maximum_transaction', 'transaction_fee_percentage', 'integration_status',
            'is_verified', 'partnership_start_date'
        ]


class GovernmentOfficialProfileSerializer(serializers.ModelSerializer):
    """Serializer for government official profile"""
    
    class Meta:
        model = GovernmentOfficialProfile
        fields = [
            'employee_id', 'official_title', 'department', 'ministry',
            'position_level', 'jurisdiction_level', 'assigned_regions',
            'can_approve_certifications', 'can_issue_permits', 'can_conduct_inspections',
            'employment_status', 'appointment_date'
        ]
        read_only_fields = ['employee_id']


class ComprehensiveUserProfileSerializer(serializers.ModelSerializer):
    """Comprehensive user profile serializer including all profile types"""
    
    # Extended profile
    extended_profile = ExtendedUserProfileSerializer(required=False)
    
    # Role-specific profiles
    farmer_profile = FarmerProfileSerializer(required=False)
    consumer_profile = ConsumerProfileSerializer(required=False)
    institution_profile = InstitutionProfileSerializer(required=False)
    agent_profile = AgentProfileSerializer(required=False)
    financial_partner_profile = FinancialPartnerProfileSerializer(required=False)
    government_official_profile = GovernmentOfficialProfileSerializer(required=False)
    
    # User roles and metadata
    roles_display = serializers.SerializerMethodField(read_only=True)
    user_type = serializers.SerializerMethodField(read_only=True)
    profile_completion = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'phone_number',
            'country', 'region', 'language', 'is_active', 'is_verified',
            'phone_verified', 'email_verified', 'date_joined', 'last_login',
            'roles_display', 'user_type', 'profile_completion',
            'extended_profile', 'farmer_profile', 'consumer_profile',
            'institution_profile', 'agent_profile', 'financial_partner_profile',
            'government_official_profile'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']

    def get_roles_display(self, obj):
        """Get display names for all user roles"""
        return [role.get_name_display() for role in obj.roles.all()]

    def get_user_type(self, obj):
        """Get primary user role"""
        first_role = obj.roles.first()
        return first_role.name if first_role else 'USER'

    def get_profile_completion(self, obj):
        """Calculate profile completion percentage"""
        total_fields = 0
        completed_fields = 0
        
        # Basic user fields (required)
        basic_fields = ['first_name', 'last_name']
        for field in basic_fields:
            total_fields += 1
            if getattr(obj, field):
                completed_fields += 1
        
        # Contact verification
        total_fields += 2  # email and phone verification
        if getattr(obj, 'email_verified', False):
            completed_fields += 1
        if getattr(obj, 'phone_verified', False):
            completed_fields += 1
        
        # Extended profile
        if hasattr(obj, 'extended_profile'):
            profile = obj.extended_profile
            extended_fields = ['bio', 'city', 'address_line_1']
            for field in extended_fields:
                total_fields += 1
                if getattr(profile, field):
                    completed_fields += 1
        
        # Role-specific profile
        user_roles = [role.name for role in obj.roles.all()]
        
        if 'FARMER' in user_roles and hasattr(obj, 'farmer_profile'):
            profile = obj.farmer_profile
            farmer_fields = ['farm_name', 'farm_size', 'farm_type']
            for field in farmer_fields:
                total_fields += 1
                if getattr(profile, field):
                    completed_fields += 1
                    
        elif 'CONSUMER' in user_roles and hasattr(obj, 'consumer_profile'):
            profile = obj.consumer_profile
            consumer_fields = ['delivery_address', 'budget_range']
            for field in consumer_fields:
                total_fields += 1
                if getattr(profile, field):
                    completed_fields += 1
        
        return round((completed_fields / total_fields) * 100) if total_fields > 0 else 0

    def update(self, instance, validated_data):
        """Update user and all related profiles"""
        
        # Extract profile data
        extended_data = validated_data.pop('extended_profile', {})
        farmer_data = validated_data.pop('farmer_profile', {})
        consumer_data = validated_data.pop('consumer_profile', {})
        institution_data = validated_data.pop('institution_profile', {})
        agent_data = validated_data.pop('agent_profile', {})
        financial_data = validated_data.pop('financial_partner_profile', {})
        government_data = validated_data.pop('government_official_profile', {})
        
        # Update basic user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update extended profile
        if extended_data:
            extended_profile, created = ExtendedUserProfile.objects.get_or_create(user=instance)
            for attr, value in extended_data.items():
                setattr(extended_profile, attr, value)
            extended_profile.save()
        
        # Update role-specific profiles
        user_roles = [role.name for role in instance.roles.all()]
        
        if 'FARMER' in user_roles and farmer_data:
            farmer_profile, created = FarmerProfile.objects.get_or_create(user=instance)
            for attr, value in farmer_data.items():
                setattr(farmer_profile, attr, value)
            farmer_profile.save()
        
        if 'CONSUMER' in user_roles and consumer_data:
            consumer_profile, created = ConsumerProfile.objects.get_or_create(user=instance)
            for attr, value in consumer_data.items():
                setattr(consumer_profile, attr, value)
            consumer_profile.save()
        
        if 'INSTITUTION' in user_roles and institution_data:
            institution_profile, created = InstitutionProfile.objects.get_or_create(user=instance)
            for attr, value in institution_data.items():
                setattr(institution_profile, attr, value)
            institution_profile.save()
        
        if 'AGENT' in user_roles and agent_data:
            agent_profile, created = AgentProfile.objects.get_or_create(user=instance)
            for attr, value in agent_data.items():
                setattr(agent_profile, attr, value)
            agent_profile.save()
        
        if 'FINANCIAL_PARTNER' in user_roles and financial_data:
            financial_profile, created = FinancialPartnerProfile.objects.get_or_create(user=instance)
            for attr, value in financial_data.items():
                setattr(financial_profile, attr, value)
            financial_profile.save()
        
        if 'GOVERNMENT_OFFICIAL' in user_roles and government_data:
            government_profile, created = GovernmentOfficialProfile.objects.get_or_create(user=instance)
            for attr, value in government_data.items():
                setattr(government_profile, attr, value)
            government_profile.save()
        
        return instance


class UserActivationSerializer(serializers.Serializer):
    """Serializer for user account activation"""
    
    def update(self, instance, validated_data):
        """Activate user account and verify contact information"""
        instance.is_active = True
        instance.is_verified = True
        
        # Verify contact based on available information
        if instance.email:
            instance.email_verified = True
        if instance.phone_number:
            instance.phone_verified = True
        
        instance.save()
        
        # Ensure extended profile exists
        ExtendedUserProfile.objects.get_or_create(user=instance)
        
        return instance


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Simplified serializer for basic profile updates"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'country', 'region', 'language'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if value and User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number uniqueness"""
        if value and User.objects.filter(phone_number=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value
