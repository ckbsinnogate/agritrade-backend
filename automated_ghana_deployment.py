#!/usr/bin/env python
"""
AgriConnect Ghana - Automated Production Deployment
Complete deployment automation for Ghana agricultural platform
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

class GhanaProductionDeployer:
    """Automated deployment manager for AgriConnect Ghana"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_config = {}
        self.deployment_steps = []
        
    def check_prerequisites(self):
        """Check deployment prerequisites"""
        print("🔍 CHECKING DEPLOYMENT PREREQUISITES")
        print("-" * 40)
        
        checks = []
        
        # Check Git
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
            checks.append(("Git installed", True))
            print("✅ Git: Available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            checks.append(("Git installed", False))
            print("❌ Git: Not found")
        
        # Check Heroku CLI
        try:
            subprocess.run(['heroku', '--version'], capture_output=True, check=True)
            checks.append(("Heroku CLI", True))
            print("✅ Heroku CLI: Available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            checks.append(("Heroku CLI", False))
            print("❌ Heroku CLI: Not found")
        
        # Check Python
        try:
            python_version = sys.version.split()[0]
            checks.append(("Python 3.11+", python_version.startswith('3.11')))
            print(f"✅ Python: {python_version}")
        except:
            checks.append(("Python 3.11+", False))
            print("❌ Python: Version check failed")
        
        # Check Django project files
        required_files = ['manage.py', 'Procfile', 'requirements.txt', 'app.json']
        for file in required_files:
            file_exists = (self.project_root / file).exists()
            checks.append((f"{file} exists", file_exists))
            print(f"{'✅' if file_exists else '❌'} {file}: {'Found' if file_exists else 'Missing'}")
        
        # Check production settings
        prod_settings = (self.project_root / 'agriconnect' / 'production_settings.py').exists()
        checks.append(("Production settings", prod_settings))
        print(f"{'✅' if prod_settings else '❌'} Production settings: {'Found' if prod_settings else 'Missing'}")
        
        all_passed = all(check[1] for check in checks)
        
        if all_passed:
            print(f"\n🎉 All prerequisites met!")
        else:
            print(f"\n❌ Prerequisites missing:")
            for check_name, passed in checks:
                if not passed:
                    print(f"   • {check_name}")
        
        return all_passed, checks
    
    def gather_deployment_config(self):
        """Gather deployment configuration from user"""
        print("\n⚙️  GHANA DEPLOYMENT CONFIGURATION")
        print("-" * 38)
        
        print("📋 Please provide the following information:")
        
        # App name
        app_name = input("🏷️  Heroku app name (e.g., agriconnect-ghana): ").strip()
        if not app_name:
            app_name = "agriconnect-ghana"
        
        # Domain
        domain = input(f"🌐 Custom domain (optional, press Enter for {app_name}.herokuapp.com): ").strip()
        if not domain:
            domain = f"{app_name}.herokuapp.com"
        
        # Environment
        env_type = input("🏗️  Environment (production/staging) [production]: ").strip().lower()
        if env_type not in ['production', 'staging']:
            env_type = 'production'
        
        # Paystack keys
        print(f"\n💳 Paystack Configuration for Ghana:")
        paystack_public = input("🔑 Paystack Public Key (pk_live_... or pk_test_...): ").strip()
        paystack_secret = input("🔐 Paystack Secret Key (sk_live_... or sk_test_...): ").strip()
        webhook_secret = input("🔔 Webhook Secret (optional, can be set later): ").strip()
        
        # Email configuration
        print(f"\n📧 Email Configuration:")
        email_user = input("📮 Email address for notifications: ").strip()
        email_pass = input("🔒 Email password/app password: ").strip()
        
        self.deployment_config = {
            'app_name': app_name,
            'domain': domain,
            'environment': env_type,
            'paystack': {
                'public_key': paystack_public,
                'secret_key': paystack_secret,
                'webhook_secret': webhook_secret
            },
            'email': {
                'user': email_user,
                'password': email_pass
            },
            'ghana_config': {
                'default_currency': 'GHS',
                'target_market': 'Ghana',
                'timezone': 'Africa/Accra'
            }
        }
        
        print(f"\n✅ Configuration collected:")
        print(f"   App: {app_name}")
        print(f"   Domain: {domain}")
        print(f"   Environment: {env_type}")
        print(f"   Currency: GHS (Ghana Cedis)")
        
        return True
    
    def create_deployment_files(self):
        """Create/update deployment files"""
        print(f"\n📁 CREATING DEPLOYMENT FILES")
        print("-" * 32)
        
        # Update Procfile
        procfile_content = f"""web: gunicorn agriconnect.wsgi:application --bind 0.0.0.0:$PORT --workers 2
worker: celery -A agriconnect worker --loglevel=info
beat: celery -A agriconnect beat --loglevel=info
release: python manage.py migrate --settings=agriconnect.production_settings"""
        
        with open(self.project_root / 'Procfile', 'w') as f:
            f.write(procfile_content)
        print("✅ Procfile updated")
        
        # Update runtime.txt
        with open(self.project_root / 'runtime.txt', 'w') as f:
            f.write("python-3.11.5")
        print("✅ runtime.txt created")
        
        # Create .env template
        env_template = f"""# AgriConnect Ghana Production Environment
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS={self.deployment_config['domain']}
DATABASE_URL=postgres://user:pass@host:port/dbname

# Ghana Configuration
DEFAULT_CURRENCY=GHS
TARGET_MARKET=Ghana
SITE_URL=https://{self.deployment_config['domain']}

# Paystack Ghana
PAYSTACK_PUBLIC_KEY={self.deployment_config['paystack']['public_key']}
PAYSTACK_SECRET_KEY={self.deployment_config['paystack']['secret_key']}
PAYSTACK_WEBHOOK_SECRET={self.deployment_config['paystack']['webhook_secret']}

# Email Configuration
EMAIL_HOST_USER={self.deployment_config['email']['user']}
EMAIL_HOST_PASSWORD={self.deployment_config['email']['password']}

# Redis/Cache
REDIS_URL=redis://localhost:6379/0
"""
        
        with open(self.project_root / f'{self.deployment_config["environment"]}.env', 'w') as f:
            f.write(env_template)
        print(f"✅ {self.deployment_config['environment']}.env created")
        
        # Update app.json for Ghana
        app_json = {
            "name": "AgriConnect Ghana",
            "description": "Agricultural commerce platform for Ghana with mobile money integration",
            "repository": "https://github.com/yourusername/agriconnect-ghana",
            "keywords": ["django", "agriculture", "payments", "ghana", "paystack", "mobile-money"],
            "website": f"https://{self.deployment_config['domain']}",
            "env": {
                "SECRET_KEY": {"generator": "secret"},
                "DEBUG": {"value": "False"},
                "DEFAULT_CURRENCY": {"value": "GHS"},
                "TARGET_MARKET": {"value": "Ghana"},
                "PAYSTACK_PUBLIC_KEY": {"value": self.deployment_config['paystack']['public_key']},
                "PAYSTACK_SECRET_KEY": {"value": self.deployment_config['paystack']['secret_key']},
                "EMAIL_HOST_USER": {"value": self.deployment_config['email']['user']}
            },
            "addons": [
                "heroku-postgresql:mini",
                "heroku-redis:mini"
            ],
            "buildpacks": [{"url": "heroku/python"}],
            "stack": "heroku-22"
        }
        
        with open(self.project_root / 'app.json', 'w') as f:
            json.dump(app_json, f, indent=2)
        print("✅ app.json updated for Ghana")
        
        return True
    
    def generate_deployment_script(self):
        """Generate deployment script"""
        print(f"\n🚀 GENERATING DEPLOYMENT SCRIPT")
        print("-" * 35)
        
        script_content = f"""#!/bin/bash
# AgriConnect Ghana - Production Deployment Script
# Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

echo "🇬🇭 AGRICONNECT GHANA - PRODUCTION DEPLOYMENT"
echo "=============================================="

# Step 1: Login to Heroku
echo "🔐 Step 1: Heroku Login"
heroku login

# Step 2: Create Heroku App
echo "🏗️  Step 2: Creating Heroku App"
heroku create {self.deployment_config['app_name']} || echo "App may already exist"

# Step 3: Set Environment Variables
echo "⚙️  Step 3: Setting Environment Variables"
heroku config:set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" --app {self.deployment_config['app_name']}
heroku config:set DEBUG=False --app {self.deployment_config['app_name']}
heroku config:set DEFAULT_CURRENCY=GHS --app {self.deployment_config['app_name']}
heroku config:set TARGET_MARKET=Ghana --app {self.deployment_config['app_name']}
heroku config:set SITE_URL=https://{self.deployment_config['domain']} --app {self.deployment_config['app_name']}
heroku config:set PAYSTACK_PUBLIC_KEY={self.deployment_config['paystack']['public_key']} --app {self.deployment_config['app_name']}
heroku config:set PAYSTACK_SECRET_KEY={self.deployment_config['paystack']['secret_key']} --app {self.deployment_config['app_name']}
heroku config:set EMAIL_HOST_USER={self.deployment_config['email']['user']} --app {self.deployment_config['app_name']}
heroku config:set EMAIL_HOST_PASSWORD={self.deployment_config['email']['password']} --app {self.deployment_config['app_name']}

# Step 4: Add Database and Redis
echo "🗄️  Step 4: Adding Database and Redis"
heroku addons:create heroku-postgresql:mini --app {self.deployment_config['app_name']}
heroku addons:create heroku-redis:mini --app {self.deployment_config['app_name']}

# Step 5: Deploy Application
echo "📦 Step 5: Deploying Application"
git add .
git commit -m "Production deployment for Ghana - $(date)"
git push heroku main

# Step 6: Run Database Migrations
echo "🔄 Step 6: Running Database Migrations"
heroku run python manage.py migrate --settings=agriconnect.production_settings --app {self.deployment_config['app_name']}
heroku run python manage.py collectstatic --noinput --settings=agriconnect.production_settings --app {self.deployment_config['app_name']}

# Step 7: Setup Ghana Configuration
echo "🇬🇭 Step 7: Setting up Ghana Configuration"
heroku run python setup_paystack_ghana.py --app {self.deployment_config['app_name']}

# Step 8: Create Superuser (Interactive)
echo "👤 Step 8: Create Superuser"
heroku run python manage.py createsuperuser --settings=agriconnect.production_settings --app {self.deployment_config['app_name']}

# Step 9: Open Application
echo "🌐 Step 9: Opening Application"
heroku open --app {self.deployment_config['app_name']}

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================="
echo "🇬🇭 App URL: https://{self.deployment_config['domain']}"
echo "💳 Currency: Ghana Cedis (GHS)"
echo "📱 Mobile Money: MTN, Vodafone, AirtelTigo"
echo "🔔 Webhook: https://{self.deployment_config['domain']}/api/v1/payments/webhook/paystack/"
echo ""
echo "🚀 NEXT STEPS:"
echo "1. Add webhook URL to Paystack dashboard"
echo "2. Configure webhook secret using enhanced_webhook_management.py"
echo "3. Test with Ghana payment methods"
echo "4. Begin farmer onboarding in Ashanti Region"
echo ""
"""
        
        script_path = self.project_root / 'deploy_ghana.sh'
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable on Unix-like systems
        if os.name != 'nt':
            os.chmod(script_path, 0o755)
        
        print(f"✅ Deployment script created: deploy_ghana.sh")
        
        # Also create a PowerShell version for Windows
        ps_script = script_content.replace('#!/bin/bash', '# PowerShell version').replace('echo ', 'Write-Host ')
        
        with open(self.project_root / 'deploy_ghana.ps1', 'w') as f:
            f.write(ps_script)
        
        print(f"✅ PowerShell script created: deploy_ghana.ps1")
        
        return True
    
    def create_post_deployment_checklist(self):
        """Create post-deployment verification checklist"""
        print(f"\n📋 POST-DEPLOYMENT CHECKLIST")
        print("-" * 32)
        
        checklist = f"""# 🇬🇭 AgriConnect Ghana - Post-Deployment Checklist

## 🎯 **IMMEDIATE VERIFICATION (First 30 minutes)**

### **Application Health**
- [ ] App loads successfully at https://{self.deployment_config['domain']}
- [ ] Admin panel accessible at https://{self.deployment_config['domain']}/admin/
- [ ] API endpoints responding at https://{self.deployment_config['domain']}/api/v1/
- [ ] Static files loading correctly (CSS, JS, images)
- [ ] No 500 errors in Heroku logs

### **Payment System**
- [ ] Paystack gateway configured with Ghana settings
- [ ] Primary currency set to GHS (Ghana Cedis)
- [ ] Mobile money options available (MTN, Vodafone, AirtelTigo)
- [ ] Test payment initialization working
- [ ] Webhook endpoint accessible

### **Database**
- [ ] All migrations applied successfully
- [ ] Paystack gateway created in database
- [ ] Sample data populated if needed
- [ ] Superuser account created and accessible

---

## 🔔 **WEBHOOK CONFIGURATION (Next 1 hour)**

### **Paystack Dashboard Setup**
- [ ] Login to Paystack dashboard
- [ ] Navigate to Settings → Webhooks
- [ ] Add webhook URL: https://{self.deployment_config['domain']}/api/v1/payments/webhook/paystack/
- [ ] Select events: charge.success, charge.failed, transfer.success, transfer.failed
- [ ] Copy webhook secret
- [ ] Configure secret using enhanced_webhook_management.py

### **Webhook Testing**
- [ ] Webhook endpoint returns 200 OK
- [ ] Signature verification working
- [ ] Test webhook events processing correctly
- [ ] Ghana payment scenarios tested

---

## 🧪 **GHANA PAYMENT TESTING (Next 2 hours)**

### **Mobile Money Testing**
- [ ] MTN Mobile Money test payment (GHS 50-200)
- [ ] Vodafone Cash test payment (GHS 100-300)
- [ ] AirtelTigo Money test payment (GHS 75-250)
- [ ] Payment success webhooks received
- [ ] Transaction records created in database

### **Card Payment Testing**
- [ ] Test with Paystack test cards
- [ ] Visa card payment (GHS 150)
- [ ] Mastercard payment (GHS 300)
- [ ] Payment failure scenarios
- [ ] Refund processing if applicable

### **Bank Transfer Testing**
- [ ] Bank transfer initiation working
- [ ] Ghana bank options available
- [ ] Transfer status tracking
- [ ] Settlement notifications

---

## 🇬🇭 **GHANA MARKET READINESS (Next 4 hours)**

### **Regional Configuration**
- [ ] All 10 Ghana regions available in system
- [ ] Ashanti Region set as pilot launch area
- [ ] Northern Region configured for expansion
- [ ] Regional delivery addresses working

### **Agricultural Features**
- [ ] Crop seasons configured (Major, Minor, Dry)
- [ ] Farmer profiles creation working
- [ ] Agricultural product categories loaded
- [ ] Cooperative payment options available

### **Language and Localization**
- [ ] English (Ghana) language set
- [ ] Ghana Cedis currency formatting
- [ ] Local phone number formats (+233)
- [ ] Ghana timezone (Africa/Accra)

---

## 📊 **MONITORING SETUP (Next 1 hour)**

### **Application Monitoring**
- [ ] Heroku metrics dashboard configured
- [ ] Error tracking enabled (Sentry/Rollbar)
- [ ] Performance monitoring setup
- [ ] Uptime monitoring configured

### **Payment Monitoring**
- [ ] Transaction success rates tracking
- [ ] Payment method performance metrics
- [ ] Mobile money conversion rates
- [ ] Failed payment alerting

---

## 🚀 **LAUNCH PREPARATION (Next 24 hours)**

### **Content and Communication**
- [ ] Landing page content for Ghana farmers
- [ ] Payment method explanations in local context
- [ ] Farmer onboarding flow tested
- [ ] Support contact information updated

### **Partner Integration**
- [ ] MTN Mobile Money partnership confirmed
- [ ] Agricultural suppliers onboarded
- [ ] COCOBOD partnership discussions initiated
- [ ] Local farmer cooperatives contacted

### **Marketing and Launch**
- [ ] Ashanti Region pilot announcement prepared
- [ ] Farmer education materials ready
- [ ] Social media accounts set up
- [ ] Launch event planning initiated

---

## ✅ **LAUNCH READINESS CRITERIA**

**Technical (Must Have)**
- ✅ 99%+ uptime for 48 hours
- ✅ <2 second average response time
- ✅ Zero critical errors in production
- ✅ All payment methods functional

**Business (Must Have)**
- ✅ 10+ agricultural suppliers onboarded
- ✅ 100+ test transactions completed successfully
- ✅ Mobile money integration verified
- ✅ Ghana regulatory requirements met

**Market (Should Have)**
- ✅ 3+ farmer cooperatives interested
- ✅ Local media coverage secured
- ✅ Government agriculture ministry contacted
- ✅ Launch event planned in Kumasi

---

## 📞 **SUPPORT CONTACTS**

- **Technical Support**: tech@agriconnect-ghana.com
- **Payment Issues**: payments@agriconnect-ghana.com  
- **Ghana Operations**: ghana@agriconnect-ghana.com
- **Emergency**: +233-XXX-XXX-XXX

---

**Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}**
**Deployment Target: {self.deployment_config['domain']}**
**Environment: {self.deployment_config['environment'].title()}**
"""
        
        with open(self.project_root / 'POST_DEPLOYMENT_CHECKLIST.md', 'w') as f:
            f.write(checklist)
        
        print("✅ Post-deployment checklist created")
        
        return True

def main():
    """Main deployment automation workflow"""
    
    print("🇬🇭 AGRICONNECT GHANA - AUTOMATED PRODUCTION DEPLOYMENT")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("🚀 Complete Production Deployment Automation")
    print("=" * 70)
    
    deployer = GhanaProductionDeployer()
    
    # Step 1: Check prerequisites
    prereqs_ok, checks = deployer.check_prerequisites()
    
    if not prereqs_ok:
        print(f"\n❌ Prerequisites not met. Please install missing components.")
        return False
    
    # Step 2: Gather configuration
    config_ok = deployer.gather_deployment_config()
    
    if not config_ok:
        print(f"\n❌ Configuration gathering failed.")
        return False
    
    # Step 3: Create deployment files
    files_ok = deployer.create_deployment_files()
    
    if not files_ok:
        print(f"\n❌ Deployment file creation failed.")
        return False
    
    # Step 4: Generate deployment script
    script_ok = deployer.generate_deployment_script()
    
    if not script_ok:
        print(f"\n❌ Deployment script generation failed.")
        return False
    
    # Step 5: Create post-deployment checklist
    checklist_ok = deployer.create_post_deployment_checklist()
    
    if not checklist_ok:
        print(f"\n❌ Checklist creation failed.")
        return False
    
    # Final summary
    print(f"\n" + "=" * 70)
    print(f"🎉 AUTOMATED DEPLOYMENT PREPARATION COMPLETE")
    print(f"=" * 70)
    
    print(f"✅ Prerequisites: All requirements met")
    print(f"✅ Configuration: Ghana settings applied")
    print(f"✅ Deployment Files: Created for {deployer.deployment_config['environment']}")
    print(f"✅ Deployment Script: Generated (deploy_ghana.sh)")
    print(f"✅ Checklist: Post-deployment verification ready")
    
    print(f"\n🇬🇭 GHANA DEPLOYMENT SUMMARY:")
    print(f"   • App Name: {deployer.deployment_config['app_name']}")
    print(f"   • Domain: {deployer.deployment_config['domain']}")
    print(f"   • Environment: {deployer.deployment_config['environment'].title()}")
    print(f"   • Currency: Ghana Cedis (GHS)")
    print(f"   • Mobile Money: MTN, Vodafone, AirtelTigo")
    
    print(f"\n🚀 DEPLOYMENT COMMANDS:")
    if os.name == 'nt':  # Windows
        print(f"   PowerShell: .\\deploy_ghana.ps1")
        print(f"   Or run individual heroku commands manually")
    else:  # Unix-like
        print(f"   Bash: ./deploy_ghana.sh")
        print(f"   Make executable: chmod +x deploy_ghana.sh")
    
    print(f"\n📋 POST-DEPLOYMENT:")
    print(f"   1. Run deployment script")
    print(f"   2. Follow POST_DEPLOYMENT_CHECKLIST.md")
    print(f"   3. Configure webhook using enhanced_webhook_management.py")
    print(f"   4. Test Ghana payment methods")
    print(f"   5. Begin farmer onboarding")
    
    print(f"\n🔗 IMPORTANT URLS:")
    print(f"   App: https://{deployer.deployment_config['domain']}")
    print(f"   Admin: https://{deployer.deployment_config['domain']}/admin/")
    print(f"   API: https://{deployer.deployment_config['domain']}/api/v1/")
    print(f"   Webhook: https://{deployer.deployment_config['domain']}/api/v1/payments/webhook/paystack/")
    
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🎯 DEPLOYMENT AUTOMATION: COMPLETE!")
        print(f"🚀 Ready to deploy AgriConnect Ghana to production")
    else:
        print(f"\n⚠️  DEPLOYMENT PREPARATION: FAILED")
        print(f"🔧 Please resolve issues and try again")
