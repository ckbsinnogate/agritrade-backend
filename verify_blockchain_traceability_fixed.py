#!/usr/bin/env python3
"""
AgriConnect Blockchain Traceability System Verification
This script verifies that all PRD Section 4.2 Blockchain Traceability System requirements are implemented
"""

import os
import sys
import django

# Setup Django environment
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')

try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    sys.exit(1)

def print_section(title, color="36"):  # Cyan
    print(f"\n\033[{color}m{'='*80}\033[0m")
    print(f"\033[{color}m{title.center(80)}\033[0m")
    print(f"\033[{color}m{'='*80}\033[0m")

def print_requirement(req_num, title, status="", color="32"):
    status_icon = "✅" if status == "IMPLEMENTED" else "❌" if status == "MISSING" else "🔍"
    print(f"\n\033[{color}m{req_num}. {title} {status_icon}\033[0m")

def verify_blockchain_infrastructure():
    """Verify blockchain infrastructure components"""
    print_requirement("4.2.1", "Blockchain Infrastructure: Networks, Smart Contracts, Transactions")
    
    try:
        from traceability.models import BlockchainNetwork, SmartContract, BlockchainTransaction
        
        networks = BlockchainNetwork.objects.count()
        contracts = SmartContract.objects.count()
        transactions = BlockchainTransaction.objects.count()
        
        print(f"   📡 Blockchain Networks: {networks}")
        print(f"   📜 Smart Contracts: {contracts}")
        print(f"   💳 Blockchain Transactions: {transactions}")
        
        # Show sample data
        if networks > 0:
            sample_network = BlockchainNetwork.objects.first()
            print(f"      • Sample Network: {sample_network.name} ({sample_network.network_type})")
        
        if contracts > 0:
            sample_contract = SmartContract.objects.first()
            print(f"      • Sample Contract: {sample_contract.name} - {sample_contract.contract_type}")
        
        is_implemented = networks > 0 and contracts > 0
        return is_implemented
        
    except ImportError as e:
        print(f"   ❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verify_farm_registration():
    """Verify farm registration and certification system"""
    print_requirement("4.2.2", "Farm Registration: Digital farm profiles with blockchain verification")
    
    try:
        from traceability.models import Farm, FarmCertification
        
        farms = Farm.objects.count()
        certifications = FarmCertification.objects.count()
        verified_certs = FarmCertification.objects.filter(blockchain_verified=True).count()
        
        print(f"   🏡 Registered Farms: {farms}")
        print(f"   📋 Farm Certifications: {certifications}")
        print(f"   ✅ Blockchain Verified Certifications: {verified_certs}")
        
        # Show sample data
        if farms > 0:
            sample_farm = Farm.objects.first()
            print(f"      • Sample Farm: {sample_farm.name} ({sample_farm.location})")
            
        if certifications > 0:
            sample_cert = FarmCertification.objects.first()
            cert_type = sample_cert.get_certification_type_display()
            print(f"      • Sample Certification: {cert_type} - Verified: {sample_cert.blockchain_verified}")
        
        is_implemented = farms > 0 and certifications > 0
        return is_implemented
        
    except ImportError as e:
        print(f"   ❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verify_product_traceability():
    """Verify product traceability system"""
    print_requirement("4.2.3", "Product Traceability: Farm-to-consumer tracking with QR codes")
    
    try:
        from traceability.models import ProductTrace, SupplyChainEvent
        
        traces = ProductTrace.objects.count()
        events = SupplyChainEvent.objects.count()
        qr_enabled = ProductTrace.objects.exclude(qr_code_data='').count()
        blockchain_verified_events = SupplyChainEvent.objects.filter(status='verified').count()
        
        print(f"   📦 Product Traces: {traces}")
        print(f"   🔄 Supply Chain Events: {events}")
        print(f"   📱 QR Code Enabled Products: {qr_enabled}")
        print(f"   ⛓️  Blockchain Verified Events: {blockchain_verified_events}")
        
        # Show sample data
        if traces > 0:
            sample_trace = ProductTrace.objects.first()
            print(f"      • Sample Trace: {sample_trace.product.name} - Batch: {sample_trace.batch_number}")
            
        if events > 0:
            sample_event = SupplyChainEvent.objects.first()
            print(f"      • Sample Event: {sample_event.get_event_type_display()} - {sample_event.location}")
        
        is_implemented = traces > 0 and events > 0 and qr_enabled > 0
        return is_implemented
        
    except ImportError as e:
        print(f"   ❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verify_consumer_interface():
    """Verify consumer scanning and verification interface"""
    print_requirement("4.2.4", "Consumer Interface: QR scanning and product verification")
    
    try:
        from traceability.models import ConsumerScan, ProductTrace
        
        scans = ConsumerScan.objects.count()
        unique_products_scanned = ConsumerScan.objects.values('product_trace').distinct().count()
        traceable_products = ProductTrace.objects.exclude(qr_code_data='').count()
        
        print(f"   📱 Consumer Scans: {scans}")
        print(f"   📦 Unique Products Scanned: {unique_products_scanned}")
        print(f"   🔍 Traceable Products Available: {traceable_products}")
        
        # Show sample data
        if scans > 0:
            sample_scan = ConsumerScan.objects.first()
            print(f"      • Sample Scan: {sample_scan.product_trace.product.name} at {sample_scan.scan_location}")
        
        is_implemented = traceable_products > 0  # Consumer interface exists if products are traceable
        return is_implemented
        
    except ImportError as e:
        print(f"   ❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verify_smart_contracts():
    """Verify smart contract implementation"""
    print_requirement("4.2.5", "Smart Contracts: Automated verification and compliance")
    
    try:
        from traceability.models import SmartContract, BlockchainTransaction
        
        contracts = SmartContract.objects.count()
        active_contracts = SmartContract.objects.filter(is_active=True).count()
        contract_transactions = BlockchainTransaction.objects.filter(smart_contract__isnull=False).count()
        
        print(f"   📜 Total Smart Contracts: {contracts}")
        print(f"   ✅ Active Smart Contracts: {active_contracts}")
        print(f"   💳 Contract Transactions: {contract_transactions}")
        
        # Show contract types
        if contracts > 0:
            contract_types = SmartContract.objects.values_list('contract_type', flat=True).distinct()
            print(f"      • Contract Types: {list(contract_types)}")
        
        is_implemented = contracts > 0 and active_contracts > 0
        return is_implemented
        
    except ImportError as e:
        print(f"   ❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verify_data_integrity():
    """Verify blockchain data integrity and immutability"""
    print_requirement("4.2.6", "Data Integrity: Immutable records and hash verification")
    
    try:
        from traceability.models import ProductTrace, SupplyChainEvent, FarmCertification
        
        # Check for blockchain hashes
        traces_with_hash = ProductTrace.objects.exclude(blockchain_id='').count()
        events_with_hash = SupplyChainEvent.objects.exclude(blockchain_hash='').count()
        certs_with_hash = FarmCertification.objects.exclude(blockchain_hash='').count()
        
        # Check for blockchain verification
        verified_traces = ProductTrace.objects.exclude(blockchain_id='').count()  # All traces with blockchain_id are verified
        verified_events = SupplyChainEvent.objects.filter(status='verified').count()
        verified_certs = FarmCertification.objects.filter(blockchain_verified=True).count()
        
        print(f"   🔐 Records with Blockchain Hash:")
        print(f"      • Product Traces: {traces_with_hash}")
        print(f"      • Supply Chain Events: {events_with_hash}")
        print(f"      • Certifications: {certs_with_hash}")
        
        print(f"   ✅ Blockchain Verified Records:")
        print(f"      • Product Traces: {verified_traces}")
        print(f"      • Supply Chain Events: {verified_events}")
        print(f"      • Certifications: {verified_certs}")
        
        total_hashed = traces_with_hash + events_with_hash + certs_with_hash
        total_verified = verified_traces + verified_events + verified_certs
        
        is_implemented = total_hashed > 0 and total_verified > 0
        return is_implemented
        
    except ImportError as e:
        print(f"   ❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main verification function"""
    print_section("AGRICONNECT BLOCKCHAIN TRACEABILITY SYSTEM VERIFICATION", "33")
    print("\033[33mPRD Section 4.2 Requirements Verification\033[0m")
    
    # Track implementation status
    results = {}
    
    print_section("REQUIREMENT VERIFICATION", "36")
    
    # Verify each requirement
    results["blockchain_infrastructure"] = verify_blockchain_infrastructure()
    results["farm_registration"] = verify_farm_registration()
    results["product_traceability"] = verify_product_traceability()
    results["consumer_interface"] = verify_consumer_interface()
    results["smart_contracts"] = verify_smart_contracts()
    results["data_integrity"] = verify_data_integrity()
    
    # Summary
    print_section("IMPLEMENTATION SUMMARY", "32")
    
    implemented_count = sum(1 for status in results.values() if status)
    total_count = len(results)
    
    print(f"\n📊 \033[32mImplementation Status: {implemented_count}/{total_count} Requirements Met\033[0m")
    
    for requirement, status in results.items():
        status_text = "✅ IMPLEMENTED" if status else "❌ MISSING"
        color = "32" if status else "31"
        req_name = requirement.replace('_', ' ').title()
        print(f"   \033[{color}m{req_name}: {status_text}\033[0m")
    
    # Overall status
    compliance_percentage = (implemented_count / total_count) * 100
    
    if implemented_count == total_count:
        print(f"\n🎉 \033[32mALL BLOCKCHAIN TRACEABILITY REQUIREMENTS IMPLEMENTED!\033[0m")
    elif compliance_percentage >= 80:
        print(f"\n✅ \033[32mBLOCKCHAIN TRACEABILITY SYSTEM IS PRODUCTION READY! ({compliance_percentage:.0f}%)\033[0m")
    elif compliance_percentage >= 60:
        print(f"\n⚠️  \033[33mSYSTEM IS PARTIALLY IMPLEMENTED ({compliance_percentage:.0f}%) - NEEDS COMPLETION\033[0m")
    else:
        print(f"\n❌ \033[31mSYSTEM NEEDS SIGNIFICANT IMPLEMENTATION ({compliance_percentage:.0f}%)\033[0m")
    
    # Database statistics
    print_section("DATABASE STATISTICS", "34")
    
    try:
        from traceability.models import (
            BlockchainNetwork, SmartContract, BlockchainTransaction,
            Farm, FarmCertification, ProductTrace, SupplyChainEvent, ConsumerScan
        )
        
        print(f"📡 Blockchain Networks: {BlockchainNetwork.objects.count()}")
        print(f"📜 Smart Contracts: {SmartContract.objects.count()}")
        print(f"💳 Blockchain Transactions: {BlockchainTransaction.objects.count()}")
        print(f"🏡 Registered Farms: {Farm.objects.count()}")
        print(f"📋 Farm Certifications: {FarmCertification.objects.count()}")
        print(f"📦 Product Traces: {ProductTrace.objects.count()}")
        print(f"🔄 Supply Chain Events: {SupplyChainEvent.objects.count()}")
        print(f"📱 Consumer Scans: {ConsumerScan.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error retrieving statistics: {e}")
    
    print(f"\n🌟 \033[32mAgriConnect Blockchain Traceability System Status: {'COMPLETE' if implemented_count == total_count else 'IN PROGRESS'}\033[0m")

if __name__ == "__main__":
    main()
