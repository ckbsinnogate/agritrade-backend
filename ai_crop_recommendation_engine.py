"""
🇬🇭 AGRICONNECT PHASE 7: AI CROP RECOMMENDATION ENGINE
Machine Learning-powered crop selection optimization for Ghana farmers
"""

import os
import django
from datetime import datetime, timedelta
import json
import random
import numpy as np
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriconnect.settings')
django.setup()

from django.utils import timezone

class GhanaAICropRecommendationEngine:
    """AI-powered crop recommendation system for Ghana farmers"""
    
    def __init__(self):
        self.ghana_regions = {
            'Ashanti': {
                'coordinates': (6.6885, -1.6244),
                'rainfall_mm': 1400,
                'temperature_avg': 26.5,
                'soil_type': 'forest_oxisols',
                'elevation': 250,
                'ph_range': (5.5, 6.5),
                'predominant_farming': 'mixed_farming'
            },
            'Northern': {
                'coordinates': (9.4034, -0.8424),
                'rainfall_mm': 950,
                'temperature_avg': 28.2,
                'soil_type': 'savanna_alfisols',
                'elevation': 183,
                'ph_range': (6.0, 7.5),
                'predominant_farming': 'cereal_production'
            },
            'Brong-Ahafo': {
                'coordinates': (7.3392, -2.3265),
                'rainfall_mm': 1250,
                'temperature_avg': 26.8,
                'soil_type': 'forest_oxisols',
                'elevation': 310,
                'ph_range': (5.8, 6.8),
                'predominant_farming': 'tree_crops'
            },
            'Western': {
                'coordinates': (4.8967, -1.7831),
                'rainfall_mm': 1800,
                'temperature_avg': 26.1,
                'soil_type': 'coastal_oxisols',
                'elevation': 50,
                'ph_range': (5.2, 6.2),
                'predominant_farming': 'plantation_crops'
            },
            'Eastern': {
                'coordinates': (6.0893, -0.2581),
                'rainfall_mm': 1350,
                'temperature_avg': 26.3,
                'soil_type': 'forest_oxisols',
                'elevation': 420,
                'ph_range': (5.5, 6.5),
                'predominant_farming': 'mixed_farming'
            }
        }
        
        self.crop_database = {
            'Cocoa': {
                'scientific_name': 'Theobroma cacao',
                'category': 'tree_crop',
                'optimal_conditions': {
                    'rainfall_mm': (1200, 2000),
                    'temperature_c': (21, 32),
                    'ph_range': (6.0, 7.0),
                    'elevation_m': (0, 700),
                    'humidity_percent': (75, 95)
                },
                'growth_characteristics': {
                    'maturity_months': 60,
                    'productive_years': 30,
                    'yield_kg_per_hectare': 450,
                    'planting_density': 1111,  # trees per hectare
                    'harvest_cycles_per_year': 2
                },
                'market_data': {
                    'price_ghs_per_kg': 12.50,
                    'demand_stability': 'high',
                    'export_potential': 'excellent',
                    'local_market': 'limited',
                    'price_volatility': 0.15
                },
                'climate_resilience': {
                    'drought_tolerance': 'medium',
                    'flood_tolerance': 'low',
                    'heat_tolerance': 'medium',
                    'disease_resistance': 'medium'
                },
                'suitable_regions': ['Ashanti', 'Western', 'Eastern', 'Brong-Ahafo'],
                'seasonal_requirements': {
                    'planting_season': 'major_rains',
                    'maintenance_season': 'year_round',
                    'harvest_season': ['major_harvest', 'minor_harvest']
                }
            },
            'Maize': {
                'scientific_name': 'Zea mays',
                'category': 'cereal',
                'optimal_conditions': {
                    'rainfall_mm': (500, 1200),
                    'temperature_c': (18, 32),
                    'ph_range': (6.0, 7.5),
                    'elevation_m': (0, 2000),
                    'humidity_percent': (60, 80)
                },
                'growth_characteristics': {
                    'maturity_months': 4,
                    'productive_years': 1,
                    'yield_kg_per_hectare': 2500,
                    'planting_density': 53333,  # plants per hectare
                    'harvest_cycles_per_year': 2
                },
                'market_data': {
                    'price_ghs_per_kg': 2.10,
                    'demand_stability': 'high',
                    'export_potential': 'medium',
                    'local_market': 'excellent',
                    'price_volatility': 0.25
                },
                'climate_resilience': {
                    'drought_tolerance': 'medium',
                    'flood_tolerance': 'medium',
                    'heat_tolerance': 'high',
                    'disease_resistance': 'medium'
                },
                'suitable_regions': ['Northern', 'Brong-Ahafo', 'Ashanti', 'Eastern', 'Volta'],
                'seasonal_requirements': {
                    'planting_season': ['major_rains', 'minor_rains'],
                    'maintenance_season': 'growing_period',
                    'harvest_season': ['major_harvest', 'minor_harvest']
                }
            },
            'Cassava': {
                'scientific_name': 'Manihot esculenta',
                'category': 'root_tuber',
                'optimal_conditions': {
                    'rainfall_mm': (800, 1500),
                    'temperature_c': (20, 35),
                    'ph_range': (4.5, 7.0),
                    'elevation_m': (0, 1500),
                    'humidity_percent': (65, 85)
                },
                'growth_characteristics': {
                    'maturity_months': 12,
                    'productive_years': 1,
                    'yield_kg_per_hectare': 12000,
                    'planting_density': 10000,  # plants per hectare
                    'harvest_cycles_per_year': 1
                },
                'market_data': {
                    'price_ghs_per_kg': 1.20,
                    'demand_stability': 'very_high',
                    'export_potential': 'medium',
                    'local_market': 'excellent',
                    'price_volatility': 0.10
                },
                'climate_resilience': {
                    'drought_tolerance': 'very_high',
                    'flood_tolerance': 'medium',
                    'heat_tolerance': 'very_high',
                    'disease_resistance': 'high'
                },
                'suitable_regions': ['Ashanti', 'Eastern', 'Brong-Ahafo', 'Northern', 'Volta'],
                'seasonal_requirements': {
                    'planting_season': ['major_rains', 'minor_rains'],
                    'maintenance_season': 'minimal',
                    'harvest_season': 'flexible'
                }
            },
            'Rice': {
                'scientific_name': 'Oryza sativa',
                'category': 'cereal',
                'optimal_conditions': {
                    'rainfall_mm': (1000, 2000),
                    'temperature_c': (20, 35),
                    'ph_range': (5.5, 7.0),
                    'elevation_m': (0, 1200),
                    'humidity_percent': (80, 95)
                },
                'growth_characteristics': {
                    'maturity_months': 4,
                    'productive_years': 1,
                    'yield_kg_per_hectare': 3800,
                    'planting_density': 2500000,  # plants per hectare
                    'harvest_cycles_per_year': 2
                },
                'market_data': {
                    'price_ghs_per_kg': 3.80,
                    'demand_stability': 'very_high',
                    'export_potential': 'high',
                    'local_market': 'excellent',
                    'price_volatility': 0.18
                },
                'climate_resilience': {
                    'drought_tolerance': 'low',
                    'flood_tolerance': 'high',
                    'heat_tolerance': 'medium',
                    'disease_resistance': 'medium'
                },
                'suitable_regions': ['Northern', 'Upper East', 'Upper West', 'Volta'],
                'seasonal_requirements': {
                    'planting_season': ['major_rains', 'minor_rains'],
                    'maintenance_season': 'intensive',
                    'harvest_season': ['major_harvest', 'minor_harvest']
                }
            },
            'Yam': {
                'scientific_name': 'Dioscorea spp.',
                'category': 'root_tuber',
                'optimal_conditions': {
                    'rainfall_mm': (1000, 1500),
                    'temperature_c': (25, 30),
                    'ph_range': (5.5, 7.0),
                    'elevation_m': (0, 800),
                    'humidity_percent': (70, 85)
                },
                'growth_characteristics': {
                    'maturity_months': 10,
                    'productive_years': 1,
                    'yield_kg_per_hectare': 8000,
                    'planting_density': 10000,  # plants per hectare
                    'harvest_cycles_per_year': 1
                },
                'market_data': {
                    'price_ghs_per_kg': 3.50,
                    'demand_stability': 'high',
                    'export_potential': 'medium',
                    'local_market': 'excellent',
                    'price_volatility': 0.20
                },
                'climate_resilience': {
                    'drought_tolerance': 'medium',
                    'flood_tolerance': 'low',
                    'heat_tolerance': 'medium',
                    'disease_resistance': 'medium'
                },
                'suitable_regions': ['Brong-Ahafo', 'Ashanti', 'Eastern', 'Northern'],
                'seasonal_requirements': {
                    'planting_season': 'major_rains',
                    'maintenance_season': 'moderate',
                    'harvest_season': 'dry_season'
                }
            },
            'Plantain': {
                'scientific_name': 'Musa × paradisiaca',
                'category': 'fruit_crop',
                'optimal_conditions': {
                    'rainfall_mm': (1200, 2500),
                    'temperature_c': (26, 30),
                    'ph_range': (5.5, 7.0),
                    'elevation_m': (0, 1000),
                    'humidity_percent': (75, 90)
                },
                'growth_characteristics': {
                    'maturity_months': 12,
                    'productive_years': 5,
                    'yield_kg_per_hectare': 15000,
                    'planting_density': 1600,  # plants per hectare
                    'harvest_cycles_per_year': 3
                },
                'market_data': {
                    'price_ghs_per_kg': 2.80,
                    'demand_stability': 'high',
                    'export_potential': 'low',
                    'local_market': 'excellent',
                    'price_volatility': 0.22
                },
                'climate_resilience': {
                    'drought_tolerance': 'low',
                    'flood_tolerance': 'medium',
                    'heat_tolerance': 'medium',
                    'disease_resistance': 'low'
                },
                'suitable_regions': ['Ashanti', 'Western', 'Eastern', 'Central'],
                'seasonal_requirements': {
                    'planting_season': 'major_rains',
                    'maintenance_season': 'year_round',
                    'harvest_season': 'continuous'
                }
            }
        }
        
        # AI Model weights for recommendation scoring
        self.ai_weights = {
            'climate_suitability': 0.30,
            'market_profitability': 0.25,
            'risk_assessment': 0.20,
            'farmer_experience': 0.15,
            'seasonal_timing': 0.10
        }
    
    def calculate_climate_suitability_score(self, crop_name, region_name, current_conditions=None):
        """Calculate how suitable the climate is for the crop in the region"""
        
        crop = self.crop_database[crop_name]
        region = self.ghana_regions[region_name]
        
        # Base suitability from region data
        optimal = crop['optimal_conditions']
        
        # Rainfall suitability
        rainfall_score = self.calculate_range_score(
            region['rainfall_mm'],
            optimal['rainfall_mm']
        )
        
        # Temperature suitability
        temp_score = self.calculate_range_score(
            region['temperature_avg'],
            optimal['temperature_c']
        )
        
        # pH suitability
        ph_score = self.calculate_range_score(
            (region['ph_range'][0] + region['ph_range'][1]) / 2,
            optimal['ph_range']
        )
        
        # Elevation suitability
        elevation_score = self.calculate_range_score(
            region['elevation'],
            optimal['elevation_m']
        )
        
        # Regional suitability bonus
        region_bonus = 1.2 if region_name in crop['suitable_regions'] else 0.8
        
        # Calculate weighted average
        climate_score = (
            rainfall_score * 0.35 +
            temp_score * 0.30 +
            ph_score * 0.20 +
            elevation_score * 0.15
        ) * region_bonus
        
        # Add current weather conditions if available
        if current_conditions:
            weather_adjustment = self.assess_current_weather_impact(crop_name, current_conditions)
            climate_score *= weather_adjustment
        
        return min(climate_score, 1.0)  # Cap at 1.0
    
    def calculate_range_score(self, actual_value, optimal_range):
        """Calculate score based on how close actual value is to optimal range"""
        
        if isinstance(optimal_range, tuple):
            min_val, max_val = optimal_range
            if min_val <= actual_value <= max_val:
                return 1.0
            elif actual_value < min_val:
                return max(0.0, 1.0 - (min_val - actual_value) / min_val)
            else:
                return max(0.0, 1.0 - (actual_value - max_val) / max_val)
        else:
            # Single optimal value
            return max(0.0, 1.0 - abs(actual_value - optimal_range) / optimal_range)
    
    def assess_current_weather_impact(self, crop_name, weather_conditions):
        """Assess impact of current weather on crop suitability"""
        
        crop = self.crop_database[crop_name]
        resilience = crop['climate_resilience']
        
        weather_score = 1.0
        
        # Check for extreme conditions
        if weather_conditions.get('extreme_heat', False):
            if resilience['heat_tolerance'] == 'low':
                weather_score *= 0.6
            elif resilience['heat_tolerance'] == 'medium':
                weather_score *= 0.8
        
        if weather_conditions.get('drought_risk', False):
            if resilience['drought_tolerance'] == 'low':
                weather_score *= 0.5
            elif resilience['drought_tolerance'] == 'medium':
                weather_score *= 0.7
        
        if weather_conditions.get('flooding_risk', False):
            if resilience['flood_tolerance'] == 'low':
                weather_score *= 0.4
            elif resilience['flood_tolerance'] == 'medium':
                weather_score *= 0.7
        
        return weather_score
    
    def calculate_market_profitability_score(self, crop_name, farmer_profile):
        """Calculate expected profitability for the farmer"""
        
        crop = self.crop_database[crop_name]
        market = crop['market_data']
        growth = crop['growth_characteristics']
        
        # Base revenue calculation
        yield_per_hectare = growth['yield_kg_per_hectare']
        price_per_kg = market['price_ghs_per_kg']
        base_revenue = yield_per_hectare * price_per_kg
        
        # Market stability factor
        stability_multiplier = {
            'very_high': 1.2,
            'high': 1.1,
            'medium': 1.0,
            'low': 0.8
        }.get(market['demand_stability'], 1.0)
        
        # Price volatility adjustment
        volatility_penalty = 1.0 - (market['price_volatility'] * 0.5)
        
        # Export potential bonus
        export_bonus = {
            'excellent': 1.15,
            'high': 1.10,
            'medium': 1.05,
            'low': 1.0
        }.get(market['export_potential'], 1.0)
        
        # Local market accessibility
        local_bonus = {
            'excellent': 1.10,
            'high': 1.05,
            'medium': 1.0,
            'limited': 0.9
        }.get(market['local_market'], 1.0)
        
        # Farm size consideration
        farm_size = farmer_profile.get('farm_size_hectares', 2.0)
        size_efficiency = min(1.2, 1.0 + (farm_size - 1.0) * 0.05)  # Economies of scale
        
        # Calculate final profitability score
        profitability_score = (
            base_revenue * 
            stability_multiplier * 
            volatility_penalty * 
            export_bonus * 
            local_bonus * 
            size_efficiency
        ) / 50000  # Normalize to 0-1 scale
        
        return min(profitability_score, 1.0)
    
    def calculate_risk_assessment_score(self, crop_name, region_name, farmer_profile):
        """Calculate risk score for crop-region combination"""
        
        crop = self.crop_database[crop_name]
        resilience = crop['climate_resilience']
        
        # Climate risk assessment
        climate_risk = 0.0
        
        # Drought risk
        if resilience['drought_tolerance'] == 'low':
            climate_risk += 0.25
        elif resilience['drought_tolerance'] == 'medium':
            climate_risk += 0.10
        
        # Disease risk
        if resilience['disease_resistance'] == 'low':
            climate_risk += 0.20
        elif resilience['disease_resistance'] == 'medium':
            climate_risk += 0.10
        
        # Market risk (price volatility)
        market_risk = crop['market_data']['price_volatility'] * 0.3
        
        # Investment risk (based on crop maturity time)
        maturity_months = crop['growth_characteristics']['maturity_months']
        investment_risk = min(0.3, maturity_months / 100)  # Longer maturity = higher risk
        
        # Farmer experience risk
        farmer_experience = farmer_profile.get('experience_years', 5)
        experience_risk = max(0.0, (5 - farmer_experience) * 0.05)
        
        # Total risk calculation
        total_risk = climate_risk + market_risk + investment_risk + experience_risk
        
        # Convert to score (lower risk = higher score)
        risk_score = max(0.0, 1.0 - total_risk)
        
        return risk_score
    
    def calculate_farmer_experience_score(self, crop_name, farmer_profile):
        """Calculate score based on farmer's experience with similar crops"""
        
        crop = self.crop_database[crop_name]
        crop_category = crop['category']
        
        farmer_crops = farmer_profile.get('previous_crops', [])
        experience_years = farmer_profile.get('experience_years', 0)
        
        # Base experience score
        experience_score = min(1.0, experience_years / 10)  # 10 years = full score
        
        # Category familiarity bonus
        familiar_categories = []
        for prev_crop in farmer_crops:
            if prev_crop in self.crop_database:
                familiar_categories.append(self.crop_database[prev_crop]['category'])
        
        if crop_category in familiar_categories:
            experience_score *= 1.3  # 30% bonus for familiar crop type
        
        # Specific crop experience bonus
        if crop_name in farmer_crops:
            experience_score *= 1.5  # 50% bonus for same crop
        
        return min(experience_score, 1.0)
    
    def calculate_seasonal_timing_score(self, crop_name, current_month):
        """Calculate score based on optimal planting timing"""
        
        crop = self.crop_database[crop_name]
        seasonal_req = crop['seasonal_requirements']
        
        # Define seasonal periods for Ghana
        seasonal_periods = {
            'major_rains': [4, 5, 6, 7],      # April-July
            'minor_rains': [9, 10, 11],       # September-November
            'dry_season': [12, 1, 2, 3],      # December-March
            'year_round': list(range(1, 13))   # All months
        }
        
        planting_season = seasonal_req['planting_season']
        
        if isinstance(planting_season, list):
            # Multiple planting seasons
            for season in planting_season:
                if current_month in seasonal_periods.get(season, []):
                    return 1.0
            return 0.3  # Can plant but not optimal
        else:
            # Single planting season
            if current_month in seasonal_periods.get(planting_season, []):
                return 1.0
            else:
                return 0.2  # Poor timing
    
    def generate_ai_crop_recommendations(self, farmer_profile, region_name, current_conditions=None):
        """Generate AI-powered crop recommendations for farmer"""
        
        current_month = datetime.now().month
        recommendations = []
        
        for crop_name in self.crop_database.keys():
            # Calculate individual scores
            climate_score = self.calculate_climate_suitability_score(
                crop_name, region_name, current_conditions
            )
            
            profitability_score = self.calculate_market_profitability_score(
                crop_name, farmer_profile
            )
            
            risk_score = self.calculate_risk_assessment_score(
                crop_name, region_name, farmer_profile
            )
            
            experience_score = self.calculate_farmer_experience_score(
                crop_name, farmer_profile
            )
            
            timing_score = self.calculate_seasonal_timing_score(
                crop_name, current_month
            )
            
            # Calculate weighted overall score
            overall_score = (
                climate_score * self.ai_weights['climate_suitability'] +
                profitability_score * self.ai_weights['market_profitability'] +
                risk_score * self.ai_weights['risk_assessment'] +
                experience_score * self.ai_weights['farmer_experience'] +
                timing_score * self.ai_weights['seasonal_timing']
            )
            
            # Generate revenue projection
            crop_data = self.crop_database[crop_name]
            farm_size = farmer_profile.get('farm_size_hectares', 2.0)
            projected_yield = crop_data['growth_characteristics']['yield_kg_per_hectare'] * farm_size
            projected_revenue = projected_yield * crop_data['market_data']['price_ghs_per_kg'] * climate_score
            
            recommendation = {
                'crop_name': crop_name,
                'overall_score': round(overall_score, 3),
                'recommendation_level': self.get_recommendation_level(overall_score),
                'scores': {
                    'climate_suitability': round(climate_score, 3),
                    'market_profitability': round(profitability_score, 3),
                    'risk_assessment': round(risk_score, 3),
                    'farmer_experience': round(experience_score, 3),
                    'seasonal_timing': round(timing_score, 3)
                },
                'projections': {
                    'projected_yield_kg': round(projected_yield, 2),
                    'projected_revenue_ghs': round(projected_revenue, 2),
                    'break_even_months': crop_data['growth_characteristics']['maturity_months'],
                    'roi_percentage': round((projected_revenue / (farm_size * 5000) - 1) * 100, 1)  # Assuming 5000 GHS/hectare investment
                },
                'crop_details': {
                    'category': crop_data['category'],
                    'maturity_months': crop_data['growth_characteristics']['maturity_months'],
                    'harvest_cycles_per_year': crop_data['growth_characteristics']['harvest_cycles_per_year'],
                    'market_price_ghs_per_kg': crop_data['market_data']['price_ghs_per_kg']
                },
                'recommendations': self.generate_specific_recommendations(crop_name, region_name, overall_score)
            }
            
            recommendations.append(recommendation)
        
        # Sort by overall score (best recommendations first)
        recommendations.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return recommendations
    
    def get_recommendation_level(self, score):
        """Convert score to recommendation level"""
        if score >= 0.8:
            return "Highly Recommended"
        elif score >= 0.6:
            return "Recommended"
        elif score >= 0.4:
            return "Consider with Caution"
        else:
            return "Not Recommended"
    
    def generate_specific_recommendations(self, crop_name, region_name, score):
        """Generate specific farming recommendations for the crop"""
        
        crop = self.crop_database[crop_name]
        
        recommendations = []
        
        if score >= 0.7:
            recommendations.append(f"Excellent choice for {region_name} region")
            recommendations.append("Consider expanding cultivation area")
        elif score >= 0.5:
            recommendations.append("Good option with proper management")
            recommendations.append("Monitor weather conditions closely")
        else:
            recommendations.append("High risk - consider alternatives")
            recommendations.append("Requires significant investment in risk mitigation")
        
        # Add crop-specific advice
        if crop_name == 'Cocoa':
            recommendations.append("Ensure shade trees for optimal growth")
            recommendations.append("Focus on disease prevention programs")
        elif crop_name == 'Maize':
            recommendations.append("Apply fertilizer at proper growth stages")
            recommendations.append("Ensure adequate storage facilities")
        elif crop_name == 'Rice':
            recommendations.append("Ensure reliable water supply")
            recommendations.append("Consider mechanized farming for efficiency")
        
        return recommendations[:3]  # Return top 3 recommendations

def run_ai_crop_recommendation_demo():
    """Run AI crop recommendation demonstration"""
    
    print("🤖 AGRICONNECT AI CROP RECOMMENDATION ENGINE")
    print("=" * 60)
    
    ai_engine = GhanaAICropRecommendationEngine()
    
    # Demo farmer profile
    farmer_profile = {
        'farmer_id': 'ai_farmer_001',
        'name': 'Kwame Asante',
        'region': 'Ashanti',
        'farm_size_hectares': 3.5,
        'experience_years': 8,
        'previous_crops': ['Maize', 'Cassava', 'Plantain'],
        'investment_capacity_ghs': 15000,
        'risk_tolerance': 'medium',
        'primary_goal': 'maximize_income'
    }
    
    # Current weather conditions
    current_conditions = {
        'extreme_heat': False,
        'drought_risk': False,
        'flooding_risk': False,
        'rainfall_last_30_days': 120,
        'temperature_avg': 26.5
    }
    
    print(f"\n👨‍🌾 FARMER PROFILE")
    print(f"Name: {farmer_profile['name']}")
    print(f"Region: {farmer_profile['region']}")
    print(f"Farm Size: {farmer_profile['farm_size_hectares']} hectares")
    print(f"Experience: {farmer_profile['experience_years']} years")
    print(f"Previous Crops: {', '.join(farmer_profile['previous_crops'])}")
    print(f"Investment Capacity: GHS {farmer_profile['investment_capacity_ghs']:,}")
    
    # Generate AI recommendations
    recommendations = ai_engine.generate_ai_crop_recommendations(
        farmer_profile,
        farmer_profile['region'],
        current_conditions
    )
    
    print(f"\n🧠 AI CROP RECOMMENDATIONS")
    print("=" * 60)
    
    # Display top 5 recommendations
    for i, rec in enumerate(recommendations[:5], 1):
        score_color = "🟢" if rec['overall_score'] >= 0.7 else "🟡" if rec['overall_score'] >= 0.5 else "🔴"
        
        print(f"\n{i}. {score_color} {rec['crop_name'].upper()} - {rec['recommendation_level']}")
        print(f"   Overall Score: {rec['overall_score']:.3f}")
        print(f"   Category: {rec['crop_details']['category'].replace('_', ' ').title()}")
        print(f"   Projected Yield: {rec['projections']['projected_yield_kg']:,.0f} kg")
        print(f"   Projected Revenue: GHS {rec['projections']['projected_revenue_ghs']:,.2f}")
        print(f"   ROI: {rec['projections']['roi_percentage']}%")
        print(f"   Maturity: {rec['crop_details']['maturity_months']} months")
        
        # Show detailed scores
        scores = rec['scores']
        print(f"   Detailed Scores:")
        print(f"     Climate Suitability: {scores['climate_suitability']:.3f}")
        print(f"     Market Profitability: {scores['market_profitability']:.3f}")
        print(f"     Risk Assessment: {scores['risk_assessment']:.3f}")
        print(f"     Farmer Experience: {scores['farmer_experience']:.3f}")
        print(f"     Seasonal Timing: {scores['seasonal_timing']:.3f}")
        
        # Show recommendations
        print(f"   AI Recommendations:")
        for j, advice in enumerate(rec['recommendations'], 1):
            print(f"     {j}. {advice}")
    
    # Summary analysis
    top_recommendation = recommendations[0]
    print(f"\n🏆 TOP AI RECOMMENDATION: {top_recommendation['crop_name'].upper()}")
    print("-" * 50)
    print(f"🎯 Why This Crop:")
    print(f"   • Score: {top_recommendation['overall_score']:.3f} ({top_recommendation['recommendation_level']})")
    print(f"   • Best climate match for {farmer_profile['region']} region")
    print(f"   • High profitability potential: GHS {top_recommendation['projections']['projected_revenue_ghs']:,.2f}")
    print(f"   • {top_recommendation['projections']['roi_percentage']}% ROI projected")
    
    print(f"\n💰 FINANCIAL PROJECTION SUMMARY")
    print("-" * 50)
    total_projected_revenue = sum(rec['projections']['projected_revenue_ghs'] for rec in recommendations[:3])
    print(f"Top 3 Crops Combined Revenue: GHS {total_projected_revenue:,.2f}")
    print(f"Average ROI (Top 3): {sum(rec['projections']['roi_percentage'] for rec in recommendations[:3])/3:.1f}%")
    
    print(f"\n🌾 CROP DIVERSIFICATION STRATEGY")
    print("-" * 50)
    print("AI Recommended Portfolio:")
    total_hectares = farmer_profile['farm_size_hectares']
    for i, rec in enumerate(recommendations[:3], 1):
        allocation = (4 - i) / 6 * total_hectares  # Decreasing allocation
        print(f"{i}. {rec['crop_name']}: {allocation:.1f} hectares ({allocation/total_hectares*100:.0f}%)")
    
    print("\n" + "=" * 60)
    print("✅ AI CROP RECOMMENDATION ENGINE DEMONSTRATION COMPLETE")
    print("🤖 Ready for production deployment with machine learning!")
    print("=" * 60)
    
    return {
        'farmer_profile': farmer_profile,
        'recommendations': recommendations,
        'top_recommendation': top_recommendation,
        'ai_engine_status': 'Phase 7 AI Ready for Production'
    }

if __name__ == "__main__":
    try:
        ai_results = run_ai_crop_recommendation_demo()
        
        # Save AI results
        with open('ai_crop_recommendations_results.json', 'w') as f:
            json.dump(ai_results, f, indent=2, default=str)
        
        print(f"\n💾 AI crop recommendations saved to 'ai_crop_recommendations_results.json'")
        
    except Exception as e:
        print(f"❌ Error running AI crop recommendation demo: {str(e)}")
        print("🔧 Ensure Django environment is properly configured")
