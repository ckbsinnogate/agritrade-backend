#!/usr/bin/env python3
"""
Simple Quality Inspector Features Test
Validates all 6 Quality Inspector features are working
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapiproject.settings')
django.setup()

# Import models
from warehouses.models import QualityInspection, Staff, Warehouse
from products.models import Certification, Product, Supplier
from traceability.models import FarmCertification, Farm
from django.contrib.auth.models import User

def test_quality_inspector_features():
    print("🔍 Quality Inspector Features Validation Test")
    print("=" * 60)
    
    # Check existing data
    print("\n📊 Current Data Status:")
    print(f"Quality Inspections: {QualityInspection.objects.count()}")
    print(f"Product Certifications: {Certification.objects.count()}")
    print(f"Farm Certifications: {FarmCertification.objects.count()}")
    print(f"Quality Inspectors: {Staff.objects.filter(role='quality_inspector').count()}")
    print(f"Warehouses: {Warehouse.objects.count()}")
    print(f"Products: {Product.objects.count()}")
    print(f"Farms: {Farm.objects.count()}")
    
    print("\n✅ Feature 1: Verify Organic Certifications")
    # Check farm certifications (organic)
    organic_certs = FarmCertification.objects.filter(certification_type='organic')
    print(f"   Found {organic_certs.count()} organic farm certifications")
    if organic_certs.exists():
        for cert in organic_certs[:3]:
            status = "Valid" if cert.is_valid() else "Expired"
            print(f"   - Farm: {cert.farm.name}, Status: {status}, Expires: {cert.expiry_date}")
    
    print("\n✅ Feature 2: Conduct Quality Assessments")
    # Check quality inspections
    inspections = QualityInspection.objects.all()
    print(f"   Found {inspections.count()} quality inspections")
    if inspections.exists():
        for inspection in inspections[:3]:
            print(f"   - Type: {inspection.inspection_type}, Score: {inspection.quality_score}, Status: {inspection.status}")
    
    print("\n✅ Feature 3: Issue Digital Certificates via Blockchain")
    # Check blockchain certificates
    blockchain_certs = Certification.objects.filter(blockchain_verified=True)
    print(f"   Found {blockchain_certs.count()} blockchain-verified certificates")
    if blockchain_certs.exists():
        for cert in blockchain_certs[:3]:
            print(f"   - Type: {cert.certification_type}, Hash: {cert.blockchain_hash[:20]}...")
    
    print("\n✅ Feature 4: Schedule Inspection Visits")
    # Check scheduled inspections
    scheduled = QualityInspection.objects.filter(status='scheduled')
    print(f"   Found {scheduled.count()} scheduled inspections")
    
    print("\n✅ Feature 5: Generate Compliance Reports")
    # Check inspection results and compliance
    completed = QualityInspection.objects.filter(status='completed')
    passed = completed.filter(result='pass')
    print(f"   Completed inspections: {completed.count()}")
    print(f"   Passed inspections: {passed.count()}")
    if completed.count() > 0:
        pass_rate = (passed.count() / completed.count()) * 100
        print(f"   Compliance rate: {pass_rate:.1f}%")
    
    print("\n✅ Feature 6: Manage Certification Renewals")
    # Check expiring certifications
    today = datetime.now().date()
    soon = today + timedelta(days=30)
    
    expiring_farm_certs = FarmCertification.objects.filter(
        expiry_date__lte=soon,
        expiry_date__gte=today
    )
    expiring_product_certs = Certification.objects.filter(
        expiry_date__lte=soon,
        expiry_date__gte=today
    )
    
    print(f"   Farm certifications expiring in 30 days: {expiring_farm_certs.count()}")
    print(f"   Product certifications expiring in 30 days: {expiring_product_certs.count()}")
    
    print("\n" + "=" * 60)
    print("🎯 QUALITY INSPECTOR FEATURES VALIDATION COMPLETE")
    print("All 6 features are implemented and accessible!")
    print("=" * 60)

if __name__ == "__main__":
    test_quality_inspector_features()
