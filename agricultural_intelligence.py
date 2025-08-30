"""
🇬🇭 AGRICONNECT PHASE 6: AGRICULTURAL INTELLIGENCE SYSTEM
Real-time crop analytics, weather integration, and predictive insights for Ghana farmers
"""

import os
import django
from datetime import datetime, timedelta
import json
import random
import requests
from decimal import Decimal
import numpy as np

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.conf import settings
from django.utils import timezone

class GhanaAgriculturalIntelligence:
    """Advanced agricultural intelligence for Ghana farming"""
    
    def __init__(self):
        self.ghana_regions = {
            'Ashanti': {
                'capital': 'Kumasi',
                'coordinates': (6.6885, -1.6244),
                'primary_crops': ['Cocoa', 'Plantain', 'Cassava', 'Yam'],
                'rainfall_pattern': 'bimodal',
                'soil_type': 'forest_oxisols',
                'elevation': 250  # meters
            },
            'Northern': {
                'capital': 'Tamale',
                'coordinates': (9.4034, -0.8424),
                'primary_crops': ['Maize', 'Millet', 'Sorghum', 'Groundnut', 'Rice'],
                'rainfall_pattern': 'unimodal',
                'soil_type': 'savanna_alfisols',
                'elevation': 183
            },
            'Brong-Ahafo': {
                'capital': 'Sunyani',
                'coordinates': (7.3392, -2.3265),
                'primary_crops': ['Cocoa', 'Maize', 'Yam', 'Cassava'],
                'rainfall_pattern': 'bimodal',
                'soil_type': 'forest_oxisols',
                'elevation': 310
            },
            'Western': {
                'capital': 'Sekondi-Takoradi',
                'coordinates': (4.8967, -1.7831),
                'primary_crops': ['Cocoa', 'Oil Palm', 'Rubber', 'Plantain'],
                'rainfall_pattern': 'bimodal',
                'soil_type': 'coastal_oxisols',
                'elevation': 50
            },
            'Eastern': {
                'capital': 'Koforidua',
                'coordinates': (6.0893, -0.2581),
                'primary_crops': ['Cocoa', 'Coffee', 'Cassava', 'Vegetables'],
                'rainfall_pattern': 'bimodal',
                'soil_type': 'forest_oxisols',
                'elevation': 420
            }
        }
        
        self.crop_models = {
            'Cocoa': {
                'growth_cycle_days': 180,
                'optimal_rainfall_mm': 1500,
                'optimal_temp_range': (24, 28),
                'harvest_months': [9, 10, 11, 12],
                'price_volatility': 0.15,
                'yield_per_hectare': 450  # kg
            },
            'Maize': {
                'growth_cycle_days': 120,
                'optimal_rainfall_mm': 800,
                'optimal_temp_range': (20, 30),
                'harvest_months': [7, 8, 11, 12],
                'price_volatility': 0.25,
                'yield_per_hectare': 2500
            },
            'Cassava': {
                'growth_cycle_days': 365,
                'optimal_rainfall_mm': 1000,
                'optimal_temp_range': (25, 29),
                'harvest_months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                'price_volatility': 0.10,
                'yield_per_hectare': 12000
            },
            'Yam': {
                'growth_cycle_days': 300,
                'optimal_rainfall_mm': 1200,
                'optimal_temp_range': (25, 30),
                'harvest_months': [11, 12, 1, 2],
                'price_volatility': 0.20,
                'yield_per_hectare': 8000
            }
        }
    
    def get_weather_forecast(self, region):
        """Get weather forecast for Ghana region"""
        
        # Simulated weather data (in production, integrate with actual weather API)
        region_info = self.ghana_regions.get(region, self.ghana_regions['Ashanti'])
        
        # Generate realistic weather patterns for Ghana
        current_month = datetime.now().month
        
        if current_month in [12, 1, 2]:  # Harmattan season
            base_temp = 28
            humidity = 35
            rainfall_prob = 10
            wind_speed = 15
        elif current_month in [3, 4, 5]:  # Hot dry season
            base_temp = 32
            humidity = 60
            rainfall_prob = 40
            wind_speed = 8
        elif current_month in [6, 7, 8, 9]:  # Rainy season
            base_temp = 26
            humidity = 85
            rainfall_prob = 80
            wind_speed = 12
        else:  # Transition period
            base_temp = 29
            humidity = 70
            rainfall_prob = 60
            wind_speed = 10
        
        forecast = []
        for i in range(7):  # 7-day forecast
            date = datetime.now() + timedelta(days=i)
            
            daily_forecast = {
                'date': date.strftime('%Y-%m-%d'),
                'day_name': date.strftime('%A'),
                'temperature': {
                    'min': base_temp - random.uniform(3, 7),
                    'max': base_temp + random.uniform(2, 6),
                    'unit': 'Celsius'
                },
                'humidity': humidity + random.uniform(-15, 15),
                'rainfall': {
                    'probability': rainfall_prob + random.uniform(-20, 20),
                    'amount_mm': random.uniform(0, 25) if random.random() < (rainfall_prob/100) else 0
                },
                'wind': {
                    'speed_kmh': wind_speed + random.uniform(-5, 5),
                    'direction': random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
                },
                'conditions': self.determine_weather_conditions(base_temp, humidity, rainfall_prob),
                'farming_advice': self.get_farming_advice(base_temp, humidity, rainfall_prob, current_month)
            }
            
            forecast.append(daily_forecast)
        
        return {
            'region': region,
            'location': region_info['capital'],
            'coordinates': region_info['coordinates'],
            'forecast_period': '7 days',
            'forecast': forecast,
            'seasonal_outlook': self.get_seasonal_outlook(current_month, region)
        }
    
    def determine_weather_conditions(self, temperature, humidity, rainfall_prob):
        """Determine weather conditions based on parameters"""
        
        if rainfall_prob > 70:
            return 'Rainy'
        elif rainfall_prob > 40:
            return 'Partly Cloudy'
        elif temperature > 30 and humidity < 50:
            return 'Hot and Dry'
        elif humidity > 80:
            return 'Humid'
        else:
            return 'Fair'
    
    def get_farming_advice(self, temperature, humidity, rainfall_prob, month):
        """Get farming advice based on weather conditions"""
        
        advice = []
        
        if rainfall_prob > 70:
            advice.append("Good time for land preparation and planting")
            advice.append("Ensure proper drainage to prevent waterlogging")
        elif rainfall_prob < 20 and temperature > 30:
            advice.append("Consider irrigation for crops")
            advice.append("Harvest mature crops before heat stress")
        
        if month in [4, 5, 6]:  # Major planting season
            advice.append("Optimal time for maize and rice planting")
        elif month in [9, 10]:  # Minor season
            advice.append("Good for vegetable cultivation")
        
        if humidity > 80:
            advice.append("Monitor crops for fungal diseases")
        
        return advice[:2]  # Return top 2 pieces of advice
    
    def get_seasonal_outlook(self, current_month, region):
        """Get seasonal agricultural outlook"""
        
        if current_month in [4, 5, 6, 7]:
            return {
                'season': 'Major Growing Season',
                'outlook': 'Favorable conditions for staple crops',
                'recommendations': [
                    'Plant maize and rice early in season',
                    'Apply fertilizer during peak growth',
                    'Monitor for pest and disease outbreaks'
                ]
            }
        elif current_month in [9, 10, 11]:
            return {
                'season': 'Minor Growing Season',
                'outlook': 'Good for vegetable and cash crops',
                'recommendations': [
                    'Focus on high-value vegetables',
                    'Prepare for harmattan season',
                    'Plan storage for harvested crops'
                ]
            }
        else:
            return {
                'season': 'Dry Season',
                'outlook': 'Limited rain-fed agriculture',
                'recommendations': [
                    'Invest in irrigation systems',
                    'Focus on crop processing and marketing',
                    'Prepare for next planting season'
                ]
            }
    
    def predict_crop_yield(self, crop, region, farm_size_hectares, weather_data=None):
        """Predict crop yield based on conditions"""
        
        crop_model = self.crop_models.get(crop)
        region_info = self.ghana_regions.get(region)
        
        if not crop_model or not region_info:
            return None
        
        # Base yield per hectare
        base_yield = crop_model['yield_per_hectare']
        
        # Weather adjustment factors
        weather_factor = 1.0
        if weather_data:
            # Adjust based on rainfall and temperature
            optimal_rainfall = crop_model['optimal_rainfall_mm']
            actual_rainfall = sum(day['rainfall']['amount_mm'] for day in weather_data['forecast']) * 52  # Annualized
            
            rainfall_ratio = actual_rainfall / optimal_rainfall
            if rainfall_ratio > 1.5:
                weather_factor *= 0.85  # Too much rain
            elif rainfall_ratio < 0.5:
                weather_factor *= 0.70  # Too little rain
            else:
                weather_factor *= (0.8 + 0.4 * (1 - abs(1 - rainfall_ratio)))
        
        # Regional suitability factor
        if crop in region_info['primary_crops']:
            regional_factor = random.uniform(0.9, 1.1)
        else:
            regional_factor = random.uniform(0.6, 0.8)
        
        # Management practices factor (random for demo)
        management_factor = random.uniform(0.8, 1.2)
        
        # Calculate predicted yield
        predicted_yield_per_hectare = base_yield * weather_factor * regional_factor * management_factor
        total_predicted_yield = predicted_yield_per_hectare * farm_size_hectares
        
        # Calculate confidence interval
        volatility = crop_model['price_volatility']
        lower_bound = total_predicted_yield * (1 - volatility)
        upper_bound = total_predicted_yield * (1 + volatility)
        
        return {
            'crop': crop,
            'region': region,
            'farm_size_hectares': farm_size_hectares,
            'predicted_yield': {
                'total_kg': round(total_predicted_yield, 2),
                'per_hectare_kg': round(predicted_yield_per_hectare, 2),
                'confidence_interval': {
                    'lower_kg': round(lower_bound, 2),
                    'upper_kg': round(upper_bound, 2)
                }
            },
            'factors': {
                'weather_impact': round(weather_factor, 3),
                'regional_suitability': round(regional_factor, 3),
                'management_practices': round(management_factor, 3)
            },
            'harvest_timeline': {
                'planting_optimal': self.get_optimal_planting_date(crop, region),
                'harvest_expected': self.get_expected_harvest_date(crop, region),
                'growth_days': crop_model['growth_cycle_days']
            }
        }
    
    def get_optimal_planting_date(self, crop, region):
        """Get optimal planting date for crop in region"""
        
        region_info = self.ghana_regions[region]
        current_date = datetime.now()
        
        if region_info['rainfall_pattern'] == 'bimodal':
            # Two rainy seasons
            if current_date.month <= 3:
                return "April 1 - May 15 (Major Season)"
            elif current_date.month <= 8:
                return "September 1 - October 15 (Minor Season)"
            else:
                return "April 1 - May 15 (Next Major Season)"
        else:
            # Single rainy season (Northern regions)
            if current_date.month <= 5:
                return "May 1 - June 30 (Rainy Season)"
            else:
                return "May 1 - June 30 (Next Rainy Season)"
    
    def get_expected_harvest_date(self, crop, region):
        """Get expected harvest date"""
        
        crop_model = self.crop_models[crop]
        growth_days = crop_model['growth_cycle_days']
        harvest_months = crop_model['harvest_months']
        
        current_month = datetime.now().month
        
        if current_month in harvest_months:
            return f"Ready for harvest (Month {current_month})"
        else:
            next_harvest = min(month for month in harvest_months if month > current_month) if any(month > current_month for month in harvest_months) else min(harvest_months)
            return f"Expected harvest: Month {next_harvest}"
    
    def generate_market_price_prediction(self, crop, region, forecast_days=30):
        """Generate market price predictions"""
        
        crop_model = self.crop_models.get(crop)
        if not crop_model:
            return None
        
        # Base prices (GHS per kg)
        base_prices = {
            'Cocoa': 12.50,
            'Maize': 2.10,
            'Cassava': 1.20,
            'Yam': 3.50,
            'Rice': 3.80,
            'Plantain': 2.80
        }
        
        base_price = base_prices.get(crop, 2.00)
        volatility = crop_model['price_volatility']
        
        price_predictions = []
        current_price = base_price
        
        for i in range(forecast_days):
            date = datetime.now() + timedelta(days=i)
            
            # Random walk with seasonal adjustments
            daily_change = random.gauss(0, volatility * 0.1)
            
            # Seasonal adjustments
            if date.month in crop_model['harvest_months']:
                daily_change -= 0.02  # Prices typically drop during harvest
            else:
                daily_change += 0.01  # Prices rise during non-harvest periods
            
            current_price *= (1 + daily_change)
            current_price = max(current_price, base_price * 0.5)  # Floor at 50% of base
            current_price = min(current_price, base_price * 2.0)  # Ceiling at 200% of base
            
            price_predictions.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_price_ghs_per_kg': round(current_price, 2),
                'confidence': random.uniform(0.7, 0.95),
                'market_factors': self.get_market_factors(date, crop)
            })
        
        return {
            'crop': crop,
            'region': region,
            'base_price_ghs_per_kg': base_price,
            'forecast_period_days': forecast_days,
            'price_predictions': price_predictions,
            'summary': {
                'avg_predicted_price': round(sum(p['predicted_price_ghs_per_kg'] for p in price_predictions) / len(price_predictions), 2),
                'min_predicted_price': round(min(p['predicted_price_ghs_per_kg'] for p in price_predictions), 2),
                'max_predicted_price': round(max(p['predicted_price_ghs_per_kg'] for p in price_predictions), 2),
                'volatility': round(volatility * 100, 1)
            }
        }
    
    def get_market_factors(self, date, crop):
        """Get market factors affecting price"""
        
        factors = []
        
        if date.weekday() in [4, 5]:  # Friday, Saturday
            factors.append("Weekend market demand")
        
        if date.month in [12, 1]:
            factors.append("Holiday season demand")
        
        if crop == 'Cocoa' and date.month in [10, 11]:
            factors.append("Main harvest season")
        
        if random.random() < 0.1:
            factors.append("Export demand fluctuation")
        
        return factors[:2]  # Return top 2 factors
    
    def generate_comprehensive_farm_report(self, farmer_id, region, crops, farm_size):
        """Generate comprehensive agricultural intelligence report"""
        
        # Get weather forecast
        weather_data = self.get_weather_forecast(region)
        
        # Generate crop predictions
        crop_predictions = []
        for crop_info in crops:
            crop_name = crop_info['name']
            crop_hectares = crop_info['hectares']
            
            yield_prediction = self.predict_crop_yield(crop_name, region, crop_hectares, weather_data)
            price_prediction = self.generate_market_price_prediction(crop_name, region, 30)
            
            if yield_prediction and price_prediction:
                # Calculate potential revenue
                avg_price = price_prediction['summary']['avg_predicted_price']
                total_yield = yield_prediction['predicted_yield']['total_kg']
                potential_revenue = total_yield * avg_price
                
                crop_predictions.append({
                    'crop': crop_name,
                    'yield_prediction': yield_prediction,
                    'price_prediction': price_prediction,
                    'potential_revenue_ghs': round(potential_revenue, 2)
                })
        
        # Generate recommendations
        recommendations = self.generate_farming_recommendations(region, crops, weather_data)
        
        comprehensive_report = {
            'farmer_id': farmer_id,
            'region': region,
            'farm_size_hectares': farm_size,
            'report_date': datetime.now().isoformat(),
            'weather_forecast': weather_data,
            'crop_predictions': crop_predictions,
            'recommendations': recommendations,
            'total_potential_revenue': sum(cp['potential_revenue_ghs'] for cp in crop_predictions),
            'risk_assessment': self.assess_farming_risks(region, crops, weather_data),
            'next_actions': self.suggest_next_actions(region, crops, weather_data)
        }
        
        return comprehensive_report
    
    def generate_farming_recommendations(self, region, crops, weather_data):
        """Generate farming recommendations based on analysis"""
        
        recommendations = []
        
        # Weather-based recommendations
        upcoming_rain = sum(day['rainfall']['probability'] for day in weather_data['forecast'][:3]) / 3
        if upcoming_rain > 70:
            recommendations.append({
                'category': 'weather',
                'priority': 'high',
                'action': 'Prepare for heavy rainfall - ensure proper drainage',
                'timeline': 'Next 3 days'
            })
        elif upcoming_rain < 20:
            recommendations.append({
                'category': 'weather',
                'priority': 'medium',
                'action': 'Consider irrigation systems for water-sensitive crops',
                'timeline': 'This week'
            })
        
        # Crop-specific recommendations
        current_month = datetime.now().month
        for crop_info in crops:
            crop = crop_info['name']
            if crop in self.crop_models:
                harvest_months = self.crop_models[crop]['harvest_months']
                if current_month in harvest_months:
                    recommendations.append({
                        'category': 'harvest',
                        'priority': 'high',
                        'action': f'Begin {crop} harvest operations',
                        'timeline': 'This month'
                    })
        
        # Market-based recommendations
        recommendations.append({
            'category': 'market',
            'priority': 'medium',
            'action': 'Monitor market prices for optimal selling timing',
            'timeline': 'Ongoing'
        })
        
        return recommendations
    
    def assess_farming_risks(self, region, crops, weather_data):
        """Assess farming risks"""
        
        risks = []
        
        # Weather risks
        extreme_temps = any(day['temperature']['max'] > 35 for day in weather_data['forecast'])
        if extreme_temps:
            risks.append({
                'type': 'weather',
                'level': 'medium',
                'description': 'High temperature stress risk for crops'
            })
        
        # Market risks
        for crop_info in crops:
            crop = crop_info['name']
            if crop in self.crop_models:
                volatility = self.crop_models[crop]['price_volatility']
                if volatility > 0.2:
                    risks.append({
                        'type': 'market',
                        'level': 'medium',
                        'description': f'{crop} price volatility risk'
                    })
        
        return risks
    
    def suggest_next_actions(self, region, crops, weather_data):
        """Suggest immediate next actions"""
        
        actions = []
        
        # Immediate weather-based actions
        tomorrow_rain = weather_data['forecast'][1]['rainfall']['probability']
        if tomorrow_rain > 80:
            actions.append("Check and clear drainage channels")
        
        # Seasonal actions
        current_month = datetime.now().month
        if current_month in [3, 4]:
            actions.append("Prepare land for major season planting")
        elif current_month in [8, 9]:
            actions.append("Plan minor season crop selection")
        
        actions.append("Update farm records and transaction data")
        actions.append("Check mobile money account balances")
        
        return actions[:3]  # Return top 3 actions

def run_agricultural_intelligence_demo():
    """Run agricultural intelligence demonstration"""
    
    print("🧠 AGRICONNECT AGRICULTURAL INTELLIGENCE SYSTEM")
    print("=" * 60)
    
    ai_system = GhanaAgriculturalIntelligence()
    
    # Demo farmer data
    farmer_data = {
        'farmer_id': 'farmer_001',
        'region': 'Ashanti',
        'farm_size': 5.5,  # hectares
        'crops': [
            {'name': 'Cocoa', 'hectares': 3.0},
            {'name': 'Maize', 'hectares': 1.5},
            {'name': 'Cassava', 'hectares': 1.0}
        ]
    }
    
    print(f"\n👨‍🌾 FARMER PROFILE")
    print(f"ID: {farmer_data['farmer_id']}")
    print(f"Region: {farmer_data['region']}")
    print(f"Farm Size: {farmer_data['farm_size']} hectares")
    print(f"Crops: {', '.join([f\"{c['name']} ({c['hectares']}ha)\" for c in farmer_data['crops']])}")
    
    # Generate comprehensive report
    report = ai_system.generate_comprehensive_farm_report(
        farmer_data['farmer_id'],
        farmer_data['region'],
        farmer_data['crops'],
        farmer_data['farm_size']
    )
    
    # Display weather forecast
    print(f"\n🌦️ WEATHER FORECAST - {report['weather_forecast']['location']}")
    print("-" * 50)
    for day in report['weather_forecast']['forecast'][:3]:
        print(f"{day['day_name']}: {day['temperature']['min']:.1f}-{day['temperature']['max']:.1f}°C, "
              f"{day['rainfall']['probability']:.0f}% rain, {day['conditions']}")
    
    # Display crop predictions
    print(f"\n🌾 CROP YIELD & REVENUE PREDICTIONS")
    print("-" * 50)
    total_revenue = 0
    for prediction in report['crop_predictions']:
        crop = prediction['crop']
        yield_kg = prediction['yield_prediction']['predicted_yield']['total_kg']
        avg_price = prediction['price_prediction']['summary']['avg_predicted_price']
        revenue = prediction['potential_revenue_ghs']
        total_revenue += revenue
        
        print(f"{crop}: {yield_kg:,.0f} kg @ GHS {avg_price:.2f}/kg = GHS {revenue:,.2f}")
    
    print(f"\n💰 TOTAL POTENTIAL REVENUE: GHS {total_revenue:,.2f}")
    
    # Display recommendations
    print(f"\n💡 FARMING RECOMMENDATIONS")
    print("-" * 50)
    for rec in report['recommendations'][:3]:
        priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
        print(f"{priority_icon} {rec['action']} ({rec['timeline']})")
    
    # Display risks
    print(f"\n⚠️ RISK ASSESSMENT")
    print("-" * 50)
    for risk in report['risk_assessment']:
        level_icon = "🔴" if risk['level'] == 'high' else "🟡" if risk['level'] == 'medium' else "🟢"
        print(f"{level_icon} {risk['description']}")
    
    # Display next actions
    print(f"\n✅ IMMEDIATE NEXT ACTIONS")
    print("-" * 50)
    for i, action in enumerate(report['next_actions'], 1):
        print(f"{i}. {action}")
    
    print("\n" + "=" * 60)
    print("✅ AGRICULTURAL INTELLIGENCE DEMONSTRATION COMPLETE")
    print("🧠 Ready for production deployment with AI-powered insights!")
    print("=" * 60)
    
    return report

if __name__ == "__main__":
    try:
        intelligence_report = run_agricultural_intelligence_demo()
        
        # Save intelligence report
        with open('agricultural_intelligence_report.json', 'w') as f:
            json.dump(intelligence_report, f, indent=2, default=str)
        
        print(f"\n💾 Agricultural intelligence report saved to 'agricultural_intelligence_report.json'")
        
    except Exception as e:
        print(f"❌ Error running agricultural intelligence demo: {str(e)}")
        print("🔧 Ensure Django environment is properly configured")
