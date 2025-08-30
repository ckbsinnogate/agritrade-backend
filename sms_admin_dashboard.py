#!/usr/bin/env python3
"""
SMS OTP Admin Dashboard
Monitor SMS OTP usage and statistics
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1/auth/sms-otp"

def get_sms_stats():
    """Get SMS OTP statistics"""
    print("📊 AgriConnect SMS OTP Statistics")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/admin/stats/")
        
        if response.status_code == 200:
            stats = response.json()
            
            print(f"📈 Total SMS Sent: {stats.get('total_sent', 0)}")
            print(f"✅ Total Verified: {stats.get('total_verified', 0)}")
            print(f"❌ Total Expired: {stats.get('total_expired', 0)}")
            print(f"🔢 Success Rate: {stats.get('success_rate', 0)}%")
            
            print("\n📱 By Country:")
            by_country = stats.get('by_country', {})
            for country, count in by_country.items():
                print(f"  {country}: {count} SMS")
            
            print("\n🎯 By Purpose:")
            by_purpose = stats.get('by_purpose', {})
            for purpose, count in by_purpose.items():
                print(f"  {purpose.title()}: {count} SMS")
                
            print(f"\n⏰ Report Generated: {stats.get('generated_at', 'N/A')}")
            
        else:
            print("❌ Failed to get statistics")
            print(f"Status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        print("Make sure Django server is running on localhost:8000")

def cleanup_old_otps():
    """Cleanup expired SMS OTPs"""
    print("\n🧹 Cleaning up expired SMS OTPs...")
    
    try:
        response = requests.post(f"{API_BASE}/admin/cleanup/")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Cleanup completed:")
            print(f"  Expired marked: {result.get('expired_marked', 0)}")
            print(f"  Old deleted: {result.get('old_deleted', 0)}")
            print(f"  Total processed: {result.get('total_processed', 0)}")
        else:
            print("❌ Cleanup failed")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cleanup request failed: {str(e)}")

if __name__ == "__main__":
    get_sms_stats()
    cleanup_old_otps()
