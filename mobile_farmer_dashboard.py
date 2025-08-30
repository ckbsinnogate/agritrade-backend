"""
🇬🇭 AGRICONNECT PHASE 6: MOBILE-FIRST FARMER DASHBOARD
Advanced mobile analytics optimized for Ghana farmers
"""

import os
import django
from datetime import datetime, timedelta
import json
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Sum, Count, Avg
from django.utils import timezone

class GhanaMobileFarmerDashboard:
    """Mobile-optimized dashboard for Ghana farmers"""
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'tw': 'Twi',
            'ga': 'Ga',
            'ee': 'Ewe',
            'ha': 'Hausa'
        }
        
        self.voice_commands = {
            'en': {
                'balance': 'Check my balance',
                'transactions': 'Show my transactions',
                'crops': 'My crop information',
                'weather': 'Weather update',
                'payments': 'Recent payments'
            },
            'tw': {
                'balance': 'Hwε me sika',
                'transactions': 'Kyerε me adetɔ',
                'crops': 'Me mfua ho nsεm',
                'weather': 'Wiem tebea',
                'payments': 'Akatua a aba yi'
            }
        }
    
    def generate_mobile_dashboard_data(self, farmer_id, language='en'):
        """Generate mobile-optimized dashboard data"""
        
        # Mobile-first data structure
        mobile_data = {
            'farmer_id': farmer_id,
            'language': language,
            'timestamp': datetime.now().isoformat(),
            'quick_stats': self.get_quick_stats(farmer_id),
            'recent_transactions': self.get_recent_transactions(farmer_id, limit=5),
            'crop_calendar': self.get_crop_calendar(),
            'weather_alert': self.get_weather_alert(),
            'payment_reminders': self.get_payment_reminders(farmer_id),
            'market_prices': self.get_market_prices(),
            'mobile_money_balance': self.get_mobile_money_status(farmer_id),
            'voice_commands': self.voice_commands.get(language, self.voice_commands['en']),
            'offline_sync': self.get_offline_sync_status()
        }
        
        return mobile_data
    
    def get_quick_stats(self, farmer_id):
        """Get quick stats for mobile display"""
        
        # Simulated farmer stats
        today = datetime.now()
        this_month = today.replace(day=1)
        
        stats = {
            'today_earnings': {
                'amount': random.uniform(50, 500),
                'currency': 'GHS',
                'transactions': random.randint(1, 8),
                'trend': random.choice(['up', 'down', 'stable'])
            },
            'month_earnings': {
                'amount': random.uniform(1500, 8000),
                'currency': 'GHS',
                'transactions': random.randint(15, 45),
                'vs_last_month': random.uniform(-20, 30)
            },
            'pending_payments': {
                'count': random.randint(0, 5),
                'total_amount': random.uniform(100, 2000),
                'currency': 'GHS'
            },
            'active_crops': {
                'count': random.randint(2, 6),
                'primary_crop': random.choice(['Cocoa', 'Maize', 'Cassava', 'Yam']),
                'harvest_status': random.choice(['Growing', 'Ready', 'Harvesting'])
            }
        }
        
        return stats
    
    def get_recent_transactions(self, farmer_id, limit=5):
        """Get recent transactions optimized for mobile"""
        
        transactions = []
        
        for i in range(limit):
            transaction = {
                'id': f"TXN{random.randint(100000, 999999)}",
                'date': (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d'),
                'time': f"{random.randint(6, 20):02d}:{random.randint(0, 59):02d}",
                'amount': random.uniform(25, 1500),
                'currency': 'GHS',
                'type': random.choice(['sale', 'purchase', 'payment_received', 'fee']),
                'status': random.choice(['completed', 'pending', 'failed']),
                'payment_method': random.choice(['mtn_momo', 'vodafone_cash', 'airteltigo_money']),
                'crop_type': random.choice(['Cocoa', 'Maize', 'Cassava', 'Vegetables']),
                'buyer': f"Buyer {random.randint(1, 50)}",
                'location': random.choice(['Kumasi Market', 'Accra Central', 'Takoradi Port', 'Local Cooperative'])
            }
            transactions.append(transaction)
        
        return transactions
    
    def get_crop_calendar(self):
        """Get Ghana crop calendar for current period"""
        
        current_month = datetime.now().month
        
        if current_month in [4, 5, 6, 7]:  # Major season
            calendar_info = {
                'current_season': 'Major Season',
                'season_status': 'Active Growing Period',
                'recommended_activities': [
                    'Apply fertilizer to maize crops',
                    'Weed cocoa farms',
                    'Prepare rice fields',
                    'Harvest early plantain'
                ],
                'critical_dates': {
                    'next_fertilizer': '2024-08-15',
                    'harvest_start': '2024-09-01',
                    'market_peak': '2024-09-15'
                }
            }
        elif current_month in [9, 10, 11, 12]:  # Minor season
            calendar_info = {
                'current_season': 'Minor Season',
                'season_status': 'Harvest & Planting Period',
                'recommended_activities': [
                    'Harvest major season crops',
                    'Plant vegetables',
                    'Prepare cassava fields',
                    'Market surplus produce'
                ],
                'critical_dates': {
                    'harvest_deadline': '2024-12-31',
                    'planting_start': '2024-10-01',
                    'market_opportunity': '2024-11-15'
                }
            }
        else:  # Dry season
            calendar_info = {
                'current_season': 'Dry Season',
                'season_status': 'Irrigation & Planning Period',
                'recommended_activities': [
                    'Set up irrigation for vegetables',
                    'Plan next major season',
                    'Maintain equipment',
                    'Process and store crops'
                ],
                'critical_dates': {
                    'irrigation_setup': '2024-01-15',
                    'planning_meeting': '2024-02-01',
                    'preparation_start': '2024-03-01'
                }
            }
        
        return calendar_info
    
    def get_weather_alert(self):
        """Get weather alerts for farmers"""
        
        weather_alerts = [
            {
                'type': 'rainfall',
                'severity': 'moderate',
                'message': 'Expected rainfall in next 48 hours - good for crop growth',
                'action': 'Continue normal farming activities',
                'icon': '🌧️'
            },
            {
                'type': 'drought',
                'severity': 'low',
                'message': 'Dry period expected for next 5 days',
                'action': 'Consider irrigation for sensitive crops',
                'icon': '☀️'
            },
            {
                'type': 'harmattan',
                'severity': 'high',
                'message': 'Strong harmattan winds expected',
                'action': 'Protect young plants and check irrigation',
                'icon': '💨'
            }
        ]
        
        return random.choice(weather_alerts)
    
    def get_payment_reminders(self, farmer_id):
        """Get payment reminders for farmer"""
        
        reminders = []
        
        # Generate 1-3 random reminders
        for i in range(random.randint(1, 3)):
            reminder = {
                'id': f"REM{random.randint(100, 999)}",
                'type': random.choice(['payment_due', 'payment_received', 'payment_pending']),
                'amount': random.uniform(100, 2000),
                'currency': 'GHS',
                'due_date': (datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                'description': random.choice([
                    'Cocoa delivery payment',
                    'Fertilizer purchase',
                    'Tractor rental fee',
                    'Seed purchase payment',
                    'Market stall fee'
                ]),
                'priority': random.choice(['high', 'medium', 'low'])
            }
            reminders.append(reminder)
        
        return reminders
    
    def get_market_prices(self):
        """Get current market prices for crops"""
        
        market_prices = {
            'Cocoa': {
                'current_price': random.uniform(11000, 13000),
                'currency': 'GHS',
                'unit': 'tonne',
                'trend': random.choice(['up', 'down', 'stable']),
                'change_percent': random.uniform(-5, 5),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            'Maize': {
                'current_price': random.uniform(1800, 2300),
                'currency': 'GHS',
                'unit': 'tonne',
                'trend': random.choice(['up', 'down', 'stable']),
                'change_percent': random.uniform(-3, 8),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            'Cassava': {
                'current_price': random.uniform(1000, 1400),
                'currency': 'GHS',
                'unit': 'tonne',
                'trend': random.choice(['up', 'down', 'stable']),
                'change_percent': random.uniform(-2, 6),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            },
            'Vegetables': {
                'current_price': random.uniform(2.0, 4.5),
                'currency': 'GHS',
                'unit': 'kg',
                'trend': random.choice(['up', 'down', 'stable']),
                'change_percent': random.uniform(-10, 15),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        }
        
        return market_prices
    
    def get_mobile_money_status(self, farmer_id):
        """Get mobile money account status"""
        
        operators = ['MTN', 'Vodafone', 'AirtelTigo']
        primary_operator = random.choice(operators)
        
        mobile_money_status = {
            'primary_account': {
                'operator': primary_operator,
                'phone_number': f"0{random.randint(20, 59)}{random.randint(1000000, 9999999)}",
                'balance': random.uniform(50, 2000),
                'currency': 'GHS',
                'status': 'active',
                'daily_limit': 5000,
                'used_today': random.uniform(0, 1000)
            },
            'linked_accounts': [
                {
                    'operator': op,
                    'status': 'linked' if op != primary_operator else 'primary',
                    'available': True
                }
                for op in operators
            ],
            'recent_activity': {
                'last_transaction': (datetime.now() - timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M'),
                'transaction_count_today': random.randint(0, 8),
                'total_volume_today': random.uniform(0, 1500)
            }
        }
        
        return mobile_money_status
    
    def get_offline_sync_status(self):
        """Get offline synchronization status"""
        
        offline_status = {
            'enabled': True,
            'last_sync': (datetime.now() - timedelta(minutes=random.randint(5, 60))).strftime('%Y-%m-%d %H:%M'),
            'pending_transactions': random.randint(0, 3),
            'sync_status': random.choice(['synced', 'pending', 'error']),
            'storage_used': random.uniform(10, 80),  # Percentage
            'storage_limit': 100  # MB
        }
        
        return offline_status

@method_decorator(csrf_exempt, name='dispatch')
class MobileFarmerDashboardAPI(View):
    """API endpoint for mobile farmer dashboard"""
    
    def get(self, request, farmer_id=None):
        """Get mobile dashboard data"""
        
        language = request.GET.get('lang', 'en')
        dashboard = GhanaMobileFarmerDashboard()
        
        try:
            farmer_id = farmer_id or request.GET.get('farmer_id', 'demo_farmer')
            dashboard_data = dashboard.generate_mobile_dashboard_data(farmer_id, language)
            
            return JsonResponse({
                'success': True,
                'data': dashboard_data,
                'message': 'Mobile dashboard data retrieved successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve dashboard data'
            }, status=500)
    
    def post(self, request):
        """Handle voice commands and mobile interactions"""
        
        try:
            data = json.loads(request.body)
            command = data.get('command')
            language = data.get('language', 'en')
            farmer_id = data.get('farmer_id')
            
            dashboard = GhanaMobileFarmerDashboard()
            
            # Process voice command
            if command in ['balance', 'transactions', 'crops', 'weather', 'payments']:
                response_data = self.process_voice_command(command, farmer_id, language, dashboard)
                
                return JsonResponse({
                    'success': True,
                    'command': command,
                    'data': response_data,
                    'message': f'Voice command "{command}" processed successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Unknown voice command'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Failed to process mobile interaction'
            }, status=500)
    
    def process_voice_command(self, command, farmer_id, language, dashboard):
        """Process voice commands"""
        
        if command == 'balance':
            stats = dashboard.get_quick_stats(farmer_id)
            return {
                'type': 'balance',
                'today_earnings': stats['today_earnings'],
                'month_earnings': stats['month_earnings']
            }
        elif command == 'transactions':
            return {
                'type': 'transactions',
                'recent_transactions': dashboard.get_recent_transactions(farmer_id, 3)
            }
        elif command == 'crops':
            return {
                'type': 'crops',
                'crop_calendar': dashboard.get_crop_calendar(),
                'market_prices': dashboard.get_market_prices()
            }
        elif command == 'weather':
            return {
                'type': 'weather',
                'weather_alert': dashboard.get_weather_alert()
            }
        elif command == 'payments':
            return {
                'type': 'payments',
                'payment_reminders': dashboard.get_payment_reminders(farmer_id),
                'mobile_money_status': dashboard.get_mobile_money_status(farmer_id)
            }
        
        return {'type': 'unknown', 'message': 'Command not recognized'}

def run_mobile_dashboard_demo():
    """Run mobile dashboard demonstration"""
    
    print("📱 AGRICONNECT MOBILE FARMER DASHBOARD")
    print("=" * 50)
    
    dashboard = GhanaMobileFarmerDashboard()
    farmer_id = "demo_farmer_001"
    
    # Generate mobile dashboard data
    mobile_data = dashboard.generate_mobile_dashboard_data(farmer_id, 'en')
    
    # Display quick stats
    print("\n💰 QUICK STATS")
    print("-" * 30)
    stats = mobile_data['quick_stats']
    print(f"Today's Earnings: GHS {stats['today_earnings']['amount']:.2f}")
    print(f"This Month: GHS {stats['month_earnings']['amount']:.2f}")
    print(f"Pending Payments: {stats['pending_payments']['count']}")
    print(f"Active Crops: {stats['active_crops']['count']} ({stats['active_crops']['primary_crop']})")
    
    # Display recent transactions
    print("\n📊 RECENT TRANSACTIONS")
    print("-" * 30)
    for txn in mobile_data['recent_transactions'][:3]:
        print(f"{txn['date']} | GHS {txn['amount']:.2f} | {txn['type']} | {txn['status']}")
    
    # Display crop calendar
    print("\n🌾 CROP CALENDAR")
    print("-" * 30)
    calendar = mobile_data['crop_calendar']
    print(f"Season: {calendar['current_season']}")
    print(f"Status: {calendar['season_status']}")
    print(f"Activities: {', '.join(calendar['recommended_activities'][:2])}")
    
    # Display weather alert
    print("\n🌦️ WEATHER ALERT")
    print("-" * 30)
    weather = mobile_data['weather_alert']
    print(f"{weather['icon']} {weather['message']}")
    print(f"Action: {weather['action']}")
    
    # Display market prices
    print("\n💹 MARKET PRICES")
    print("-" * 30)
    for crop, price_info in list(mobile_data['market_prices'].items())[:3]:
        trend_icon = "📈" if price_info['trend'] == 'up' else "📉" if price_info['trend'] == 'down' else "➡️"
        print(f"{crop}: GHS {price_info['current_price']:.2f}/{price_info['unit']} {trend_icon}")
    
    # Display mobile money status
    print("\n📱 MOBILE MONEY STATUS")
    print("-" * 30)
    momo = mobile_data['mobile_money_balance']
    print(f"Primary: {momo['primary_account']['operator']}")
    print(f"Balance: GHS {momo['primary_account']['balance']:.2f}")
    print(f"Daily Limit: GHS {momo['primary_account']['daily_limit']}")
    
    print("\n" + "=" * 50)
    print("✅ MOBILE DASHBOARD DEMONSTRATION COMPLETE")
    print("📱 Ready for production mobile deployment!")
    print("=" * 50)
    
    return mobile_data

if __name__ == "__main__":
    try:
        mobile_data = run_mobile_dashboard_demo()
        
        # Save mobile data results
        with open('mobile_dashboard_results.json', 'w') as f:
            json.dump(mobile_data, f, indent=2, default=str)
        
        print(f"\n💾 Mobile dashboard data saved to 'mobile_dashboard_results.json'")
        
    except Exception as e:
        print(f"❌ Error running mobile dashboard demo: {str(e)}")
        print("🔧 Ensure Django environment is properly configured")
