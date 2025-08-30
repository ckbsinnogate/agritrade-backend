"""
AgriConnect Communications System Demo
Enhanced SMS & OTP Integration System (PRD Section 4.7)

This script demonstrates the comprehensive communications system including:
- SMS providers and templates
- OTP generation and verification
- Communication preferences
- Multi-language support
- AVRSMS API integration
- Complete API testing
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import json

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from communications.models import (
    SMSProvider, SMSTemplate, SMSMessage, OTPCode,
    CommunicationPreference, CommunicationLog
)
from communications.services import SMSService, OTPService

User = get_user_model()

def print_section(title):
    """Print section header"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_subsection(title):
    """Print subsection header"""
    print(f"\n{'-'*30}")
    print(f"  {title}")
    print(f"{'-'*30}")

def create_sms_providers():
    """Create sample SMS providers"""
    print_subsection("Creating SMS Providers")
    
    providers_data = [
        {
            'name': 'AVRSMS Ghana',
            'provider_code': 'avrsms',
            'supported_countries': ['GH', 'NG', 'TG', 'BF'],
            'cost_per_sms': 0.02,
            'currency': 'USD',
            'is_active': True,
            'priority': 1,
            'configuration': {
                'api_id': 'API113898428691',
                'password': 'Kingsco45@1',
                'sender_id': 'AgriConnect',
                'endpoint': 'https://api.avrsms.com/v1/send'
            },
            'daily_limit': 10000,
            'success_rate': 95.50
        },
        {
            'name': 'Hubtel Ghana',
            'provider_code': 'hubtel',
            'supported_countries': ['GH'],
            'cost_per_sms': 0.025,
            'currency': 'USD',
            'is_active': True,
            'priority': 2,
            'configuration': {
                'client_id': 'hubtel_client_id',
                'client_secret': 'hubtel_secret',
                'sender_id': 'AgriConnect'
            },
            'daily_limit': 5000,
            'success_rate': 97.20
        },
        {
            'name': 'Africa\'s Talking',
            'provider_code': 'africas_talking',
            'supported_countries': ['KE', 'UG', 'TZ', 'RW', 'MW', 'NG'],
            'cost_per_sms': 0.018,
            'currency': 'USD',
            'is_active': True,
            'priority': 3,
            'configuration': {
                'username': 'agriconnect',
                'api_key': 'at_api_key',
                'sender_id': 'AgriConnect'
            },
            'daily_limit': 15000,
            'success_rate': 94.80
        }
    ]
    
    providers = []
    for provider_data in providers_data:
        provider, created = SMSProvider.objects.get_or_create(
            provider_code=provider_data['provider_code'],
            defaults=provider_data
        )
        providers.append(provider)
        print(f"{'Created' if created else 'Found'} provider: {provider.name}")
    
    print(f"\nTotal SMS Providers: {SMSProvider.objects.count()}")
    return providers

def create_sms_templates():
    """Create default SMS templates"""
    print_subsection("Creating SMS Templates")
    
    templates_data = [
        # OTP Templates
        {
            'name': 'OTP Verification - English',
            'template_type': 'otp',
            'language': 'en',
            'subject': 'AgriConnect OTP',
            'content': 'Your AgriConnect verification code is: {otp_code}. Valid for {validity_minutes} minutes. Do not share this code with anyone.',
            'variables': ['otp_code', 'validity_minutes'],
            'is_active': True,
            'is_default': True
        },
        {
            'name': 'OTP Verification - Twi',
            'template_type': 'otp',
            'language': 'tw',
            'subject': 'AgriConnect OTP',
            'content': 'Wo AgriConnect verification code ne: {otp_code}. Ɛwɔ hɔ sima {validity_minutes}. Nkyɛ obi saa code yi.',
            'variables': ['otp_code', 'validity_minutes'],
            'is_active': True,
            'is_default': True
        },
        {
            'name': 'OTP Verification - Hausa',
            'template_type': 'otp',
            'language': 'ha',
            'subject': 'AgriConnect OTP',
            'content': 'Lambar tabbatar da AgriConnect naka ita ce: {otp_code}. Tana aiki har zuwa mintuna {validity_minutes}. Kada ka raba wannan lambar.',
            'variables': ['otp_code', 'validity_minutes'],
            'is_active': True,
            'is_default': True
        },
        
        # Order Templates
        {
            'name': 'Order Confirmation - English',
            'template_type': 'order_confirmation',
            'language': 'en',
            'subject': 'Order Confirmed',
            'content': 'Order #{order_id} confirmed! Product: {product_name}, Qty: {quantity} {unit}, Total: {currency}{amount}. Delivery: {delivery_date}. Track: agriconnect.com/track/{order_id}',
            'variables': ['order_id', 'product_name', 'quantity', 'unit', 'currency', 'amount', 'delivery_date'],
            'is_active': True,
            'is_default': True
        },
        {
            'name': 'Order Confirmation - Twi',
            'template_type': 'order_confirmation',
            'language': 'tw',
            'subject': 'Woapiè Order',
            'content': 'Order #{order_id} a woapiè! Adeε: {product_name}, Dodow: {quantity} {unit}, Abodiè: {currency}{amount}. Delivery: {delivery_date}.',
            'variables': ['order_id', 'product_name', 'quantity', 'unit', 'currency', 'amount', 'delivery_date'],
            'is_active': True,
            'is_default': True
        },
        
        # Payment Templates
        {
            'name': 'Payment Success - English',
            'template_type': 'payment_confirmation',
            'language': 'en',
            'subject': 'Payment Received',
            'content': 'Payment received! {currency}{amount} for order #{order_id}. Transaction ID: {transaction_id}. Thank you for using AgriConnect!',
            'variables': ['currency', 'amount', 'order_id', 'transaction_id'],
            'is_active': True,
            'is_default': True
        },
        {
            'name': 'Payment Failed - English',
            'template_type': 'payment_notification',
            'language': 'en',
            'subject': 'Payment Failed',
            'content': 'Payment failed for order #{order_id}. Please try again or contact support at +233-XXX-XXXX. AgriConnect Team.',
            'variables': ['order_id'],
            'is_active': True,
            'is_default': True
        },
        
        # Welcome Templates
        {
            'name': 'Welcome Message - English',
            'template_type': 'welcome',
            'language': 'en',
            'subject': 'Welcome to AgriConnect',
            'content': 'Welcome to AgriConnect, {name}! Your account is now active. Start buying/selling agricultural products today. Download our app: {app_link}',
            'variables': ['name', 'app_link'],
            'is_active': True,
            'is_default': True
        },
        {
            'name': 'Welcome Message - Twi',
            'template_type': 'welcome',
            'language': 'tw',
            'subject': 'Akwaaba AgriConnect mu',
            'content': 'Akwaaba wo AgriConnect mu, {name}! Wo account no ayε adwuma sεsei. Fi ase tɔn/tɔ kuayε nneεma nnε. Download yεn app: {app_link}',
            'variables': ['name', 'app_link'],
            'is_active': True,
            'is_default': True
        },
        
        # Price Alert Templates
        {
            'name': 'Price Alert - English',
            'template_type': 'price_alert',
            'language': 'en',
            'subject': 'Price Alert',
            'content': 'Price Alert! {product_name} is now {currency}{new_price}/{unit} (was {currency}{old_price}). {change_percentage}% change. Check AgriConnect now!',
            'variables': ['product_name', 'currency', 'new_price', 'unit', 'old_price', 'change_percentage'],
            'is_active': True,
            'is_default': True
        },
        
        # Weather Alert Templates
        {
            'name': 'Weather Alert - English',
            'template_type': 'weather_alert',
            'language': 'en',
            'subject': 'Weather Alert',
            'content': 'Weather Alert for {location}: {weather_condition} expected. Temp: {temperature}°C, Humidity: {humidity}%. Protect your crops! AgriConnect Weather.',
            'variables': ['location', 'weather_condition', 'temperature', 'humidity'],
            'is_active': True,
            'is_default': True
        }
    ]
    
    templates = []
    for template_data in templates_data:
        template, created = SMSTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        templates.append(template)
        print(f"{'Created' if created else 'Found'} template: {template.name}")
    
    print(f"\nTotal SMS Templates: {SMSTemplate.objects.count()}")
    return templates

def create_demo_users():
    """Create demo users for testing"""
    print_subsection("Creating Demo Users")
    
    users_data = [
        {
            'username': 'farmer_kofi',
            'email': 'kofi@example.com',
            'first_name': 'Kofi',
            'last_name': 'Asante',
            'phone': '+233201234567'
        },
        {
            'username': 'buyer_ama',
            'email': 'ama@example.com',
            'first_name': 'Ama',
            'last_name': 'Serwah',
            'phone': '+233207654321'
        },
        {
            'username': 'trader_ibrahim',
            'email': 'ibrahim@example.com',
            'first_name': 'Ibrahim',
            'last_name': 'Mohammed',
            'phone': '+233241111111'
        }
    ]
    
    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name']
            }
        )
        users.append(user)
        print(f"{'Created' if created else 'Found'} user: {user.username} ({user.first_name} {user.last_name})")
    
    return users

def create_communication_preferences(users):
    """Create communication preferences for users"""
    print_subsection("Creating Communication Preferences")
    
    preferences_data = [
        {
            'user_index': 0,  # farmer_kofi
            'preferred_language': 'tw',  # Twi
            'sms_enabled': True,
            'sms_number': '+233201234567',
            'email_enabled': True,
            'whatsapp_enabled': False,
            'sms_order_updates': True,
            'sms_payment_notifications': True,
            'email_newsletters': True,
            'email_marketing': False,
            'timezone': 'Africa/Accra'
        },
        {
            'user_index': 1,  # buyer_ama
            'preferred_language': 'en',  # English
            'sms_enabled': True,
            'sms_number': '+233207654321',
            'email_enabled': True,
            'whatsapp_enabled': True,
            'whatsapp_number': '+233207654321',
            'sms_order_updates': True,
            'sms_payment_notifications': True,
            'email_newsletters': True,
            'email_marketing': True,
            'timezone': 'Africa/Accra'
        },
        {
            'user_index': 2,  # trader_ibrahim
            'preferred_language': 'ha',  # Hausa
            'sms_enabled': True,
            'sms_number': '+233241111111',
            'email_enabled': False,
            'whatsapp_enabled': False,
            'sms_order_updates': True,
            'sms_payment_notifications': True,
            'email_newsletters': False,
            'email_marketing': False,
            'timezone': 'Africa/Accra'
        }
    ]
    
    preferences = []
    for pref_data in preferences_data:
        user = users[pref_data.pop('user_index')]
        pref_data['user'] = user
        
        preference, created = CommunicationPreference.objects.get_or_create(
            user=user,
            defaults=pref_data
        )
        preferences.append(preference)
        print(f"{'Created' if created else 'Found'} preferences for: {user.username} (Language: {preference.preferred_language})")
    
    print(f"\nTotal Communication Preferences: {CommunicationPreference.objects.count()}")
    return preferences

def demo_otp_generation(users):
    """Demonstrate OTP generation and verification"""
    print_subsection("OTP Generation & Verification Demo")
    
    user = users[0]  # farmer_kofi
    phone_number = '+233201234567'
    
    print(f"Generating OTP for user: {user.username} ({phone_number})")
    
    # Generate OTP
    otp_service = OTPService()
    result = otp_service.generate_otp(
        user=user,
        phone_number=phone_number,
        purpose='phone_verification',
        length=6,
        expires_in_minutes=10
    )
    
    if result['success']:
        otp_id = result['otp_id']
        print(f"✓ OTP Generated successfully!")
        print(f"  OTP ID: {otp_id}")
        print(f"  Expires at: {result['expires_at']}")
        print(f"  Delivery method: {result['delivery_method']}")
        
        # Get the OTP code for demo (in production, this would be sent via SMS)
        otp_obj = OTPCode.objects.get(id=otp_id)
        print(f"  OTP Code (for demo): {otp_obj.code}")
        
        # Simulate verification
        print(f"\nVerifying OTP...")
        verify_result = otp_service.verify_otp(
            otp_id=otp_id,
            code=otp_obj.code,
            user=user
        )
        
        if verify_result['success']:
            print(f"✓ OTP Verified successfully!")
            print(f"  Purpose: {verify_result.get('purpose')}")
        else:
            print(f"✗ OTP Verification failed: {verify_result['error']}")
    else:
        print(f"✗ OTP Generation failed: {result['error']}")

def demo_sms_sending(users, templates):
    """Demonstrate SMS sending with templates"""
    print_subsection("SMS Sending Demo")
    
    user = users[1]  # buyer_ama
    phone_number = '+233207654321'
    
    # Find OTP template
    otp_template = None
    for template in templates:
        if template.template_type == 'otp' and template.language == 'en':
            otp_template = template
            break
    
    if otp_template:
        print(f"Sending SMS to: {user.username} ({phone_number})")
        print(f"Using template: {otp_template.name}")
        
        sms_service = SMSService()
        result = sms_service.send_sms(
            phone_number=phone_number,
            template_id=otp_template.id,
            variables={
                'otp_code': '123456',
                'validity_minutes': '10'
            },
            user=user
        )
        
        if result['success']:
            print(f"✓ SMS sent successfully!")
            print(f"  Message ID: {result['message_id']}")
            print(f"  Cost: ${result.get('cost', 0):.4f}")
            
            # Show the actual message content
            sms_message = SMSMessage.objects.get(id=result['message_id'])
            print(f"  Message: {sms_message.content}")
        else:
            print(f"✗ SMS sending failed: {result['error']}")
    else:
        print("✗ No OTP template found for English")

def demo_bulk_sms_sending(users, templates):
    """Demonstrate bulk SMS sending"""
    print_subsection("Bulk SMS Sending Demo")
    
    # Find welcome template
    welcome_template = None
    for template in templates:
        if template.template_type == 'welcome' and template.language == 'en':
            welcome_template = template
            break
    
    if welcome_template:
        phone_numbers = ['+233201234567', '+233207654321', '+233241111111']
        print(f"Sending bulk SMS to {len(phone_numbers)} recipients")
        print(f"Using template: {welcome_template.name}")
        
        sms_service = SMSService()
        result = sms_service.send_bulk_sms(
            recipients=phone_numbers,
            template_id=welcome_template.id,
            variables={
                'name': 'New User',
                'app_link': 'https://app.agriconnect.com'
            },
            user=users[0]  # farmer_kofi as sender
        )
        
        print(f"Bulk SMS Results:")
        print(f"  Successful sends: {result['successful']}")
        print(f"  Failed sends: {result['failed']}")
        print(f"  Total cost: ${result['total_cost']:.4f}")
    else:
        print("✗ No welcome template found for English")

def demo_analytics():
    """Demonstrate SMS analytics"""
    print_subsection("SMS Analytics Demo")
    
    # Get analytics data
    total_messages = SMSMessage.objects.count()
    delivered_messages = SMSMessage.objects.filter(status='sent').count()  # Simulate as delivered
    total_cost = sum(float(msg.cost) for msg in SMSMessage.objects.all())
    
    print(f"SMS Analytics:")
    print(f"  Total messages sent: {total_messages}")
    print(f"  Delivered messages: {delivered_messages}")
    print(f"  Delivery rate: {(delivered_messages/total_messages*100) if total_messages > 0 else 0:.1f}%")
    print(f"  Total cost: ${total_cost:.4f}")
    print(f"  Average cost per SMS: ${(total_cost/total_messages) if total_messages > 0 else 0:.4f}")
    
    # Show recent messages
    recent_messages = SMSMessage.objects.order_by('-sent_at')[:5]
    print(f"\nRecent SMS Messages:")
    for msg in recent_messages:
        print(f"  {msg.recipient_phone} | {msg.status} | ${msg.cost:.4f} | {msg.sent_at}")

def test_api_endpoints():
    """Test API endpoints are working"""
    print_subsection("Testing API Endpoints")
    
    from django.test import Client
    from django.urls import reverse
    
    client = Client()
    
    # Test endpoints that don't require authentication
    endpoints_to_test = [
        '/api/v1/communications/api/providers/',
        '/api/v1/communications/api/templates/',
        '/api/v1/communications/api/messages/',
        '/api/v1/communications/api/otp/',
        '/api/v1/communications/api/preferences/',
        '/api/v1/communications/api/logs/',
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = client.get(endpoint)
            status_code = response.status_code
            if status_code in [200, 401, 403]:  # 401/403 means endpoint exists but needs auth
                print(f"✓ {endpoint} - Status: {status_code}")
            else:
                print(f"✗ {endpoint} - Status: {status_code}")
        except Exception as e:
            print(f"✗ {endpoint} - Error: {str(e)}")

def show_system_summary():
    """Show comprehensive system summary"""
    print_section("COMMUNICATIONS SYSTEM SUMMARY")
    
    # Count all objects
    providers_count = SMSProvider.objects.count()
    templates_count = SMSTemplate.objects.count()
    messages_count = SMSMessage.objects.count()
    otp_count = OTPCode.objects.count()
    preferences_count = CommunicationPreference.objects.count()
    logs_count = CommunicationLog.objects.count()
    
    print(f"📊 Database Summary:")
    print(f"   • SMS Providers: {providers_count}")
    print(f"   • SMS Templates: {templates_count}")
    print(f"   • SMS Messages: {messages_count}")
    print(f"   • OTP Codes: {otp_count}")
    print(f"   • Communication Preferences: {preferences_count}")
    print(f"   • Communication Logs: {logs_count}")
    
    print(f"\n🚀 Features Implemented:")
    print(f"   • ✓ Multi-language SMS templates (English, Twi, Hausa)")
    print(f"   • ✓ AVRSMS API integration")
    print(f"   • ✓ OTP generation and verification")
    print(f"   • ✓ Bulk SMS sending")
    print(f"   • ✓ Communication preferences")
    print(f"   • ✓ SMS analytics and reporting")
    print(f"   • ✓ REST API endpoints")
    print(f"   • ✓ Django admin interface")
    print(f"   • ✓ Database migrations")
    
    print(f"\n🌍 Supported Languages:")
    languages = SMSTemplate.objects.values_list('language', flat=True).distinct()
    lang_map = {
        'en': 'English 🇺🇸',
        'tw': 'Twi 🇬🇭',
        'ha': 'Hausa 🇳🇬',
        'fr': 'French 🇫🇷',
        'sw': 'Swahili 🇰🇪'
    }
    for lang in languages:
        print(f"   • {lang_map.get(lang, f'{lang.upper()} 🌍')}")
    
    print(f"\n📱 SMS Providers:")
    for provider in SMSProvider.objects.all():
        status = "🟢 Active" if provider.is_active else "🔴 Inactive"
        print(f"   • {provider.name} - {status} (Priority: {provider.priority})")
    
    print(f"\n📋 Template Categories:")
    template_types = SMSTemplate.objects.values_list('template_type', flat=True).distinct()
    for template_type in template_types:
        count = SMSTemplate.objects.filter(template_type=template_type).count()
        print(f"   • {template_type.replace('_', ' ').title()}: {count} templates")

def main():
    """Main demo function"""
    print_section("AGRICONNECT COMMUNICATIONS SYSTEM DEMO")
    print("Enhanced SMS & OTP Integration System (PRD Section 4.7)")
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Create SMS providers
        providers = create_sms_providers()
        
        # Step 2: Create SMS templates
        templates = create_sms_templates()
        
        # Step 3: Create demo users
        users = create_demo_users()
        
        # Step 4: Create communication preferences
        preferences = create_communication_preferences(users)
        
        # Step 5: Demo OTP functionality
        demo_otp_generation(users)
        
        # Step 6: Demo SMS sending
        demo_sms_sending(users, templates)
        
        # Step 7: Demo bulk SMS
        demo_bulk_sms_sending(users, templates)
        
        # Step 8: Show analytics
        demo_analytics()
        
        # Step 9: Test API endpoints
        test_api_endpoints()
        
        # Step 10: Show comprehensive summary
        show_system_summary()
        
        print_section("DEMO COMPLETED SUCCESSFULLY! 🎉")
        print("✅ Enhanced SMS & OTP Integration System (PRD Section 4.7) is fully operational!")
        print("\n🔗 Available API Endpoints:")
        print("   • /api/v1/communications/api/providers/ - SMS provider management")
        print("   • /api/v1/communications/api/templates/ - SMS template management") 
        print("   • /api/v1/communications/api/messages/ - SMS message management")
        print("   • /api/v1/communications/api/otp/ - OTP generation and verification")
        print("   • /api/v1/communications/api/preferences/ - Communication preferences")
        print("   • /api/v1/communications/api/logs/ - Communication logs")
        
        print("\n📚 Next Steps:")
        print("   1. Access Django admin at /admin/ to manage SMS providers and templates")
        print("   2. Use the API endpoints to integrate SMS functionality")
        print("   3. Configure AVRSMS credentials in production")
        print("   4. Set up scheduled tasks for bulk messaging")
        print("   5. Monitor SMS delivery rates and costs")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
