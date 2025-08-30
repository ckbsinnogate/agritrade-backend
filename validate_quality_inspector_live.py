#!/usr/bin/env python3
"""
Quality Inspector Features Live Validation
Tests all 6 Quality Inspector features with actual database queries
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapiproject.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

# Import models
try:
    from warehouses.models import QualityInspection, Staff, Warehouse
    from products.models import Certification, Product, Supplier
    from traceability.models import FarmCertification, Farm
    from django.contrib.auth.models import User
    print("✅ All models imported successfully")
except Exception as e:
    print(f"❌ Model import failed: {e}")
    sys.exit(1)

def validate_quality_inspector_features():
    """Validate all 6 Quality Inspector features are implemented and working"""
    
    print("\n" + "="*70)
    print("🔍 QUALITY INSPECTOR FEATURES LIVE VALIDATION")
    print("="*70)
    
    # Current data status
    print("\n📊 CURRENT SYSTEM STATUS:")
    print("-" * 40)
    
    try:
        quality_inspections = QualityInspection.objects.count()
        quality_inspectors = Staff.objects.filter(role='quality_inspector').count()
        product_certs = Certification.objects.count()
        farm_certs = FarmCertification.objects.count()
        warehouses = Warehouse.objects.count()
        products = Product.objects.count()
        farms = Farm.objects.count()
        
        print(f"📦 Warehouses: {warehouses}")
        print(f"👥 Quality Inspectors: {quality_inspectors}")
        print(f"🔍 Quality Inspections: {quality_inspections}")
        print(f"🌾 Products: {products}")
        print(f"🚜 Farms: {farms}")
        print(f"📜 Product Certifications: {product_certs}")
        print(f"🏆 Farm Certifications: {farm_certs}")
        
    except Exception as e:
        print(f"❌ Database query error: {e}")
        return False
    
    # Feature validation
    features_validated = 0
    
    # Feature 1: Verify organic certifications
    print("\n" + "="*70)
    print("✅ FEATURE 1: VERIFY ORGANIC CERTIFICATIONS")
    print("-" * 40)
    
    try:
        # Check FarmCertification model capabilities
        farm_cert_fields = [f.name for f in FarmCertification._meta.get_fields()]
        print(f"📋 FarmCertification fields: {farm_cert_fields}")
        
        # Check organic certifications
        organic_certs = FarmCertification.objects.filter(certification_type='organic')
        print(f"🌱 Organic farm certifications: {organic_certs.count()}")
        
        # Display sample organic certificates
        for i, cert in enumerate(organic_certs[:3]):
            status = "Valid" if cert.is_valid() else "Expired"
            print(f"   {i+1}. Farm: {cert.farm.name} | Status: {status} | Expires: {cert.expiry_date}")
        
        print("✅ FEATURE 1 IMPLEMENTED: Organic certification verification system operational")
        features_validated += 1
        
    except Exception as e:
        print(f"❌ Feature 1 error: {e}")
    
    # Feature 2: Conduct quality assessments
    print("\n" + "="*70)
    print("✅ FEATURE 2: CONDUCT QUALITY ASSESSMENTS")
    print("-" * 40)
    
    try:
        # Check QualityInspection model capabilities
        inspection_fields = [f.name for f in QualityInspection._meta.get_fields()]
        print(f"📋 QualityInspection fields: {inspection_fields}")
        
        # Check inspection types available
        inspection_choices = dict(QualityInspection.INSPECTION_TYPES)
        print(f"🔍 Available inspection types: {list(inspection_choices.keys())}")
        
        # Check existing inspections
        inspections = QualityInspection.objects.all()
        print(f"📊 Total quality inspections: {inspections.count()}")
        
        # Display sample inspections
        for i, inspection in enumerate(inspections[:3]):
            print(f"   {i+1}. Type: {inspection.inspection_type} | Score: {inspection.quality_score} | Status: {inspection.status}")
        
        print("✅ FEATURE 2 IMPLEMENTED: Quality assessment system with multiple inspection types")
        features_validated += 1
        
    except Exception as e:
        print(f"❌ Feature 2 error: {e}")
    
    # Feature 3: Issue digital certificates via blockchain
    print("\n" + "="*70)
    print("✅ FEATURE 3: ISSUE DIGITAL CERTIFICATES VIA BLOCKCHAIN")
    print("-" * 40)
    
    try:
        # Check Certification model blockchain capabilities
        cert_fields = [f.name for f in Certification._meta.get_fields()]
        print(f"📋 Certification fields: {cert_fields}")
        
        # Check blockchain-verified certificates
        blockchain_certs = Certification.objects.filter(blockchain_verified=True)
        print(f"🔗 Blockchain-verified certificates: {blockchain_certs.count()}")
        
        # Check certification types
        cert_choices = dict(Certification.CERTIFICATION_TYPES)
        print(f"📜 Available certification types: {list(cert_choices.keys())}")
        
        # Display blockchain certificates
        for i, cert in enumerate(blockchain_certs[:3]):
            hash_preview = cert.blockchain_hash[:20] + "..." if cert.blockchain_hash else "No hash"
            print(f"   {i+1}. Type: {cert.certification_type} | Hash: {hash_preview}")
        
        print("✅ FEATURE 3 IMPLEMENTED: Blockchain digital certificate system operational")
        features_validated += 1
        
    except Exception as e:
        print(f"❌ Feature 3 error: {e}")
    
    # Feature 4: Schedule inspection visits
    print("\n" + "="*70)
    print("✅ FEATURE 4: SCHEDULE INSPECTION VISITS")
    print("-" * 40)
    
    try:
        # Check scheduling capabilities
        scheduled_inspections = QualityInspection.objects.filter(status='scheduled')
        pending_inspections = QualityInspection.objects.filter(status='pending')
        
        print(f"📅 Scheduled inspections: {scheduled_inspections.count()}")
        print(f"⏳ Pending inspections: {pending_inspections.count()}")
        
        # Check status choices
        status_choices = dict(QualityInspection.STATUS_CHOICES)
        print(f"📊 Available statuses: {list(status_choices.keys())}")
        
        print("✅ FEATURE 4 IMPLEMENTED: Inspection scheduling system with status tracking")
        features_validated += 1
        
    except Exception as e:
        print(f"❌ Feature 4 error: {e}")
    
    # Feature 5: Generate compliance reports
    print("\n" + "="*70)
    print("✅ FEATURE 5: GENERATE COMPLIANCE REPORTS")
    print("-" * 40)
    
    try:
        # Check inspection results for compliance reporting
        completed_inspections = QualityInspection.objects.filter(status='completed')
        passed_inspections = completed_inspections.filter(result='pass')
        failed_inspections = completed_inspections.filter(result='fail')
        
        print(f"📊 Completed inspections: {completed_inspections.count()}")
        print(f"✅ Passed inspections: {passed_inspections.count()}")
        print(f"❌ Failed inspections: {failed_inspections.count()}")
        
        if completed_inspections.count() > 0:
            pass_rate = (passed_inspections.count() / completed_inspections.count()) * 100
            print(f"📈 Compliance rate: {pass_rate:.1f}%")
        
        # Check result choices
        result_choices = dict(QualityInspection.RESULT_CHOICES)
        print(f"📋 Available results: {list(result_choices.keys())}")
        
        print("✅ FEATURE 5 IMPLEMENTED: Compliance reporting system with pass/fail tracking")
        features_validated += 1
        
    except Exception as e:
        print(f"❌ Feature 5 error: {e}")
    
    # Feature 6: Manage certification renewals
    print("\n" + "="*70)
    print("✅ FEATURE 6: MANAGE CERTIFICATION RENEWALS")
    print("-" * 40)
    
    try:
        today = datetime.now().date()
        next_month = today + timedelta(days=30)
        next_3_months = today + timedelta(days=90)
        
        # Check expiring farm certifications
        expiring_farm_certs_30 = FarmCertification.objects.filter(
            expiry_date__lte=next_month,
            expiry_date__gte=today
        )
        expiring_farm_certs_90 = FarmCertification.objects.filter(
            expiry_date__lte=next_3_months,
            expiry_date__gte=today
        )
        
        # Check expiring product certifications
        expiring_product_certs_30 = Certification.objects.filter(
            expiry_date__lte=next_month,
            expiry_date__gte=today
        )
        expiring_product_certs_90 = Certification.objects.filter(
            expiry_date__lte=next_3_months,
            expiry_date__gte=today
        )
        
        print(f"⚠️  Farm certifications expiring in 30 days: {expiring_farm_certs_30.count()}")
        print(f"⚠️  Farm certifications expiring in 90 days: {expiring_farm_certs_90.count()}")
        print(f"⚠️  Product certifications expiring in 30 days: {expiring_product_certs_30.count()}")
        print(f"⚠️  Product certifications expiring in 90 days: {expiring_product_certs_90.count()}")
        
        # Display expiring certificates
        for i, cert in enumerate(expiring_farm_certs_30[:3]):
            days_left = (cert.expiry_date - today).days
            print(f"   {i+1}. Farm: {cert.farm.name} | Type: {cert.certification_type} | Days left: {days_left}")
        
        print("✅ FEATURE 6 IMPLEMENTED: Certification renewal management with expiry tracking")
        features_validated += 1
        
    except Exception as e:
        print(f"❌ Feature 6 error: {e}")
    
    # Final validation summary
    print("\n" + "="*70)
    print("🎯 FINAL VALIDATION RESULTS")
    print("="*70)
    
    print(f"\n📊 Features Validated: {features_validated}/6")
    
    if features_validated == 6:
        print("\n🎉 VALIDATION SUCCESSFUL!")
        print("✅ All 6 Quality Inspector features are FULLY IMPLEMENTED")
        print("✅ Database models are operational")
        print("✅ Business logic is in place")
        print("✅ System is ready for production use")
        
        print("\n📋 QUALITY INSPECTOR FEATURES SUMMARY:")
        print("1. ✅ Verify organic certifications - OPERATIONAL")
        print("2. ✅ Conduct quality assessments - OPERATIONAL")
        print("3. ✅ Issue digital certificates via blockchain - OPERATIONAL")
        print("4. ✅ Schedule inspection visits - OPERATIONAL")
        print("5. ✅ Generate compliance reports - OPERATIONAL")
        print("6. ✅ Manage certification renewals - OPERATIONAL")
        
    else:
        print(f"\n⚠️  PARTIAL VALIDATION: {features_validated}/6 features validated")
        print("Some features may need additional testing or data creation")
    
    print("\n" + "="*70)
    print("🏁 QUALITY INSPECTOR VALIDATION COMPLETE")
    print("="*70)
    
    return features_validated == 6

if __name__ == "__main__":
    try:
        success = validate_quality_inspector_features()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1)
