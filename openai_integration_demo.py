#!/usr/bin/env python3
"""
AgriConnect OpenAI API Integration Demo
Practical implementation examples for key AI features
"""

import os
import sys
import django
import openai
import base64
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from products.models import Product, Category
from authentication.models import User
from orders.models import Order
from warehouses.models import Warehouse

class AgriConnectAI:
    """OpenAI integration for AgriConnect agricultural intelligence"""
    
    def __init__(self):
        # Initialize OpenAI client (you'll need to set your API key)
        self.client = openai.OpenAI(
            api_key="your-openai-api-key-here"  # Replace with actual key
        )
        
    def intelligent_crop_advisory(self, farmer_location, season, soil_type, budget):
        """AI-powered crop recommendations for Ghana farmers"""
        
        # Get current market data from database
        current_products = Product.objects.filter(status='active')
        market_prices = {p.name: float(p.price_per_unit) for p in current_products}
        
        prompt = f"""
        You are an expert agricultural advisor specializing in Ghana's farming conditions.
        
        Farmer Context:
        - Location: {farmer_location}
        - Season: {season}
        - Soil Type: {soil_type}
        - Budget: GHS {budget}
        - Current Market Prices: {market_prices}
        
        Provide personalized crop recommendations including:
        1. Top 3 most profitable crops for this context
        2. Expected yields per acre
        3. Investment requirements
        4. Risk assessment
        5. Timeline for planting and harvesting
        6. Market outlook for next 6 months
        
        Format as practical, actionable advice for a Ghanaian farmer.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Ghana's most trusted agricultural advisor with 20 years of experience."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            advice = response.choices[0].message.content
            
            return {
                "success": True,
                "advice": advice,
                "farmer_location": farmer_location,
                "season": season,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def disease_detection_and_treatment(self, image_path, symptoms_description, crop_type):
        """AI-powered plant disease detection with treatment recommendations"""
        
        # Encode image for Vision API
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        
        try:
            base64_image = encode_image(image_path)
            
            prompt = f"""
            Analyze this image of a {crop_type} plant showing potential disease symptoms.
            
            Additional symptoms reported by farmer: {symptoms_description}
            
            Provide:
            1. Disease identification (name and confidence level)
            2. Severity assessment (mild/moderate/severe)
            3. Immediate treatment recommendations
            4. Prevention strategies
            5. Expected recovery timeline
            6. Cost of treatment in Ghana context
            
            Focus on treatments available in Ghana's agricultural supply chain.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=400
            )
            
            diagnosis = response.choices[0].message.content
            
            return {
                "success": True,
                "diagnosis": diagnosis,
                "crop_type": crop_type,
                "symptoms": symptoms_description,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def market_price_prediction(self, crop_name, region, timeframe_months=3):
        """AI-powered market price forecasting"""
        
        # Get historical price data from database
        historical_orders = Order.objects.filter(
            items__product__name__icontains=crop_name,
            created_at__gte=datetime.now() - timedelta(days=180)
        ).order_by('created_at')
        
        price_history = []
        for order in historical_orders:
            for item in order.items.all():
                if crop_name.lower() in item.product.name.lower():
                    price_history.append({
                        "date": order.created_at.strftime("%Y-%m-%d"),
                        "price": float(item.price_per_unit),
                        "quantity": float(item.quantity)
                    })
        
        prompt = f"""
        Analyze market trends for {crop_name} in {region}, Ghana.
        
        Historical Price Data (last 6 months): {price_history}
        Current Season: {datetime.now().strftime("%B %Y")}
        Forecast Period: Next {timeframe_months} months
        
        Provide:
        1. Price trend analysis (increasing/decreasing/stable)
        2. Expected price range for next {timeframe_months} months
        3. Peak selling periods
        4. Market demand factors
        5. Supply chain considerations
        6. Recommended selling strategy
        
        Consider Ghana's agricultural seasons, export markets, and local consumption patterns.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a market analyst specializing in Ghana's agricultural commodities with access to regional and international market data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.6
            )
            
            prediction = response.choices[0].message.content
            
            return {
                "success": True,
                "prediction": prediction,
                "crop": crop_name,
                "region": region,
                "timeframe": f"{timeframe_months} months",
                "historical_data_points": len(price_history),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def conversational_farmer_assistant(self, farmer_question, farmer_context=None):
        """24/7 AI assistant for farmer questions"""
        
        # Get farmer's context from database if available
        if farmer_context and 'user_id' in farmer_context:
            try:
                user = User.objects.get(id=farmer_context['user_id'])
                recent_orders = Order.objects.filter(customer=user).order_by('-created_at')[:5]
                
                context_info = {
                    "farmer_type": getattr(user, 'user_type', 'farmer'),
                    "location": getattr(user, 'location', 'Ghana'),
                    "recent_crops": [item.product.name for order in recent_orders for item in order.items.all()],
                    "experience_level": "experienced" if recent_orders.count() > 10 else "beginner"
                }
            except:
                context_info = {"farmer_type": "farmer", "location": "Ghana"}
        else:
            context_info = {"farmer_type": "farmer", "location": "Ghana"}
        
        prompt = f"""
        You are AgriBot, a friendly and knowledgeable agricultural assistant for Ghana farmers.
        
        Farmer Context: {context_info}
        Question: {farmer_question}
        
        Provide a helpful, practical answer that:
        1. Addresses the specific question
        2. Considers Ghana's farming conditions
        3. Offers actionable advice
        4. Suggests follow-up resources if needed
        5. Uses simple, clear language
        
        Keep response concise but comprehensive. If the question requires visual inspection or complex diagnosis, suggest contacting agricultural extension services or using AgriConnect's AI vision tools.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Faster and cheaper for conversational AI
                messages=[
                    {"role": "system", "content": "You are AgriBot, Ghana's most helpful agricultural assistant. You speak like a knowledgeable local expert who genuinely cares about farmers' success."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            answer = response.choices[0].message.content
            
            return {
                "success": True,
                "answer": answer,
                "question": farmer_question,
                "context": context_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def supply_chain_optimization(self, order_data, warehouse_locations):
        """AI-powered supply chain and logistics optimization"""
        
        # Get current warehouse data
        warehouses = Warehouse.objects.all()
        warehouse_data = []
        for wh in warehouses:
            warehouse_data.append({
                "name": wh.name,
                "location": f"{wh.city}, {wh.region}",
                "capacity": float(wh.capacity_cubic_meters),
                "utilization": float(wh.current_utilization_percent),
                "type": wh.warehouse_type.warehouse_type if wh.warehouse_type else "general"
            })
        
        prompt = f"""
        Optimize supply chain for AgriConnect Ghana operations.
        
        Current Order Data: {order_data}
        Available Warehouses: {warehouse_data}
        
        Analyze and recommend:
        1. Optimal warehouse allocation for orders
        2. Most efficient delivery routes
        3. Inventory rebalancing opportunities
        4. Cost reduction strategies
        5. Delivery time optimization
        6. Risk mitigation for supply disruptions
        
        Consider Ghana's transportation infrastructure, seasonal road conditions, and fuel costs.
        Prioritize customer satisfaction while minimizing operational costs.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a supply chain optimization expert specializing in African agricultural logistics with deep knowledge of Ghana's infrastructure and market conditions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            optimization = response.choices[0].message.content
            
            return {
                "success": True,
                "optimization": optimization,
                "warehouses_analyzed": len(warehouse_data),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

def demo_ai_capabilities():
    """Demonstrate AgriConnect AI capabilities"""
    
    print("🤖 AGRICONNECT AI CAPABILITIES DEMONSTRATION")
    print("=" * 60)
    
    ai = AgriConnectAI()
    
    # Demo 1: Crop Advisory
    print("\n🌾 1. INTELLIGENT CROP ADVISORY")
    print("-" * 40)
    advisory = ai.intelligent_crop_advisory(
        farmer_location="Kumasi, Ashanti Region",
        season="Major Rainy Season (April-July)",
        soil_type="Forest Oxysols",
        budget=5000
    )
    
    if advisory["success"]:
        print("✅ Crop Advisory Generated Successfully")
        print(f"📍 Location: {advisory['farmer_location']}")
        print(f"📅 Season: {advisory['season']}")
        print(f"💡 Advice Preview: {advisory['advice'][:100]}...")
    else:
        print(f"❌ Advisory Failed: {advisory['error']}")
    
    # Demo 2: Conversational Assistant
    print("\n💬 2. CONVERSATIONAL FARMER ASSISTANT")
    print("-" * 40)
    
    questions = [
        "When is the best time to plant maize in Ashanti Region?",
        "My tomato plants have yellow leaves. What should I do?",
        "What's the current market price for cocoa?"
    ]
    
    for question in questions:
        print(f"❓ Question: {question}")
        response = ai.conversational_farmer_assistant(question)
        
        if response["success"]:
            print(f"🤖 AgriBot: {response['answer'][:100]}...")
        else:
            print(f"❌ Response Failed: {response['error']}")
        print()
    
    # Demo 3: Market Prediction
    print("\n📈 3. MARKET PRICE PREDICTION")
    print("-" * 40)
    prediction = ai.market_price_prediction(
        crop_name="maize",
        region="Greater Accra",
        timeframe_months=3
    )
    
    if prediction["success"]:
        print("✅ Market Prediction Generated")
        print(f"🌽 Crop: {prediction['crop']}")
        print(f"📍 Region: {prediction['region']}")
        print(f"⏰ Timeframe: {prediction['timeframe']}")
        print(f"📊 Data Points: {prediction['historical_data_points']}")
        print(f"💰 Prediction Preview: {prediction['prediction'][:100]}...")
    else:
        print(f"❌ Prediction Failed: {prediction['error']}")
    
    print("\n🎯 AI INTEGRATION RECOMMENDATIONS:")
    print("1. 🔥 Start with Conversational Assistant (highest ROI)")
    print("2. 🔥 Implement Crop Advisory for farmer retention")
    print("3. 🔥 Add Market Prediction for competitive advantage")
    print("4. 🟡 Disease Detection for premium service tier")
    print("5. 🟡 Supply Chain Optimization for operational efficiency")
    
    print(f"\n💡 Next Steps:")
    print("- Set up OpenAI API key in environment variables")
    print("- Create dedicated AI endpoints in Django views")
    print("- Integrate with existing user authentication")
    print("- Add AI responses to SMS/WhatsApp notifications")
    print("- Implement usage tracking and cost monitoring")
    
    return True

if __name__ == "__main__":
    demo_ai_capabilities()
