#!/usr/bin/env python
"""
AgriConnect SMS Testing Script
Test SMS functionality with specific phone numbers using AVRSMS integration
"""

import os
import sys
import django
from datetime import datetime, timedelta
import time

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    sys.exit(1)

def test_sms_with_numbers():
    """Test SMS functionality with specific phone numbers"""
    
    print("📱 AGRICONNECT SMS TESTING")
    print("=" * 50)
    print(f"Test Date: {datetime.now().strftime('%B %d, %Y at %H:%M')}")
    print()
    
    # Test phone numbers
    test_numbers = [
        "0200430852",  # Ghana MTN number
        "0548577075"   # Ghana MTN number
    ]
    
    try:
        from communications.models import SMSProvider, SMSTemplate, SMSMessage, OTPCode
        from communications.services import SMSService, OTPService
        from authentication.models import User
        
        print("✅ Successfully imported communication models and services")
        print()
        
        # Check SMS provider status
        print("🔧 SMS PROVIDER STATUS")
        print("-" * 30)
        
        providers = SMSProvider.objects.all()
        if providers.exists():
            for provider in providers:
                status = "🟢 ACTIVE" if provider.is_active else "🔴 INACTIVE"
                print(f"{status} {provider.name} - {provider.provider_type}")
                if provider.name == 'AVRSMS':
                    print(f"   API ID: {provider.api_credentials.get('api_id', 'Not set')}")
                    print(f"   Endpoint: {provider.api_endpoint}")
        else:
            print("❌ No SMS providers configured")
            print("Setting up AVRSMS provider...")
            
            # Create AVRSMS provider
            avrsms_provider = SMSProvider.objects.create(
                name='AVRSMS',
                provider_type='avrsms',
                api_endpoint='https://api.avrsms.com/v1/sms/send',
                api_credentials={
                    'api_id': 'API113898428691',
                    'password': 'Kingsco45@1'
                },
                is_active=True,
                supported_countries=['GH', 'NG'],
                rate_limit_per_minute=100
            )
            print(f"✅ Created AVRSMS provider: {avrsms_provider.name}")
        
        print()
        
        # Check SMS templates
        print("📝 SMS TEMPLATES STATUS")
        print("-" * 30)
        
        templates = SMSTemplate.objects.all()
        if templates.exists():
            print(f"✅ Found {templates.count()} SMS templates")
            for template in templates[:3]:  # Show first 3
                print(f"   • {template.name} ({template.language})")
        else:
            print("⚠️  No SMS templates found, creating basic templates...")
            
            # Create basic SMS templates
            test_template = SMSTemplate.objects.create(
                name='test_message',
                language='en',
                message_type='general',
                content='Hello {name}! This is a test message from AgriConnect. Time: {timestamp}',
                variables=['name', 'timestamp']
            )
            
            otp_template = SMSTemplate.objects.create(
                name='otp_verification',
                language='en',
                message_type='otp',
                content='Your AgriConnect verification code is: {otp_code}. Valid for {expiry_minutes} minutes.',
                variables=['otp_code', 'expiry_minutes']
            )
            
            print(f"✅ Created basic templates: {test_template.name}, {otp_template.name}")
        
        print()
        
        # Test SMS sending
        print("📤 SMS SENDING TESTS")
        print("-" * 30)
        
        sms_service = SMSService()
        
        for i, phone_number in enumerate(test_numbers, 1):
            print(f"\n🧪 Test {i}: Sending to {phone_number}")
            print("-" * 25)
            
            # Format phone number for Ghana
            if phone_number.startswith('0'):
                formatted_number = f"+233{phone_number[1:]}"
            else:
                formatted_number = phone_number
            
            print(f"📞 Formatted number: {formatted_number}")
            
            # Test message content
            test_message = f"Hello! This is a test SMS from AgriConnect platform. Sent at {datetime.now().strftime('%H:%M on %B %d, %Y')}. If you received this, our SMS system is working correctly! 🌾"
            
            try:
                # Send test message
                result = sms_service.send_sms(
                    phone_number=formatted_number,
                    message=test_message,
                    message_type='test'
                )
                
                if result.get('success'):
                    print(f"✅ SMS sent successfully!")
                    print(f"   Message ID: {result.get('message_id', 'N/A')}")
                    print(f"   Status: {result.get('status', 'N/A')}")
                    print(f"   Cost: {result.get('cost', 'N/A')}")
                    
                    # Save to database
                    sms_message = SMSMessage.objects.create(
                        phone_number=formatted_number,
                        message=test_message,
                        message_type='test',
                        provider=SMSProvider.objects.filter(is_active=True).first(),
                        status='sent',
                        external_message_id=result.get('message_id'),
                        cost=result.get('cost', 0.0)
                    )
                    print(f"   Database record: {sms_message.id}")
                    
                else:
                    print(f"❌ SMS sending failed!")
                    print(f"   Error: {result.get('error', 'Unknown error')}")
                    print(f"   Details: {result.get('details', 'N/A')}")
                
            except Exception as e:
                print(f"❌ Exception during SMS sending: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Wait between messages to respect rate limits
            if i < len(test_numbers):
                print("⏳ Waiting 5 seconds before next message...")
                time.sleep(5)
        
        print()
        
        # Test OTP functionality
        print("🔐 OTP VERIFICATION TESTS")
        print("-" * 30)
        
        otp_service = OTPService()
        
        for i, phone_number in enumerate(test_numbers, 1):
            print(f"\n🧪 OTP Test {i}: {phone_number}")
            print("-" * 20)
            
            # Format phone number
            if phone_number.startswith('0'):
                formatted_number = f"+233{phone_number[1:]}"
            else:
                formatted_number = phone_number
            
            try:
                # Generate and send OTP
                otp_result = otp_service.generate_and_send_otp(
                    phone_number=formatted_number,
                    purpose='test_verification'
                )
                
                if otp_result.get('success'):
                    otp_code = otp_result.get('otp_code')
                    print(f"✅ OTP generated and sent!")
                    print(f"   OTP Code: {otp_code}")
                    print(f"   Expires: {otp_result.get('expires_at')}")
                    print(f"   SMS Status: {otp_result.get('sms_status', 'N/A')}")
                    
                    # Test OTP verification
                    print(f"\n🔍 Testing OTP verification...")
                    verify_result = otp_service.verify_otp(
                        phone_number=formatted_number,
                        otp_code=otp_code,
                        purpose='test_verification'
                    )
                    
                    if verify_result.get('valid'):
                        print(f"✅ OTP verification successful!")
                    else:
                        print(f"❌ OTP verification failed: {verify_result.get('error')}")
                    
                else:
                    print(f"❌ OTP generation failed!")
                    print(f"   Error: {otp_result.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"❌ Exception during OTP test: {str(e)}")
            
            # Wait between OTP tests
            if i < len(test_numbers):
                print("⏳ Waiting 3 seconds before next OTP test...")
                time.sleep(3)
        
        print()
        
        # Display statistics
        print("📊 TEST STATISTICS")
        print("-" * 30)
        
        total_messages = SMSMessage.objects.count()
        sent_messages = SMSMessage.objects.filter(status='sent').count()
        failed_messages = SMSMessage.objects.filter(status='failed').count()
        total_otps = OTPCode.objects.count()
        
        print(f"📱 Total SMS Messages: {total_messages}")
        print(f"✅ Successfully Sent: {sent_messages}")
        print(f"❌ Failed Messages: {failed_messages}")
        print(f"🔐 Total OTP Codes: {total_otps}")
        
        if total_messages > 0:
            success_rate = (sent_messages / total_messages) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print()
        
        # Recent messages
        print("📋 RECENT MESSAGES")
        print("-" * 30)
        
        recent_messages = SMSMessage.objects.order_by('-created_at')[:5]
        for msg in recent_messages:
            status_emoji = "✅" if msg.status == 'sent' else "❌" if msg.status == 'failed' else "⏳"
            print(f"{status_emoji} {msg.phone_number} - {msg.message_type} - {msg.created_at.strftime('%H:%M:%S')}")
            print(f"   {msg.message[:50]}{'...' if len(msg.message) > 50 else ''}")
        
        print()
        print("🎉 SMS TESTING COMPLETE!")
        print("=" * 50)
        print("✅ SMS functionality has been tested with both phone numbers")
        print("✅ Check your phones for received messages")
        print("✅ OTP verification workflow tested")
        print()
        print("📱 Next Steps:")
        print("1. Verify you received the test messages")
        print("2. Check if OTP codes were delivered")
        print("3. Review the statistics above")
        print("4. Check Django admin for detailed logs")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure the communications app is properly installed and migrated")
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sms_with_numbers()
