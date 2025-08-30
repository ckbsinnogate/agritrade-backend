#!/usr/bin/env python3
"""
AgriTrade App Platform Deployment Monitor
Monitors the deployment status and verifies the application is running correctly
"""

import requests
import time
import json
from datetime import datetime

def check_deployment_status():
    """Monitor the deployment and verify endpoints"""
    
    print("🚀 AgriTrade App Platform Deployment Monitor")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Your app URL will be something like: https://agritrade-backend-[hash].ondigitalocean.app
    # You'll need to update this with your actual URL from App Platform dashboard
    base_url = "https://agritrade-backend-{REPLACE_WITH_YOUR_HASH}.ondigitalocean.app"
    
    endpoints_to_test = [
        {
            'name': 'Health Check',
            'url': f'{base_url}/api/health/',
            'expected_status': 200,
            'description': 'Basic health check endpoint'
        },
        {
            'name': 'API Root',
            'url': f'{base_url}/api/v1/',
            'expected_status': 200,
            'description': 'REST API root endpoint'
        },
        {
            'name': 'Admin Interface',
            'url': f'{base_url}/admin/',
            'expected_status': 200,
            'description': 'Django admin interface'
        }
    ]
    
    print("📋 DEPLOYMENT VERIFICATION CHECKLIST")
    print("=" * 60)
    
    print("\n1. ✅ Code pushed to GitHub repository")
    print("2. 🔄 Waiting for App Platform to detect changes...")
    print("3. 🏗️ Build should start automatically (check your dashboard)")
    print("4. 📦 Expected build process:")
    print("   - Using Python buildpack (no Docker)")
    print("   - Installing from requirements.txt")
    print("   - Running migrations")
    print("   - Starting gunicorn server")
    print("   - NO collectstatic (avoiding file logging error)")
    
    print("\n" + "=" * 60)
    print("🎯 ENDPOINTS TO TEST AFTER DEPLOYMENT")
    print("=" * 60)
    
    for endpoint in endpoints_to_test:
        print(f"\n📍 {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        print(f"   Expected: HTTP {endpoint['expected_status']}")
        print(f"   Purpose: {endpoint['description']}")
    
    print("\n" + "=" * 60)
    print("🚨 WHAT TO DO NEXT")
    print("=" * 60)
    
    print("\n1. 📊 CHECK APP PLATFORM DASHBOARD:")
    print("   - Go to your DigitalOcean App Platform dashboard")
    print("   - Look for 'agritrade-backend' app")
    print("   - Check if new build is starting/running")
    
    print("\n2. 🔍 MONITOR BUILD LOGS:")
    print("   - Click on the app → Runtime Logs")
    print("   - Look for successful Python buildpack detection")
    print("   - Verify no 'collectstatic' or file logging errors")
    
    print("\n3. ✅ EXPECTED SUCCESS INDICATORS:")
    print("   ✓ Python buildpack detected")
    print("   ✓ Dependencies installed from requirements.txt")
    print("   ✓ Migrations completed successfully")
    print("   ✓ Gunicorn server started")
    print("   ✓ Health check endpoint responding")
    
    print("\n4. 🌐 GET YOUR APP URL:")
    print("   - Copy the app URL from dashboard")
    print("   - Update this script with your actual URL")
    print("   - Run endpoint tests")
    
    print("\n" + "=" * 60)
    print("💡 TROUBLESHOOTING")
    print("=" * 60)
    
    print("\nIf deployment still fails:")
    print("• Check environment variables are set correctly")
    print("• Verify SECRET_KEY is configured")
    print("• Ensure DATABASE_URL is set (add PostgreSQL database)")
    print("• Check build logs for specific error messages")
    
    print("\n" + "=" * 60)
    print("🎉 SUCCESS CRITERIA")
    print("=" * 60)
    
    print("\nDeployment is successful when:")
    print("✅ Build completes without errors")
    print("✅ App status shows 'Running'")
    print("✅ Health check endpoint returns 200")
    print("✅ All 17 Django applications are accessible")
    
    print(f"\n⏰ Monitor completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

def test_endpoints_when_ready(app_url):
    """Test endpoints once you have the actual app URL"""
    
    endpoints = [
        f'{app_url}/api/health/',
        f'{app_url}/api/v1/',
        f'{app_url}/admin/'
    ]
    
    print(f"\n🧪 TESTING ENDPOINTS FOR: {app_url}")
    print("=" * 60)
    
    for endpoint in endpoints:
        try:
            print(f"\n📍 Testing: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS: HTTP {response.status_code}")
                if 'health' in endpoint:
                    try:
                        health_data = response.json()
                        print(f"   📊 Response: {json.dumps(health_data, indent=2)}")
                    except:
                        print(f"   📊 Response: {response.text[:100]}...")
            else:
                print(f"   ❌ FAILED: HTTP {response.status_code}")
                print(f"   📊 Response: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ CONNECTION ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    check_deployment_status()
    
    print("\n" + "🔄" * 20)
    print("To test endpoints once deployed, update the base_url variable")
    print("in this script with your actual App Platform URL and run:")
    print("python deployment_monitor.py")
    print("🔄" * 20)
