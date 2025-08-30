"""
Django Management Command: AI-Enhanced Communication Demo
Demonstrates AI-powered communication features
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
import asyncio
import json
from datetime import datetime, timedelta

from ...ai_enhanced_communication_service import CommunicationAIService, CommunicationAnalyticsAI
from ...communications.models import (
    SMSMessage, CommunicationLog, AIMessageOptimization, 
    FarmerCommunicationProfile, IntelligentResponse
)


class Command(BaseCommand):
    help = 'Demonstrate AI-Enhanced Communication System capabilities'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--demo-type',
            type=str,
            default='all',
            choices=['all', 'optimization', 'timing', 'content', 'response', 'analytics'],
            help='Type of AI communication demo to run'
        )
        
        parser.add_argument(
            '--farmer-count',
            type=int,
            default=5,
            help='Number of demo farmers to use'
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🤖 AGRICONNECT AI-ENHANCED COMMUNICATION DEMO")
        self.stdout.write("=" * 60)
        
        demo_type = options['demo_type']
        farmer_count = options['farmer_count']
        
        # Initialize AI services
        self.ai_comm_service = CommunicationAIService()
        self.analytics_service = CommunicationAnalyticsAI()
        
        # Create demo farmer profiles
        demo_farmers = self.create_demo_farmers(farmer_count)
        
        if demo_type == 'all' or demo_type == 'optimization':
            self.demo_message_optimization(demo_farmers)
        
        if demo_type == 'all' or demo_type == 'timing':
            self.demo_timing_prediction(demo_farmers)
        
        if demo_type == 'all' or demo_type == 'content':
            self.demo_content_generation()
        
        if demo_type == 'all' or demo_type == 'response':
            self.demo_intelligent_responses(demo_farmers)
        
        if demo_type == 'all' or demo_type == 'analytics':
            self.demo_analytics()
        
        self.stdout.write(self.style.SUCCESS("\n🎉 AI-Enhanced Communication Demo Complete!"))
    
    def create_demo_farmers(self, count):
        """Create demo farmer profiles for testing"""
        self.stdout.write(f"\n👨‍🌾 Creating {count} demo farmer profiles...")
        
        demo_farmers = []
        crops_options = [
            ['maize', 'beans'], ['cocoa'], ['cassava', 'yam'], 
            ['tomatoes', 'pepper'], ['rice'], ['plantain', 'banana']
        ]
        regions = ['Ashanti', 'Northern', 'Greater Accra', 'Western', 'Volta', 'Central']
        languages = ['English', 'Twi', 'Ga', 'Ewe', 'Hausa']
        education_levels = ['basic', 'secondary', 'tertiary']
        
        for i in range(count):
            farmer = {
                'id': 1000 + i,
                'name': f'Demo Farmer {i+1}',
                'phone_number': f'+233{20 + i}{1000000 + i}',
                'region': regions[i % len(regions)],
                'crops': crops_options[i % len(crops_options)],
                'language': languages[i % len(languages)],
                'education_level': education_levels[i % len(education_levels)],
                'experience_years': (i % 10) + 1,
                'farm_size_hectares': (i % 5) + 1
            }
            demo_farmers.append(farmer)
            
            self.stdout.write(f"  ✅ {farmer['name']} - {farmer['region']} Region - {farmer['crops']}")
        
        return demo_farmers
    
    def demo_message_optimization(self, farmers):
        """Demonstrate AI message optimization"""
        self.stdout.write(f"\n🧠 DEMO: AI MESSAGE OPTIMIZATION")
        self.stdout.write("-" * 40)
        
        test_messages = [
            {
                'type': 'weather_alert',
                'content': 'Heavy rains expected tomorrow. Check your crops.',
                'context': 'Weather warning for farmers'
            },
            {
                'type': 'market_update',
                'content': 'Maize prices have increased by 15%. Good time to sell.',
                'context': 'Market price notification'
            },
            {
                'type': 'farming_tip',
                'content': 'Apply fertilizer to your crops during the rainy season.',
                'context': 'Agricultural advice'
            }
        ]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for i, farmer in enumerate(farmers[:3]):  # Test with first 3 farmers
            message = test_messages[i % len(test_messages)]
            
            self.stdout.write(f"\n📝 Optimizing message for {farmer['name']}:")
            self.stdout.write(f"   Original: '{message['content']}'")
            
            try:
                result = loop.run_until_complete(
                    self.ai_comm_service.optimize_message_content(
                        farmer, message['type'], message['content']
                    )
                )
                
                if result.get('success'):
                    self.stdout.write(f"   ✅ Optimized: '{result['optimized_message']}'")
                    self.stdout.write(f"   📊 Engagement Score: {result.get('engagement_score', 0)}/100")
                    self.stdout.write(f"   🎯 Urgency: {result.get('urgency_level', 'medium')}")
                    
                    # Save optimization record
                    AIMessageOptimization.objects.create(
                        original_content=message['content'],
                        optimized_content=result['optimized_message'],
                        message_type=message['type'],
                        farmer_profile=farmer,
                        ai_model_used='OpenRouter AI',
                        optimization_score=result.get('engagement_score', 0),
                        processing_time_ms=1500,
                        improvements_made=result.get('improvements', [])
                    )
                else:
                    self.stdout.write(f"   ❌ Optimization failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.stdout.write(f"   ❌ Error: {str(e)}")
        
        loop.close()
    
    def demo_timing_prediction(self, farmers):
        """Demonstrate AI timing prediction"""
        self.stdout.write(f"\n⏰ DEMO: AI TIMING PREDICTION")
        self.stdout.write("-" * 40)
        
        message_scenarios = [
            {'type': 'weather_alert', 'urgency': 'high'},
            {'type': 'market_update', 'urgency': 'medium'},
            {'type': 'farming_tip', 'urgency': 'low'}
        ]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for i, farmer in enumerate(farmers[:3]):
            scenario = message_scenarios[i % len(message_scenarios)]
            
            self.stdout.write(f"\n🕐 Predicting timing for {farmer['name']}:")
            self.stdout.write(f"   Message Type: {scenario['type']}")
            self.stdout.write(f"   Urgency: {scenario['urgency']}")
            
            try:
                result = loop.run_until_complete(
                    self.ai_comm_service.predict_optimal_timing(
                        farmer['id'], scenario['type'], scenario['urgency']
                    )
                )
                
                if result.get('success'):
                    optimal_time = result.get('optimal_time')
                    engagement_prob = result.get('engagement_probability', 0)
                    
                    self.stdout.write(f"   ✅ Optimal Time: {optimal_time.strftime('%Y-%m-%d %H:%M')}")
                    self.stdout.write(f"   📈 Engagement Probability: {engagement_prob}%")
                    self.stdout.write(f"   💡 Reasoning: {result.get('reasoning', 'AI-optimized')}")
                else:
                    self.stdout.write(f"   ❌ Prediction failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.stdout.write(f"   ❌ Error: {str(e)}")
        
        loop.close()
    
    def demo_content_generation(self):
        """Demonstrate AI content generation"""
        self.stdout.write(f"\n📝 DEMO: AI CONTENT GENERATION")
        self.stdout.write("-" * 40)
        
        content_scenarios = [
            {
                'type': 'weather_alert',
                'context': {
                    'location': 'Kumasi, Ashanti Region',
                    'temperature': 28,
                    'rainfall': 15,
                    'humidity': 85,
                    'forecast': 'Heavy rains expected',
                    'crops': ['maize', 'beans'],
                    'season': 'major_season',
                    'language': 'English'
                }
            },
            {
                'type': 'market_update',
                'context': {
                    'crops': ['cocoa'],
                    'current_prices': {'cocoa': 'GHS 8500/tonne'},
                    'price_changes': {'cocoa': '+12%'},
                    'market_location': 'Tema Port',
                    'demand_level': 'High',
                    'farmer_crops': ['cocoa'],
                    'storage_capacity': 'Limited'
                }
            },
            {
                'type': 'farming_tip',
                'context': {
                    'crop': 'tomatoes',
                    'growth_stage': 'flowering',
                    'season': 'dry_season',
                    'region': 'Upper East',
                    'experience': 'beginner'
                }
            }
        ]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for scenario in content_scenarios:
            self.stdout.write(f"\n📋 Generating {scenario['type']} content:")
            
            try:
                result = loop.run_until_complete(
                    self.ai_comm_service.generate_intelligent_content(
                        scenario['type'], scenario['context']
                    )
                )
                
                if result.get('success'):
                    content = result.get('content', 'No content generated')
                    urgency = result.get('urgency', 'medium')
                    
                    self.stdout.write(f"   ✅ Generated: '{content}'")
                    self.stdout.write(f"   🚨 Urgency: {urgency}")
                    
                    if 'actions' in result:
                        self.stdout.write(f"   📋 Actions: {', '.join(result['actions'])}")
                else:
                    self.stdout.write(f"   ❌ Generation failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.stdout.write(f"   ❌ Error: {str(e)}")
        
        loop.close()
    
    def demo_intelligent_responses(self, farmers):
        """Demonstrate AI intelligent responses"""
        self.stdout.write(f"\n🤖 DEMO: INTELLIGENT RESPONSE SYSTEM")
        self.stdout.write("-" * 40)
        
        farmer_messages = [
            "My maize plants have yellow leaves. What should I do?",
            "When is the best time to harvest my cocoa pods?",
            "How much fertilizer should I use for 2 hectares of tomatoes?",
            "The weather is too dry. Should I water my crops?",
            "Where can I sell my cassava at the best price?"
        ]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for i, farmer in enumerate(farmers):
            if i >= len(farmer_messages):
                break
                
            message = farmer_messages[i]
            
            self.stdout.write(f"\n💬 Processing message from {farmer['name']}:")
            self.stdout.write(f"   Question: '{message}'")
            
            try:
                result = loop.run_until_complete(
                    self.ai_comm_service.intelligent_response_handler(
                        message, farmer['id']
                    )
                )
                
                if result.get('success'):
                    response = result.get('response_message', 'No response generated')
                    intent = result.get('intent', 'unknown')
                    urgency = result.get('urgency', 'medium')
                    requires_human = result.get('requires_human', False)
                    
                    self.stdout.write(f"   ✅ Response: '{response}'")
                    self.stdout.write(f"   🎯 Intent: {intent}")
                    self.stdout.write(f"   🚨 Urgency: {urgency}")
                    self.stdout.write(f"   👤 Needs Human: {'Yes' if requires_human else 'No'}")
                    
                    # Save intelligent response record
                    IntelligentResponse.objects.create(
                        incoming_message=message,
                        farmer_id=farmer['id'],
                        detected_intent=intent,
                        urgency_level=urgency,
                        topic_category='farming_question',
                        ai_response=response,
                        confidence_score=85.0,
                        requires_human_intervention=requires_human,
                        ai_model_used='OpenRouter AI',
                        processing_time_ms=2000,
                        response_sent=True
                    )
                else:
                    self.stdout.write(f"   ❌ Response failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.stdout.write(f"   ❌ Error: {str(e)}")
        
        loop.close()
    
    def demo_analytics(self):
        """Demonstrate AI communication analytics"""
        self.stdout.write(f"\n📊 DEMO: AI COMMUNICATION ANALYTICS")
        self.stdout.write("-" * 40)
        
        # Create some demo communication logs
        self.create_demo_communication_logs()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                self.analytics_service.analyze_communication_effectiveness('30d')
            )
            
            if result.get('success'):
                analytics = result.get('analytics', {})
                
                self.stdout.write(f"\n📈 Communication Analytics (30 days):")
                self.stdout.write(f"   Overall Effectiveness: {analytics.get('overall_effectiveness', 0)}/100")
                self.stdout.write(f"   AI Enhancement Impact: {analytics.get('ai_enhancement_impact', 'N/A')}")
                self.stdout.write(f"   Best Times: {', '.join(analytics.get('best_times', []))}")
                self.stdout.write(f"   Top Message Types: {', '.join(analytics.get('top_message_types', []))}")
                
                recommendations = analytics.get('recommendations', [])
                if recommendations:
                    self.stdout.write(f"\n💡 AI Recommendations:")
                    for i, rec in enumerate(recommendations, 1):
                        self.stdout.write(f"   {i}. {rec}")
            else:
                self.stdout.write(f"   ❌ Analytics failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.stdout.write(f"   ❌ Error: {str(e)}")
        
        loop.close()
    
    def create_demo_communication_logs(self):
        """Create demo communication logs for analytics"""
        message_types = ['weather_alert', 'market_update', 'farming_tip', 'price_alert']
        statuses = ['delivered', 'delivered', 'delivered', 'failed']  # 75% success rate
        
        # Create logs for the past 30 days
        base_time = timezone.now() - timedelta(days=30)
        
        for day in range(30):
            for hour in [9, 14, 18]:  # 3 messages per day
                log_time = base_time + timedelta(days=day, hours=hour)
                
                CommunicationLog.objects.get_or_create(
                    recipient_phone=f"+233201000{day:03d}",
                    message_content=f"Demo message {day}-{hour}",
                    message_type=message_types[day % len(message_types)],
                    ai_enhanced=day % 2 == 0,  # 50% AI enhanced
                    ai_optimization_score=75 + (day % 25),  # Varying scores
                    delivery_status=statuses[day % len(statuses)],
                    created_at=log_time
                )
        
        self.stdout.write(f"   📝 Created demo communication logs")
    
    def display_summary(self):
        """Display demo summary"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("🎯 AI-ENHANCED COMMUNICATION DEMO SUMMARY")
        self.stdout.write("=" * 60)
        
        # Count demo records created
        optimizations = AIMessageOptimization.objects.count()
        responses = IntelligentResponse.objects.count()
        logs = CommunicationLog.objects.filter(ai_enhanced=True).count()
        
        self.stdout.write(f"📊 Demo Records Created:")
        self.stdout.write(f"   • Message Optimizations: {optimizations}")
        self.stdout.write(f"   • Intelligent Responses: {responses}")
        self.stdout.write(f"   • AI-Enhanced Logs: {logs}")
        
        self.stdout.write(f"\n🚀 AI Features Demonstrated:")
        self.stdout.write(f"   ✅ Smart message optimization")
        self.stdout.write(f"   ✅ Predictive timing optimization")
        self.stdout.write(f"   ✅ Intelligent content generation")
        self.stdout.write(f"   ✅ Automated response handling")
        self.stdout.write(f"   ✅ Communication analytics")
        
        self.stdout.write(f"\n🎉 All AI communication features operational!")
