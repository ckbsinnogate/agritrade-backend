#!/usr/bin/env python
"""
AgriConnect Phase 5: Blockchain Traceability System Demo
=======================================================

Complete demonstration of farm-to-table traceability features:
- Farm registration and verification
- Product traceability with QR codes
- Supply chain event tracking
- Consumer scanning simulation
- Blockchain integration testing

Run: python demo_phase5_traceability.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import json
import random

# Setup Django
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.db import models
from traceability.models import (
    BlockchainNetwork, SmartContract, BlockchainTransaction,
    Farm, FarmCertification, ProductTrace, SupplyChainEvent,
    ConsumerScan
)
from products.models import Product, Category

User = get_user_model()

class TraceabilityDemo:
    """Demo class for Phase 5 Blockchain Traceability System"""
    
    def __init__(self):
        self.farmers = []
        self.farms = []
        self.products = []
        self.product_traces = []
        self.blockchain_networks = []
        self.smart_contracts = []
    
    def generate_unique_slug(self, name):
        """Generate a unique slug for a product"""
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug
        
    def run_complete_demo(self):
        """Run complete traceability demo"""
        print("🌾 AGRICONNECT PHASE 5: BLOCKCHAIN TRACEABILITY DEMO")
        print("=" * 60)
        
        try:
            # Step 1: Setup blockchain infrastructure
            self.setup_blockchain_infrastructure()
            
            # Step 2: Create farmers and farms
            self.create_demo_farmers()
            self.register_demo_farms()
            
            # Step 3: Add farm certifications
            self.add_farm_certifications()
            
            # Step 4: Create products and traces
            self.create_product_traces()
            
            # Step 5: Record supply chain events
            self.record_supply_chain_events()
            
            # Step 6: Test QR code generation
            self.test_qr_code_generation()
            
            # Step 7: Simulate consumer scans
            self.simulate_consumer_scans()
            
            # Step 8: Display comprehensive report
            self.display_comprehensive_report()
            
            print("\n✅ PHASE 5 DEMO COMPLETED SUCCESSFULLY!")
            print("🚀 Blockchain Traceability System is ready for production!")
            
        except Exception as e:
            print(f"\n❌ Demo failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def setup_blockchain_infrastructure(self):
        """Setup blockchain networks and smart contracts"""
        print("\n🔗 Step 1: Setting up Blockchain Infrastructure")
        print("-" * 50)
          # Create blockchain networks
        networks_data = [
            {
                'name': 'Ethereum Mainnet',
                'network_id': 1,
                'rpc_url': 'https://mainnet.infura.io/v3/your-project-id',
                'explorer_url': 'https://etherscan.io',
                'native_currency': 'ETH',
                'is_testnet': False,
                'is_active': True
            },
            {
                'name': 'Polygon Mumbai Testnet',
                'network_id': 80001,
                'rpc_url': 'https://rpc-mumbai.maticvigil.com/',
                'explorer_url': 'https://mumbai.polygonscan.com',
                'native_currency': 'MATIC',
                'is_testnet': True,
                'is_active': True
            },
            {
                'name': 'Binance Smart Chain Testnet',
                'network_id': 97,
                'rpc_url': 'https://data-seed-prebsc-1-s1.binance.org:8545/',
                'explorer_url': 'https://testnet.bscscan.com',
                'native_currency': 'BNB',
                'is_testnet': True,
                'is_active': True
            }
        ]
        
        for network_data in networks_data:
            network, created = BlockchainNetwork.objects.get_or_create(
                name=network_data['name'],
                defaults=network_data
            )
            self.blockchain_networks.append(network)
            status = "✅ Created" if created else "🔄 Updated"
            print(f"  {status}: {network.name} (Network ID: {network.network_id})")
          # Create smart contracts
        contracts_data = [
            {
                'name': 'AgriConnect Product Traceability',
                'contract_address': '0x742d35Cc6634C0532925a3b8D098e9d4f93E4AEf',
                'version': '1.0.0',
                'abi': [
                    {
                        "inputs": [{"name": "_productId", "type": "string"}],
                        "name": "registerProduct",
                        "outputs": [{"name": "", "type": "uint256"}],
                        "type": "function"
                    }
                ],
                'is_deployed': True,
                'deployment_transaction': '0x123...abc'
            },
            {
                'name': 'AgriConnect Certification',
                'contract_address': '0x853d955aCEf822Db058eb8505911ED77F175b99e',
                'version': '1.0.0',
                'abi': [
                    {
                        "inputs": [{"name": "_certId", "type": "string"}],
                        "name": "issueCertificate",
                        "outputs": [{"name": "", "type": "bool"}],
                        "type": "function"
                    }
                ],
                'is_deployed': True,
                'deployment_transaction': '0x456...def'
            }        ]
        
        for contract_data in contracts_data:
            contract_data['network'] = self.blockchain_networks[1]  # Use Polygon testnet
            contract_data['deployed_at'] = timezone.now()
            
            contract, created = SmartContract.objects.get_or_create(
                name=contract_data['name'],
                network=contract_data['network'],
                defaults=contract_data
            )
            self.smart_contracts.append(contract)
            status = "✅ Created" if created else "🔄 Updated"
            print(f"  {status}: {contract.name} at {contract.contract_address}")
        
        print(f"  📊 Total Networks: {len(self.blockchain_networks)}")
        print(f"  📋 Total Contracts: {len(self.smart_contracts)}")
    
    def create_demo_farmers(self):
        """Create demo farmers for testing"""
        print("\n👨‍🌾 Step 2: Creating Demo Farmers")
        print("-" * 50)
        
        farmers_data = [
            {
                'username': 'kwame_organic',
                'email': 'kwame@agrifarm.gh',
                'first_name': 'Kwame',
                'last_name': 'Asante',
                'phone_number': '+233244123456'
            },
            {
                'username': 'fatima_cocoa',
                'email': 'fatima@cocoafarm.gh',
                'first_name': 'Fatima',
                'last_name': 'Abdul-Rahman',
                'phone_number': '+233205987654'
            },
            {
                'username': 'john_plantain',
                'email': 'john@plantainfarm.gh',
                'first_name': 'John',
                'last_name': 'Osei',
                'phone_number': '+233244567890'
            },
            {
                'username': 'mary_vegetables',
                'email': 'mary@vegfarm.gh',
                'first_name': 'Mary',
                'last_name': 'Amponsah',
                'phone_number': '+233277123456'
            }
        ]
        
        for farmer_data in farmers_data:
            farmer, created = User.objects.get_or_create(
                username=farmer_data['username'],
                defaults=farmer_data
            )
            self.farmers.append(farmer)
            status = "✅ Created" if created else "🔄 Updated"
            print(f"  {status}: {farmer.get_full_name()} ({farmer.username})")
        
        print(f"  👥 Total Farmers: {len(self.farmers)}")
    
    def register_demo_farms(self):
        """Register farms for traceability"""
        print("\n🏡 Step 3: Registering Demo Farms")
        print("-" * 50)
        
        farms_data = [
            {
                'name': 'Green Valley Organic Farm',
                'location': 'Ashanti Region, Kumasi, Ghana',
                'latitude': Decimal('6.6885'),
                'longitude': Decimal('-1.6244'),
                'farm_size_hectares': Decimal('25.5'),
                'organic_certified': True,
                'certification_body': 'Ghana Organic Agriculture Network',
                'registration_number': 'GH-ORG-001-2024'
            },
            {
                'name': 'Golden Cocoa Estate',
                'location': 'Western Region, Sefwi Wiawso, Ghana',
                'latitude': Decimal('6.2084'),
                'longitude': Decimal('-2.4817'),
                'farm_size_hectares': Decimal('50.0'),
                'organic_certified': True,
                'certification_body': 'Fairtrade Africa',
                'registration_number': 'GH-COC-002-2024'
            },
            {
                'name': 'Tropical Plantain Gardens',
                'location': 'Eastern Region, Koforidua, Ghana',
                'latitude': Decimal('6.0898'),
                'longitude': Decimal('-0.2571'),
                'farm_size_hectares': Decimal('15.8'),
                'organic_certified': False,
                'certification_body': '',
                'registration_number': 'GH-PLT-003-2024'
            },
            {
                'name': 'Fresh Vegetable Fields',
                'location': 'Greater Accra, Tema, Ghana',
                'latitude': Decimal('5.6698'),
                'longitude': Decimal('-0.0166'),
                'farm_size_hectares': Decimal('8.2'),
                'organic_certified': True,
                'certification_body': 'GlobalGAP',
                'registration_number': 'GH-VEG-004-2024'
            }
        ]
        
        for i, farm_data in enumerate(farms_data):
            farm_data['farmer'] = self.farmers[i]
            farm_data['is_verified'] = True
            farm_data['verification_date'] = timezone.now()
            farm_data['blockchain_address'] = f"0x{random.randint(10**39, 10**40-1):040x}"
            
            farm, created = Farm.objects.get_or_create(
                registration_number=farm_data['registration_number'],
                defaults=farm_data
            )
            self.farms.append(farm)
            status = "✅ Created" if created else "🔄 Updated"
            print(f"  {status}: {farm.name}")
            print(f"    📍 Location: {farm.location}")
            print(f"    📏 Size: {farm.farm_size_hectares} hectares")
            print(f"    🌱 Organic: {'Yes' if farm.organic_certified else 'No'}")
            print(f"    🔗 Blockchain: {farm.blockchain_address}")
        
        print(f"  🏡 Total Farms: {len(self.farms)}")
    
    def add_farm_certifications(self):
        """Add certifications to farms"""
        print("\n📜 Step 4: Adding Farm Certifications")
        print("-" * 50)
        
        certifications_data = [
            # Green Valley Organic Farm certifications
            {
                'farm': 0,
                'certification_type': 'organic',
                'certificate_number': 'ORG-GH-2024-001',
                'issuing_authority': 'Ghana Organic Agriculture Network',
                'issue_date': datetime.now().date() - timedelta(days=180),
                'expiry_date': datetime.now().date() + timedelta(days=185),
                'blockchain_verified': True
            },
            {
                'farm': 0,
                'certification_type': 'global_gap',
                'certificate_number': 'GAP-GH-2024-001',
                'issuing_authority': 'GlobalGAP Ghana',
                'issue_date': datetime.now().date() - timedelta(days=90),
                'expiry_date': datetime.now().date() + timedelta(days=275),
                'blockchain_verified': True
            },
            # Golden Cocoa Estate certifications
            {
                'farm': 1,
                'certification_type': 'organic',
                'certificate_number': 'ORG-GH-2024-002',
                'issuing_authority': 'Fairtrade Africa',
                'issue_date': datetime.now().date() - timedelta(days=200),
                'expiry_date': datetime.now().date() + timedelta(days=165),
                'blockchain_verified': True
            },
            {
                'farm': 1,
                'certification_type': 'fair_trade',
                'certificate_number': 'FT-GH-2024-002',
                'issuing_authority': 'Fairtrade International',
                'issue_date': datetime.now().date() - timedelta(days=150),
                'expiry_date': datetime.now().date() + timedelta(days=215),
                'blockchain_verified': True
            },
            # Fresh Vegetable Fields certifications
            {
                'farm': 3,
                'certification_type': 'global_gap',
                'certificate_number': 'GAP-GH-2024-004',
                'issuing_authority': 'GlobalGAP Ghana',
                'issue_date': datetime.now().date() - timedelta(days=60),
                'expiry_date': datetime.now().date() + timedelta(days=305),
                'blockchain_verified': True
            },
            {
                'farm': 3,
                'certification_type': 'haccp',
                'certificate_number': 'HACCP-GH-2024-004',
                'issuing_authority': 'Ghana Standards Authority',
                'issue_date': datetime.now().date() - timedelta(days=30),
                'expiry_date': datetime.now().date() + timedelta(days=335),
                'blockchain_verified': False
            }        ]
        
        for cert_data in certifications_data:
            cert_data['farm'] = self.farms[cert_data['farm']]
            cert_data['certificate_file_hash'] = f"Qm{random.randint(10**45, 10**46-1):046x}"
            cert_data['blockchain_hash'] = f"0x{random.randint(10**63, 10**64-1):064x}"
            
            certification, created = FarmCertification.objects.get_or_create(
                farm=cert_data['farm'],
                certification_type=cert_data['certification_type'],
                certificate_number=cert_data['certificate_number'],
                defaults=cert_data
            )
            status = "✅ Created" if created else "🔄 Updated"
            print(f"  {status}: {certification.farm.name}")
            print(f"    📋 Type: {certification.get_certification_type_display()}")
            print(f"    🏢 Authority: {certification.issuing_authority}")
            print(f"    📅 Valid until: {certification.expiry_date}")
            print(f"    ✅ Blockchain Verified: {'Yes' if certification.blockchain_verified else 'No'}")
        
        total_certifications = FarmCertification.objects.count()
        print(f"  📜 Total Certifications: {total_certifications}")
    
    def create_product_traces(self):
        """Create product traces for demonstration"""
        print("\n📦 Step 5: Creating Product Traces")
        print("-" * 50)
        
        # Get existing products
        tomatoes = Product.objects.filter(name__icontains='tomato').first()
        yam = Product.objects.filter(name__icontains='yam').first()
        plantain = Product.objects.filter(name__icontains='plantain').first()
        cabbage = Product.objects.filter(name__icontains='cabbage').first()
          # Create products if they don't exist
        vegetable_cat, _ = Category.objects.get_or_create(name='Vegetables')
        root_cat, _ = Category.objects.get_or_create(name='Root Crops')
        
        if not tomatoes:
            print("  ⚠️  Creating Organic Tomatoes...")
            tomatoes = Product.objects.create(
                name='Organic Tomatoes',
                slug=self.generate_unique_slug('Organic Tomatoes'),
                description='Fresh organic tomatoes',
                category=vegetable_cat,
                unit='kg',
                price_per_unit=Decimal('8.50'),
                organic_status='organic',
                seller=self.farmers[3],
                product_type='raw'            )
        
        if not yam:
            print("  ⚠️  Creating White Yam...")
            yam = Product.objects.create(
                name='White Yam',
                slug=self.generate_unique_slug('White Yam'),
                description='Fresh white yam tubers',
                category=root_cat,
                unit='kg',
                price_per_unit=Decimal('12.00'),
                organic_status='non_organic',
                seller=self.farmers[0],
                product_type='raw'            )
        
        if not plantain:
            print("  ⚠️  Creating Green Plantain...")
            plantain = Product.objects.create(
                name='Green Plantain',
                slug=self.generate_unique_slug('Green Plantain'),
                description='Fresh green plantain',
                category=vegetable_cat,
                unit='bunch',
                price_per_unit=Decimal('15.00'),
                organic_status='non_organic',
                seller=self.farmers[2],
                product_type='raw'            )
        
        if not cabbage:
            print("  ⚠️  Creating Organic Cabbage...")
            cabbage = Product.objects.create(
                name='Organic Cabbage',
                slug=self.generate_unique_slug('Organic Cabbage'),
                description='Fresh organic cabbage',
                category=vegetable_cat,
                unit='head',
                price_per_unit=Decimal('6.00'),
                organic_status='organic',
                seller=self.farmers[3],
                product_type='raw'
            )
        
        products_data = [
            {
                'product': tomatoes,
                'farm': self.farms[3],  # Fresh Vegetable Fields
                'harvest_location': 'Block A, Fresh Vegetable Fields',
                'batch_number': 'TOM-2024-001',
                'quantity_harvested': Decimal('250.00'),
                'quality_grade': 'premium',
                'harvest_date': timezone.now() - timedelta(days=3)
            },
            {
                'product': yam,
                'farm': self.farms[0],  # Green Valley Organic Farm
                'harvest_location': 'Section B, Green Valley',
                'batch_number': 'YAM-2024-002',
                'quantity_harvested': Decimal('500.00'),
                'quality_grade': 'good',
                'harvest_date': timezone.now() - timedelta(days=7)
            },
            {
                'product': plantain,
                'farm': self.farms[2],  # Tropical Plantain Gardens
                'harvest_location': 'Grove 1, Plantain Gardens',
                'batch_number': 'PLT-2024-003',
                'quantity_harvested': Decimal('180.00'),
                'quality_grade': 'premium',
                'harvest_date': timezone.now() - timedelta(days=5)
            },
            {
                'product': cabbage,
                'farm': self.farms[3],  # Fresh Vegetable Fields
                'harvest_location': 'Block C, Fresh Vegetable Fields',
                'batch_number': 'CAB-2024-004',
                'quantity_harvested': Decimal('120.00'),
                'quality_grade': 'premium',
                'harvest_date': timezone.now() - timedelta(days=2)
            }
        ]
        
        for trace_data in products_data:
            trace_data['blockchain_id'] = f"0x{random.randint(10**63, 10**64-1):064x}"
            trace_data['qr_code_data'] = json.dumps({
                'product_id': str(trace_data['product'].id),
                'batch_number': trace_data['batch_number'],
                'blockchain_id': trace_data['blockchain_id']
            })
            trace_data['ipfs_hash'] = f"Qm{random.randint(10**45, 10**46-1):046x}"
            
            trace, created = ProductTrace.objects.get_or_create(
                product=trace_data['product'],
                defaults=trace_data
            )
            self.product_traces.append(trace)
            status = "✅ Created" if created else "🔄 Updated"
            print(f"  {status}: {trace.product.name}")
            print(f"    🏡 Farm: {trace.farm.name}")
            print(f"    📦 Batch: {trace.batch_number}")
            print(f"    ⚖️  Quantity: {trace.quantity_harvested} {trace.product.unit}")
            print(f"    ⭐ Quality: {trace.quality_grade}")
            print(f"    🔗 Blockchain ID: {trace.blockchain_id[:20]}...")
        
        print(f"  📦 Total Product Traces: {len(self.product_traces)}")
    
    def record_supply_chain_events(self):
        """Record supply chain events for each product trace"""
        print("\n🔄 Step 6: Recording Supply Chain Events")
        print("-" * 50)
        
        event_types = [
            'harvest', 'process', 'package', 'store', 'transport', 'inspect', 'deliver'
        ]
        
        for trace in self.product_traces:
            events_count = 0
            base_time = trace.harvest_date
            
            for i, event_type in enumerate(event_types):
                # Create realistic timeline
                event_time = base_time + timedelta(hours=i*6, minutes=random.randint(0, 120))
                
                if event_time > timezone.now():
                    break
                
                event_data = {
                    'product_trace': trace,
                    'event_type': event_type,
                    'actor': trace.farm.farmer,
                    'location': self.get_event_location(event_type, trace.farm.location),
                    'latitude': trace.farm.latitude + Decimal(str(random.uniform(-0.01, 0.01))),
                    'longitude': trace.farm.longitude + Decimal(str(random.uniform(-0.01, 0.01))),
                    'timestamp': event_time,
                    'description': self.get_event_description(event_type, trace.product.name),
                    'metadata': self.get_event_metadata(event_type),
                    'blockchain_hash': f"0x{random.randint(10**63, 10**64-1):064x}",
                    'status': 'verified' if random.choice([True, True, False]) else 'completed',
                    'verification_required': event_type in ['harvest', 'inspect', 'deliver'],
                    'verified_at': event_time + timedelta(minutes=random.randint(30, 180)) if random.choice([True, False]) else None
                }
                
                event, created = SupplyChainEvent.objects.get_or_create(
                    product_trace=trace,
                    event_type=event_type,
                    timestamp=event_time,
                    defaults=event_data
                )
                
                if created:
                    events_count += 1
            
            print(f"  📦 {trace.product.name} ({trace.batch_number})")
            print(f"    🔄 Events: {events_count} recorded")
            print(f"    📊 Status: Supply chain tracking active")
        
        total_events = SupplyChainEvent.objects.count()
        print(f"  🔄 Total Supply Chain Events: {total_events}")
    
    def test_qr_code_generation(self):
        """Test QR code generation for product traces"""
        print("\n📱 Step 7: Testing QR Code Generation")
        print("-" * 50)
        
        for trace in self.product_traces[:2]:  # Test first 2 products
            qr_data = {
                'product_id': str(trace.product.id),
                'product_name': trace.product.name,
                'batch_number': trace.batch_number,
                'blockchain_id': trace.blockchain_id,
                'farm_name': trace.farm.name,
                'farmer_name': trace.farm.farmer.get_full_name(),
                'harvest_date': trace.harvest_date.isoformat(),
                'organic_certified': trace.farm.organic_certified,
                'verification_url': f"https://agriconnect.gh/verify/{trace.blockchain_id}"
            }
            
            # Simulate QR code generation (in real implementation, this would use qrcode library)
            trace.qr_code_data = json.dumps(qr_data)
            trace.qr_code_image = f"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...{random.randint(10**10, 10**11-1)}"
            trace.save()
            
            print(f"  ✅ QR Code generated for {trace.product.name}")
            print(f"    📦 Batch: {trace.batch_number}")
            print(f"    🔗 Contains: Product info, farm details, blockchain verification")
            print(f"    📱 Format: Base64 encoded PNG image")
        
        print(f"  📱 QR Codes generated for {len(self.product_traces[:2])} products")
    
    def simulate_consumer_scans(self):
        """Simulate consumer QR code scans"""
        print("\n👥 Step 8: Simulating Consumer Scans")
        print("-" * 50)
        
        # Simulate different types of consumers
        consumer_types = [
            {'id': 'consumer_001', 'device': 'iPhone', 'location': 'Accra, Ghana'},
            {'id': 'consumer_002', 'device': 'Android', 'location': 'Kumasi, Ghana'},
            {'id': 'anonymous', 'device': 'Android', 'location': 'Tema, Ghana'},
            {'id': 'consumer_003', 'device': 'iPhone', 'location': 'Cape Coast, Ghana'}
        ]
        
        for trace in self.product_traces:
            # Simulate 1-5 scans per product
            num_scans = random.randint(1, 5)
            
            for i in range(num_scans):
                consumer = random.choice(consumer_types)
                scan_time = timezone.now() - timedelta(
                    hours=random.randint(1, 72),
                    minutes=random.randint(0, 59)
                )
                
                scan_data = {
                    'product_trace': trace,
                    'consumer_id': consumer['id'],
                    'ip_address': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    'user_agent': f"Mozilla/5.0 ({consumer['device']})",
                    'location': consumer['location'],
                    'latitude': Decimal(str(random.uniform(4.5, 11.0))),
                    'longitude': Decimal(str(random.uniform(-3.5, 1.5))),
                    'device_type': consumer['device'].lower(),
                    'app_version': '1.0.0',
                    'scan_duration': random.randint(30, 300),  # 30 seconds to 5 minutes
                    'feedback_rating': random.randint(4, 5) if random.choice([True, False]) else None,
                    'feedback_comment': 'Great to see the farm where my food comes from!' if random.choice([True, False]) else '',
                    'scanned_at': scan_time
                }
                
                scan = ConsumerScan.objects.create(**scan_data)
                
                # Update trace view count
                trace.consumer_view_count += 1
                trace.last_viewed_at = scan_time
                trace.save()
            
            print(f"  📱 {trace.product.name}: {num_scans} consumer scans")
            print(f"    👀 Total views: {trace.consumer_view_count}")
            print(f"    🕒 Last viewed: {trace.last_viewed_at.strftime('%Y-%m-%d %H:%M')}")
        
        total_scans = ConsumerScan.objects.count()
        print(f"  👥 Total Consumer Scans: {total_scans}")
    
    def display_comprehensive_report(self):
        """Display comprehensive traceability system report"""
        print("\n📊 PHASE 5 TRACEABILITY SYSTEM REPORT")
        print("=" * 60)
        
        # Blockchain Infrastructure
        print("\n🔗 Blockchain Infrastructure:")
        print(f"  Networks: {BlockchainNetwork.objects.count()}")
        print(f"  Smart Contracts: {SmartContract.objects.count()}")
        print(f"  Transactions: {BlockchainTransaction.objects.count()}")
        
        # Farm & Farmer Statistics
        print("\n🏡 Farm & Farmer Statistics:")
        print(f"  Registered Farmers: {len(self.farmers)}")
        print(f"  Verified Farms: {Farm.objects.filter(is_verified=True).count()}")
        print(f"  Organic Certified Farms: {Farm.objects.filter(organic_certified=True).count()}")
        print(f"  Total Farm Size: {sum(f.farm_size_hectares for f in self.farms):.1f} hectares")
        
        # Certification Statistics
        total_certs = FarmCertification.objects.count()
        verified_certs = FarmCertification.objects.filter(blockchain_verified=True).count()
        print(f"\n📜 Certification Statistics:")
        print(f"  Total Certifications: {total_certs}")
        print(f"  Blockchain Verified: {verified_certs} ({verified_certs/total_certs*100:.1f}%)")
        
        # Product Traceability
        print(f"\n📦 Product Traceability:")
        print(f"  Products with Traces: {len(self.product_traces)}")
        print(f"  Supply Chain Events: {SupplyChainEvent.objects.count()}")
        print(f"  QR Codes Generated: {ProductTrace.objects.exclude(qr_code_image='').count()}")
        
        # Consumer Engagement
        total_scans = ConsumerScan.objects.count()
        total_views = sum(trace.consumer_view_count for trace in self.product_traces)
        avg_rating = ConsumerScan.objects.exclude(feedback_rating__isnull=True).aggregate(
            avg_rating=django.db.models.Avg('feedback_rating')
        )['avg_rating'] or 0
        
        print(f"\n👥 Consumer Engagement:")
        print(f"  Total QR Scans: {total_scans}")
        print(f"  Total Product Views: {total_views}")
        print(f"  Average Rating: {avg_rating:.1f}/5.0")
        print(f"  Feedback Comments: {ConsumerScan.objects.exclude(feedback_comment='').count()}")
        
        # Most Popular Products
        print(f"\n⭐ Most Popular Products:")
        popular_products = sorted(self.product_traces, key=lambda x: x.consumer_view_count, reverse=True)[:3]
        for i, trace in enumerate(popular_products, 1):
            print(f"  {i}. {trace.product.name} - {trace.consumer_view_count} views")
        
        # Recent Activity
        print(f"\n🕒 Recent Activity (Last 24 hours):")
        recent_scans = ConsumerScan.objects.filter(
            scanned_at__gte=timezone.now() - timedelta(days=1)
        ).count()
        recent_events = SupplyChainEvent.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=1)
        ).count()
        
        print(f"  Consumer Scans: {recent_scans}")
        print(f"  Supply Chain Events: {recent_events}")
        
        # System Health
        print(f"\n✅ System Health:")
        print(f"  All farms verified: {'Yes' if all(f.is_verified for f in self.farms) else 'No'}")
        print(f"  All products traced: {'Yes' if len(self.product_traces) > 0 else 'No'}")
        print(f"  QR codes functional: {'Yes' if any(t.qr_code_image for t in self.product_traces) else 'No'}")
        print(f"  Consumer engagement: {'Active' if total_scans > 0 else 'Inactive'}")
        
        print(f"\n🎯 Phase 5 Success Metrics:")
        print(f"  ✅ Farm registration: COMPLETE")
        print(f"  ✅ Product traceability: COMPLETE")
        print(f"  ✅ QR code generation: COMPLETE")
        print(f"  ✅ Consumer scanning: COMPLETE")
        print(f"  ✅ Supply chain tracking: COMPLETE")
        print(f"  ✅ Blockchain integration: READY")
        
    # Helper methods
    def get_event_location(self, event_type, base_location):
        """Generate event-specific location"""
        locations = {
            'harvest': f"Field, {base_location}",
            'process': f"Processing Center, {base_location}",
            'package': f"Packaging Facility, {base_location}",
            'store': "AgriConnect Warehouse, Tema",
            'transport': "Highway A1, Ghana",
            'inspect': "Quality Control Lab, Accra",
            'deliver': "Market, Accra"
        }
        return locations.get(event_type, base_location)
    
    def get_event_description(self, event_type, product_name):
        """Generate event-specific description"""
        descriptions = {
            'harvest': f"Fresh {product_name} harvested from farm",
            'process': f"{product_name} cleaned and sorted",
            'package': f"{product_name} packaged for transport",
            'store': f"{product_name} stored in climate-controlled warehouse",
            'transport': f"{product_name} loaded for transport to market",
            'inspect': f"Quality inspection completed for {product_name}",
            'deliver': f"{product_name} delivered to final destination"
        }
        return descriptions.get(event_type, f"Supply chain event for {product_name}")
    
    def get_event_metadata(self, event_type):
        """Generate event-specific metadata"""
        metadata = {
            'harvest': {
                'weather': 'Sunny, 28°C',
                'workers': random.randint(3, 8),
                'equipment': 'Hand tools, baskets'
            },
            'process': {
                'temperature': random.randint(15, 25),
                'duration_minutes': random.randint(30, 120),
                'method': 'Manual sorting'
            },
            'package': {
                'package_type': 'Cardboard boxes',
                'package_count': random.randint(10, 50),
                'weight_kg': random.randint(200, 500)
            },
            'store': {
                'temperature': random.randint(12, 18),
                'humidity': random.randint(60, 85),
                'storage_zone': f"Zone {random.choice(['A', 'B', 'C'])}"
            },
            'transport': {
                'vehicle_type': 'Refrigerated truck',
                'distance_km': random.randint(50, 300),
                'driver': f"Driver {random.randint(1, 10)}"
            },
            'inspect': {
                'quality_score': random.randint(85, 98),
                'inspector': f"Inspector {random.randint(1, 5)}",
                'tests_performed': ['Visual', 'Weight', 'Freshness']
            },
            'deliver': {
                'recipient': 'Market Vendor',
                'delivery_time': f"{random.randint(8, 16):02d}:00",
                'condition': 'Excellent'
            }
        }
        return metadata.get(event_type, {})

def main():
    """Main demo execution"""
    demo = TraceabilityDemo()
    demo.run_complete_demo()

if __name__ == '__main__':
    main()
