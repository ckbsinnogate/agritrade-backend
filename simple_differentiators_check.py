#!/usr/bin/env python
"""
🔍 SIMPLE DIFFERENTIATORS STATUS CHECK
Quick verification of all 7 key differentiators implementation status
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

def check_differentiator_status():
    """Check implementation status of all 7 key differentiators"""
    
    print("\n🔍 AGRICONNECT DIFFERENTIATORS STATUS CHECK")
    print("=" * 60)
    
    differentiators = {}
    
    # 1. Blockchain Traceability
    try:
        from traceability.models import TraceabilityRecord, SupplyChainEvent, QRCode
        traces = TraceabilityRecord.objects.count()
        events = SupplyChainEvent.objects.count()
        qr_codes = QRCode.objects.count()
        
        if traces > 0 and events > 0:
            differentiators['1. Blockchain Traceability'] = {
                'status': 'COMPLETE ✅',
                'details': f'{traces} traces, {events} events, {qr_codes} QR codes',
                'compliance': '100%'
            }
        else:
            differentiators['1. Blockchain Traceability'] = {
                'status': 'PARTIAL ⚠️',
                'details': 'Models exist but need data',
                'compliance': '80%'
            }
    except ImportError:
        differentiators['1. Blockchain Traceability'] = {
            'status': 'MISSING ❌',
            'details': 'Traceability models not found',
            'compliance': '0%'
        }
    
    # 2. Escrow Payment System
    try:
        from payments.models import EscrowAccount, EscrowMilestone, DisputeCase
        escrows = EscrowAccount.objects.count()
        milestones = EscrowMilestone.objects.count()
        disputes = DisputeCase.objects.count()
        
        if escrows > 0:
            differentiators['2. Escrow Payment System'] = {
                'status': 'COMPLETE ✅',
                'details': f'{escrows} escrows, {milestones} milestones, {disputes} disputes',
                'compliance': '100%'
            }
        else:
            differentiators['2. Escrow Payment System'] = {
                'status': 'PARTIAL ⚠️',
                'details': 'Models exist but need data',
                'compliance': '70%'
            }
    except ImportError:
        differentiators['2. Escrow Payment System'] = {
            'status': 'MISSING ❌',
            'details': 'Escrow models not found',
            'compliance': '0%'
        }
    
    # 3. Multi-Warehouse Network
    try:
        from warehouses.models import Warehouse, WarehouseZone, InventoryLevel
        warehouses = Warehouse.objects.count()
        zones = WarehouseZone.objects.count()
        inventory = InventoryLevel.objects.count()
        
        if warehouses >= 4:
            differentiators['3. Multi-Warehouse Network'] = {
                'status': 'COMPLETE ✅',
                'details': f'{warehouses} warehouses, {zones} zones, {inventory} inventory items',
                'compliance': '100%'
            }
        else:
            differentiators['3. Multi-Warehouse Network'] = {
                'status': 'PARTIAL ⚠️',
                'details': f'Only {warehouses} warehouses (need 4+)',
                'compliance': '60%'
            }
    except ImportError:
        differentiators['3. Multi-Warehouse Network'] = {
            'status': 'MISSING ❌',
            'details': 'Warehouse models not found',
            'compliance': '0%'
        }
    
    # 4. SMS/OTP Integration
    try:
        from communications.models import SMSProvider, SMSMessage, OTPCode
        providers = SMSProvider.objects.count()
        messages = SMSMessage.objects.count()
        otp_codes = OTPCode.objects.count()
        
        if providers > 0 and messages > 0:
            differentiators['4. SMS/OTP Integration'] = {
                'status': 'COMPLETE ✅',
                'details': f'{providers} providers, {messages} messages, {otp_codes} OTP codes',
                'compliance': '100%'
            }
        else:
            differentiators['4. SMS/OTP Integration'] = {
                'status': 'PARTIAL ⚠️',
                'details': 'Models exist but need testing',
                'compliance': '80%'
            }
    except ImportError:
        differentiators['4. SMS/OTP Integration'] = {
            'status': 'MISSING ❌',
            'details': 'SMS models not found',
            'compliance': '0%'
        }
    
    # 5. Organic/Non-Organic Certification
    try:
        from products.models import Certification
        certs = Certification.objects.count()
        organic_certs = Certification.objects.filter(certificate_type='organic').count()
        quality_certs = Certification.objects.filter(certificate_type='quality').count()
        
        if certs > 0 and organic_certs > 0:
            differentiators['5. Organic/Non-Organic Certification'] = {
                'status': 'COMPLETE ✅',
                'details': f'{certs} total certs ({organic_certs} organic, {quality_certs} quality)',
                'compliance': '100%'
            }
        else:
            differentiators['5. Organic/Non-Organic Certification'] = {
                'status': 'PARTIAL ⚠️',
                'details': 'Models exist but need certificates',
                'compliance': '70%'
            }
    except ImportError:
        differentiators['5. Organic/Non-Organic Certification'] = {
            'status': 'MISSING ❌',
            'details': 'Certification models not found',
            'compliance': '0%'
        }
    
    # 6. Multi-Currency Support
    try:
        from payments.models import PaymentGateway
        gateways = PaymentGateway.objects.count()
        
        # Check for multi-currency support
        multi_currency_gateways = 0
        total_currencies = set()
        for gateway in PaymentGateway.objects.all():
            if hasattr(gateway, 'supported_currencies') and gateway.supported_currencies:
                if len(gateway.supported_currencies) > 1:
                    multi_currency_gateways += 1
                total_currencies.update(gateway.supported_currencies)
        
        if len(total_currencies) >= 3:
            differentiators['6. Multi-Currency Support'] = {
                'status': 'COMPLETE ✅',
                'details': f'{len(total_currencies)} currencies supported: {", ".join(sorted(total_currencies))}',
                'compliance': '100%'
            }
        else:
            differentiators['6. Multi-Currency Support'] = {
                'status': 'PARTIAL ⚠️',
                'details': f'Only {len(total_currencies)} currencies supported',
                'compliance': '60%'
            }
    except ImportError:
        differentiators['6. Multi-Currency Support'] = {
            'status': 'MISSING ❌',
            'details': 'Payment gateway models not found',
            'compliance': '0%'
        }
    
    # 7. Climate-Smart Features
    try:
        # Check if we have any climate/weather related models or data
        from products.models import Product
        
        # Look for climate-related features in products or other models
        products = Product.objects.count()
        
        # This is a basic check - in a full implementation, we'd have dedicated climate models
        differentiators['7. Climate-Smart Features'] = {
            'status': 'FRAMEWORK ⚠️',
            'details': 'Basic framework exists, needs weather integration',
            'compliance': '40%'
        }
    except ImportError:
        differentiators['7. Climate-Smart Features'] = {
            'status': 'MISSING ❌',
            'details': 'No climate-smart features found',
            'compliance': '0%'
        }
    
    # Display results
    print("\n📊 DIFFERENTIATORS STATUS SUMMARY")
    print("=" * 60)
    
    total_complete = 0
    total_differentiators = len(differentiators)
    
    for name, info in differentiators.items():
        print(f"{info['status']} {name}")
        print(f"   └─ {info['details']}")
        print(f"   └─ Compliance: {info['compliance']}")
        print()
        
        if info['status'].startswith('COMPLETE'):
            total_complete += 1
    
    # Calculate overall compliance
    overall_compliance = (total_complete / total_differentiators) * 100
    
    print(f"🎯 OVERALL STATUS: {total_complete}/{total_differentiators} = {overall_compliance:.0f}% COMPLETE")
    
    if overall_compliance >= 100:
        print("🏆 ALL DIFFERENTIATORS COMPLETE! READY FOR PRODUCTION!")
    elif overall_compliance >= 80:
        print("✅ ALMOST READY! Minor improvements needed.")
    elif overall_compliance >= 60:
        print("⚠️ GOOD PROGRESS! Some key features need completion.")
    else:
        print("❌ SIGNIFICANT WORK NEEDED! Multiple systems require implementation.")
    
    return differentiators, overall_compliance

if __name__ == "__main__":
    try:
        status, compliance = check_differentiator_status()
        
        if compliance < 100:
            print(f"\n📋 NEXT STEPS:")
            print("Run the complete_differentiators.py script to finish implementation.")
        else:
            print(f"\n🎉 SUCCESS: All 7 key differentiators are fully implemented!")
            
    except Exception as e:
        print(f"❌ Error during check: {e}")
        import traceback
        traceback.print_exc()
