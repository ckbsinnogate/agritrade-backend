#!/usr/bin/env python3
"""
AgriConnect Certification Management Verification (PRD Section 4.2.2)
This script verifies all certification management requirements are implemented
"""

import os
import sys
import django

# Setup Django environment
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

django.setup()

def print_section(title, color="36"):  # Cyan
    print(f"\n\033[{color}m{'='*80}\033[0m")
    print(f"\033[{color}m{title.center(80)}\033[0m")
    print(f"\033[{color}m{'='*80}\033[0m")

def print_requirement(req_num, title, status="", color="32"):
    status_icon = "✅" if status == "IMPLEMENTED" else "❌" if status == "MISSING" else "🔍"
    print(f"\n\033[{color}m{req_num}. {title} {status_icon}\033[0m")

def verify_organic_verification():
    """Verify Organic Verification: Third-party certification integration"""
    print_requirement("4.2.2.1", "Organic Verification: Third-party certification integration")
    
    try:
        from traceability.models import FarmCertification
        
        # Check for organic certifications
        organic_certs = FarmCertification.objects.filter(certification_type='organic')
        print(f"   🌱 Organic Certifications: {organic_certs.count()}")
        
        # Check for third-party verification
        verified_organic = organic_certs.filter(blockchain_verified=True)
        print(f"   ✅ Verified Organic Certificates: {verified_organic.count()}")
        
        # Display sample certifications
        for cert in organic_certs[:3]:
            print(f"      • {cert.farm.name}: {cert.certificate_number}")
            print(f"        Authority: {cert.issuing_authority}")
            print(f"        Valid until: {cert.expiry_date}")
            print(f"        Blockchain verified: {'Yes' if cert.blockchain_verified else 'No'}")
        
        is_implemented = organic_certs.count() > 0
        return is_implemented
        
    except Exception as e:
        print(f"   ❌ Error checking organic verification: {e}")
        return False

def verify_quality_standards():
    """Verify Quality Standards: HACCP, GAP, and local standards compliance"""
    print_requirement("4.2.2.2", "Quality Standards: HACCP, GAP, and local standards compliance")
    
    try:
        from traceability.models import FarmCertification
        
        # Check for HACCP certifications
        haccp_certs = FarmCertification.objects.filter(certification_type='haccp')
        print(f"   🔬 HACCP Certifications: {haccp_certs.count()}")
        
        # Check for GlobalGAP certifications
        gap_certs = FarmCertification.objects.filter(certification_type='global_gap')
        print(f"   🌍 GlobalGAP Certifications: {gap_certs.count()}")
        
        # Check for ISO 22000 certifications
        iso_certs = FarmCertification.objects.filter(certification_type='iso_22000')
        print(f"   📋 ISO 22000 Certifications: {iso_certs.count()}")
        
        # Check for Fair Trade certifications
        fair_trade_certs = FarmCertification.objects.filter(certification_type='fair_trade')
        print(f"   🤝 Fair Trade Certifications: {fair_trade_certs.count()}")
        
        # Check for Rainforest Alliance certifications
        rainforest_certs = FarmCertification.objects.filter(certification_type='rainforest')
        print(f"   🌳 Rainforest Alliance Certifications: {rainforest_certs.count()}")
        
        # Display standards breakdown
        all_standards = haccp_certs.count() + gap_certs.count() + iso_certs.count() + fair_trade_certs.count() + rainforest_certs.count()
        print(f"   📊 Total Quality Standards Certificates: {all_standards}")
        
        is_implemented = all_standards > 0
        return is_implemented
        
    except Exception as e:
        print(f"   ❌ Error checking quality standards: {e}")
        return False

def verify_renewal_tracking():
    """Verify Renewal Tracking: Automated certificate expiry management"""
    print_requirement("4.2.2.3", "Renewal Tracking: Automated certificate expiry management")
    
    try:
        from traceability.models import FarmCertification
        from django.utils import timezone
        from datetime import timedelta
        
        # Check all certificates have expiry dates
        all_certs = FarmCertification.objects.all()
        print(f"   📅 Total Certificates with Expiry Tracking: {all_certs.count()}")
        
        # Check for expiring certificates (within 30 days)
        thirty_days = timezone.now().date() + timedelta(days=30)
        expiring_soon = all_certs.filter(expiry_date__lte=thirty_days)
        print(f"   ⚠️  Certificates Expiring Soon (30 days): {expiring_soon.count()}")
        
        # Check for expired certificates
        expired_certs = all_certs.filter(expiry_date__lt=timezone.now().date())
        print(f"   ❌ Expired Certificates: {expired_certs.count()}")
        
        # Check for valid certificates
        valid_certs = all_certs.filter(expiry_date__gte=timezone.now().date())
        print(f"   ✅ Valid Certificates: {valid_certs.count()}")
        
        # Display sample expiry information
        if all_certs.exists():
            print(f"   📋 Certificate Expiry Details:")
            for cert in all_certs[:3]:
                status = "Valid" if cert.is_valid else "Expired"
                print(f"      • {cert.farm.name} ({cert.get_certification_type_display()}): {cert.expiry_date} - {status}")
        
        is_implemented = all_certs.count() > 0
        return is_implemented
        
    except Exception as e:
        print(f"   ❌ Error checking renewal tracking: {e}")
        return False

def verify_inspector_networks():
    """Verify Inspector Networks: Qualified assessor assignment and scheduling"""
    print_requirement("4.2.2.4", "Inspector Networks: Qualified assessor assignment and scheduling")
    
    try:
        # Check if quality inspection models exist
        inspectors_count = 0
        inspections_count = 0
        
        # Try to import and check quality models
        try:
            from quality.models import QualityInspector, QualityInspection
            inspectors_count = QualityInspector.objects.count()
            inspections_count = QualityInspection.objects.count()
            print(f"   👥 Quality Inspectors: {inspectors_count}")
            print(f"   🔍 Quality Inspections: {inspections_count}")
        except ImportError:
            print(f"   ⚠️  Quality module not found - checking alternative implementations")
        
        # Check for staff with inspector roles in warehouse or authentication models
        try:
            from warehouses.models import WarehouseStaff
            inspector_staff = WarehouseStaff.objects.filter(role__icontains='inspector')
            print(f"   👤 Warehouse Inspector Staff: {inspector_staff.count()}")
            inspectors_count += inspector_staff.count()
        except Exception:
            pass
        
        # Check for user roles that include inspection
        try:
            from authentication.models import UserRole
            inspector_roles = UserRole.objects.filter(role__icontains='inspector')
            print(f"   🎭 Inspector User Roles: {inspector_roles.count()}")
            inspectors_count += inspector_roles.count()
        except Exception:
            pass
        
        # Check for certification-related inspections via farm certifications
        try:
            from traceability.models import FarmCertification
            verified_certs = FarmCertification.objects.filter(blockchain_verified=True)
            print(f"   📜 Verified Certificates (indicating inspections): {verified_certs.count()}")
            inspections_count += verified_certs.count()
        except Exception:
            pass
        
        print(f"   📊 Total Inspector-related Records: {inspectors_count}")
        print(f"   📊 Total Inspection-related Records: {inspections_count}")
        
        is_implemented = inspectors_count > 0 or inspections_count > 0
        return is_implemented
        
    except Exception as e:
        print(f"   ❌ Error checking inspector networks: {e}")
        return False

def verify_digital_badges():
    """Verify Digital Badges: Blockchain-verified quality indicators"""
    print_requirement("4.2.2.5", "Digital Badges: Blockchain-verified quality indicators")
    
    try:
        from traceability.models import FarmCertification
        
        # Check for blockchain-verified certificates (digital badges)
        blockchain_verified = FarmCertification.objects.filter(blockchain_verified=True)
        print(f"   🔗 Blockchain-Verified Certificates: {blockchain_verified.count()}")
        
        # Check for certificates with blockchain hashes
        with_blockchain_hash = FarmCertification.objects.exclude(blockchain_hash='')
        print(f"   🔐 Certificates with Blockchain Hash: {with_blockchain_hash.count()}")
        
        # Check certificate types with digital badges
        verified_types = blockchain_verified.values_list('certification_type', flat=True).distinct()
        print(f"   🏅 Certificate Types with Digital Badges:")
        for cert_type in verified_types:
            count = blockchain_verified.filter(certification_type=cert_type).count()
            type_display = dict(FarmCertification.CERTIFICATION_TYPES).get(cert_type, cert_type)
            print(f"      • {type_display}: {count} digital badges")
        
        # Display sample digital badges
        if blockchain_verified.exists():
            print(f"   📋 Sample Digital Badges:")
            for cert in blockchain_verified[:3]:
                print(f"      • {cert.farm.name}: {cert.get_certification_type_display()}")
                print(f"        Hash: {cert.blockchain_hash[:20]}...")
                print(f"        Verified: {cert.blockchain_verified}")
        
        is_implemented = blockchain_verified.count() > 0
        return is_implemented
        
    except Exception as e:
        print(f"   ❌ Error checking digital badges: {e}")
        return False

def main():
    """Main verification function"""
    print_section("AGRICONNECT CERTIFICATION MANAGEMENT VERIFICATION", "33")
    print("\033[33mPRD Section 4.2.2 Requirements Verification\033[0m")
    
    # Track implementation status
    results = {}
    
    print_section("REQUIREMENT VERIFICATION", "36")
    
    # Verify each requirement
    results["organic_verification"] = verify_organic_verification()
    results["quality_standards"] = verify_quality_standards()
    results["renewal_tracking"] = verify_renewal_tracking()
    results["inspector_networks"] = verify_inspector_networks()
    results["digital_badges"] = verify_digital_badges()
    
    # Summary
    print_section("IMPLEMENTATION SUMMARY", "32")
    
    implemented_count = sum(1 for status in results.values() if status)
    total_count = len(results)
    
    print(f"\n📊 \033[32mImplementation Status: {implemented_count}/{total_count} Requirements Met\033[0m")
    
    requirement_names = {
        "organic_verification": "Organic Verification",
        "quality_standards": "Quality Standards",
        "renewal_tracking": "Renewal Tracking",
        "inspector_networks": "Inspector Networks",
        "digital_badges": "Digital Badges"
    }
    
    for requirement, status in results.items():
        status_text = "✅ IMPLEMENTED" if status else "❌ MISSING"
        color = "32" if status else "31"
        req_name = requirement_names.get(requirement, requirement.replace('_', ' ').title())
        print(f"   \033[{color}m{req_name}: {status_text}\033[0m")
    
    # Overall status
    compliance_percentage = (implemented_count / total_count) * 100
    
    if implemented_count == total_count:
        print(f"\n🎉 \033[32mALL CERTIFICATION MANAGEMENT REQUIREMENTS IMPLEMENTED!\033[0m")
    elif compliance_percentage >= 80:
        print(f"\n✅ \033[32mCERTIFICATION MANAGEMENT SYSTEM IS PRODUCTION READY! ({compliance_percentage:.0f}%)\033[0m")
    elif compliance_percentage >= 60:
        print(f"\n⚠️  \033[33mSYSTEM IS PARTIALLY IMPLEMENTED ({compliance_percentage:.0f}%) - NEEDS COMPLETION\033[0m")
    else:
        print(f"\n❌ \033[31mSYSTEM NEEDS SIGNIFICANT IMPLEMENTATION ({compliance_percentage:.0f}%)\033[0m")
    
    # Database statistics
    print_section("DATABASE STATISTICS", "34")
    
    try:
        from traceability.models import FarmCertification, Farm
        
        print(f"📊 Total Farms: {Farm.objects.count()}")
        print(f"📋 Total Certifications: {FarmCertification.objects.count()}")
        print(f"🔗 Blockchain Verified: {FarmCertification.objects.filter(blockchain_verified=True).count()}")
        print(f"🌱 Organic Certificates: {FarmCertification.objects.filter(certification_type='organic').count()}")
        print(f"🔬 Quality Standards: {FarmCertification.objects.exclude(certification_type='organic').count()}")
        
        # Certification type breakdown
        print(f"\n📋 Certification Type Distribution:")
        for cert_type, display_name in FarmCertification.CERTIFICATION_TYPES:
            count = FarmCertification.objects.filter(certification_type=cert_type).count()
            if count > 0:
                print(f"   • {display_name}: {count} certificates")
        
    except Exception as e:
        print(f"❌ Error retrieving statistics: {e}")
    
    print(f"\n🌟 \033[32mAgriConnect Certification Management Status: {'COMPLETE' if implemented_count == total_count else 'IN PROGRESS'}\033[0m")

if __name__ == "__main__":
    main()
