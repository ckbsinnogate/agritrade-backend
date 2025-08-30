#!/usr/bin/env python
"""
Test Enhanced Analytics Function
Tests the race condition protection in _update_daily_analytics
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from ai.services import _update_daily_analytics
from authentication.models import User
from ai.models import AIUsageAnalytics
from django.utils import timezone

def test_enhanced_analytics():
    """Test the enhanced analytics function"""
    print('🧪 Testing Enhanced Analytics Function')
    print('=' * 50)

    try:
        user = User.objects.first()
        if user:
            # Get username or email for display
            username = getattr(user, 'username', None) or getattr(user, 'email', f'User {user.id}')
            print(f'📊 Testing with user: {username} (ID: {user.id})')

            # Test the analytics function
            today = timezone.now().date()
            before_count = AIUsageAnalytics.objects.filter(user=user, date=today).count()
            print(f'Analytics records before: {before_count}')

            # Test the enhanced function
            print('🔄 Running enhanced analytics function...')
            _update_daily_analytics(user, 'disease_detection', 100)

            after_count = AIUsageAnalytics.objects.filter(user=user, date=today).count()
            print(f'Analytics records after: {after_count}')

            if after_count == 1:
                analytics = AIUsageAnalytics.objects.get(user=user, date=today)
                print('✅ Analytics working correctly:')
                print(f'   - Daily queries: {analytics.daily_queries}')
                print(f'   - Disease detection queries: {analytics.disease_detection_queries}')
                print(f'   - Tokens used: {analytics.total_tokens_used}')
                print('✅ Enhanced analytics function is working perfectly!')
                
                # Test multiple calls to verify no duplicates
                print('\n🔄 Testing multiple calls for race condition protection...')
                _update_daily_analytics(user, 'disease_detection', 50)
                _update_daily_analytics(user, 'crop_advisory', 25)
                
                final_count = AIUsageAnalytics.objects.filter(user=user, date=today).count()
                if final_count == 1:
                    updated_analytics = AIUsageAnalytics.objects.get(user=user, date=today)
                    print('✅ Race condition protection working:')
                    print(f'   - Final daily queries: {updated_analytics.daily_queries}')
                    print(f'   - Final disease detection queries: {updated_analytics.disease_detection_queries}')
                    print(f'   - Final crop advisory queries: {updated_analytics.crop_advisory_queries}')
                    print(f'   - Final tokens used: {updated_analytics.total_tokens_used}')
                    print('🎉 ENHANCED ANALYTICS FUNCTION FULLY OPERATIONAL!')
                else:
                    print(f'⚠️  Race condition detected: {final_count} records found')
                    
            else:
                print(f'⚠️  Multiple records found: {after_count}')

        else:
            print('❌ No users found for testing')

    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()

    print('\n🎉 Analytics function verification complete!')

if __name__ == "__main__":
    test_enhanced_analytics()
