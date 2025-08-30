import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product
from orders.models import Order

User = get_user_model()

class Review(models.Model):
    """
    Multi-dimensional review system for products with comprehensive rating categories.
    Supports verified purchases, blockchain verification, and rich media content.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('hidden', 'Hidden'),
        ('flagged', 'Flagged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
      # Multi-dimensional ratings (1-5 scale)
    overall_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Product Quality Ratings
    quality_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Overall product quality assessment")
    freshness_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Product freshness and condition")
    taste_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Taste and flavor quality")
    packaging_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Packaging quality and presentation")
    value_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Value for money assessment")
    
    # Farmer Reliability Ratings
    delivery_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Delivery time and reliability")
    communication_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Farmer communication quality")
    consistency_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Farmer reliability and consistency")
    farmer_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Overall farmer service rating")
    
    # Service Quality Ratings
    logistics_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Logistics and transportation quality")
    warehouse_handling_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Warehouse handling and storage")
    customer_service_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Customer service experience")
    
    # Sustainability Rating
    sustainability_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, help_text="Environmental impact and sustainable practices")
    
    # Review content
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    pros = models.TextField(blank=True)
    cons = models.TextField(blank=True)
    
    # Verification
    verified_purchase = models.BooleanField(default=False)
    blockchain_verified = models.BooleanField(default=False)
    
    # Media content (stored as JSON arrays of file paths/URLs)
    images = models.JSONField(default=list, blank=True)
    videos = models.JSONField(default=list, blank=True)
    
    # Status and moderation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    flagged_reason = models.TextField(blank=True)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_reviews')
    moderated_at = models.DateTimeField(null=True, blank=True)
    
    # Interaction metrics
    helpful_votes = models.IntegerField(default=0)
    total_votes = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['reviewer', '-created_at']),
            models.Index(fields=['overall_rating']),
            models.Index(fields=['verified_purchase']),
            models.Index(fields=['status']),        ]
        unique_together = ['product', 'reviewer', 'order']  # One review per product per order
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.product.name}"
    
    @property
    def average_detailed_rating(self):
        """Calculate average of all detailed ratings (excluding overall)"""
        ratings = [
            r for r in [
                # Product Quality Ratings
                self.quality_rating, self.freshness_rating, self.taste_rating,
                self.packaging_rating, self.value_rating,
                # Farmer Reliability Ratings
                self.delivery_rating, self.communication_rating, self.consistency_rating,
                self.farmer_rating,
                # Service Quality Ratings
                self.logistics_rating, self.warehouse_handling_rating, self.customer_service_rating,
                # Sustainability Rating
                self.sustainability_rating
            ] if r is not None
        ]
        return sum(ratings) / len(ratings) if ratings else self.overall_rating
    
    @property
    def product_quality_average(self):
        """Calculate average of product quality ratings"""
        quality_ratings = [
            r for r in [
                self.quality_rating, self.freshness_rating, self.taste_rating,
                self.packaging_rating, self.value_rating
            ] if r is not None
        ]
        return sum(quality_ratings) / len(quality_ratings) if quality_ratings else None
    
    @property
    def farmer_reliability_average(self):
        """Calculate average of farmer reliability ratings"""
        reliability_ratings = [
            r for r in [
                self.delivery_rating, self.communication_rating, 
                self.consistency_rating, self.farmer_rating
            ] if r is not None
        ]
        return sum(reliability_ratings) / len(reliability_ratings) if reliability_ratings else None
    
    @property
    def service_quality_average(self):
        """Calculate average of service quality ratings"""
        service_ratings = [
            r for r in [
                self.logistics_rating, self.warehouse_handling_rating, 
                self.customer_service_rating
            ] if r is not None
        ]
        return sum(service_ratings) / len(service_ratings) if service_ratings else None
    
    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio (helpful votes / total votes)"""
        return (self.helpful_votes / self.total_votes) if self.total_votes > 0 else 0.0


class ReviewHelpfulVote(models.Model):
    """
    Track which users found reviews helpful or not helpful.
    Prevents duplicate voting and provides analytics on review quality.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes_detail')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_votes')
    is_helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'user']
        indexes = [
            models.Index(fields=['review', 'is_helpful']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        helpful_text = "helpful" if self.is_helpful else "not helpful"
        return f"{self.user.username} found review {helpful_text}"


class ReviewFlag(models.Model):
    """
    Community moderation system for flagging inappropriate or low-quality reviews.
    Supports multiple flag reasons with detailed descriptions.
    """
    
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake', 'Fake Review'),
        ('offensive', 'Offensive Language'),
        ('irrelevant', 'Irrelevant to Product'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='flags')
    flagger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flags_submitted')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='flags_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['review', 'status']),
            models.Index(fields=['flagger', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Flag: {self.reason} by {self.flagger.username}"


class ReviewResponse(models.Model):
    """
    Farmer responses to customer reviews.
    Enables direct communication and customer service through the review system.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_responses')
    content = models.TextField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['review']),
            models.Index(fields=['responder', '-created_at']),
        ]
    
    def __str__(self):
        return f"Response by {self.responder.username} to review"


class ExpertReview(models.Model):
    """
    Expert reviews from agricultural extension officers, nutritionists, and industry experts.
    Provides authoritative product assessments and recommendations.
    """
    
    EXPERT_TYPE_CHOICES = [
        ('agricultural_officer', 'Agricultural Extension Officer'),
        ('nutritionist', 'Nutritionist'),
        ('food_scientist', 'Food Scientist'),
        ('sustainability_expert', 'Sustainability Expert'),
        ('supply_chain_expert', 'Supply Chain Expert'),
        ('quality_inspector', 'Quality Inspector'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='expert_reviews')
    expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expert_reviews_given')
    expert_type = models.CharField(max_length=50, choices=EXPERT_TYPE_CHOICES)
    
    # Expert ratings
    overall_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    quality_assessment = models.TextField()
    nutritional_value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    sustainability_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    
    # Expert content
    title = models.CharField(max_length=200)
    content = models.TextField()
    recommendations = models.TextField(blank=True)
    certifications = models.JSONField(default=list, blank=True)  # List of certifications/credentials
    
    # Verification
    verified_expert = models.BooleanField(default=False)
    expert_credentials = models.TextField(blank=True)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['expert', '-created_at']),
            models.Index(fields=['expert_type']),
            models.Index(fields=['verified_expert']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f"Expert Review by {self.expert.username} ({self.expert_type})"


class ReviewRecipe(models.Model):
    """
    Recipe suggestions linked to product reviews.
    Enables customers to share cooking ideas and nutritional information.
    """
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='recipes')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes_shared')
    
    # Recipe details
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.JSONField(default=list)  # List of ingredients with quantities
    instructions = models.TextField()
    prep_time = models.IntegerField(help_text="Preparation time in minutes")
    cook_time = models.IntegerField(help_text="Cooking time in minutes")
    servings = models.IntegerField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    
    # Nutritional information
    calories_per_serving = models.IntegerField(null=True, blank=True)
    nutrition_notes = models.TextField(blank=True)
    
    # Media
    images = models.JSONField(default=list, blank=True)
    
    # Metrics
    likes_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['review', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['difficulty']),
        ]
    
    def __str__(self):
        return f"Recipe: {self.title} by {self.author.username}"


class SeasonalInsight(models.Model):
    """
    Seasonal product insights and recommendations based on review data.
    Helps customers understand the best times to purchase specific products.
    """
    
    SEASON_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
        ('dry_season', 'Dry Season'),
        ('rainy_season', 'Rainy Season'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='seasonal_insights')
    season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    
    # Seasonal metrics
    average_rating = models.DecimalField(max_digits=3, decimal_places=2)
    review_count = models.IntegerField()
    quality_score = models.DecimalField(max_digits=3, decimal_places=2)
    availability_score = models.DecimalField(max_digits=3, decimal_places=2)
    price_trend = models.CharField(max_length=20, choices=[
        ('low', 'Low Prices'),
        ('moderate', 'Moderate Prices'),
        ('high', 'High Prices'),
    ])
    
    # Insights
    insights = models.TextField()
    recommendations = models.TextField()
    best_varieties = models.JSONField(default=list, blank=True)
    
    # Regional data
    region = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'season', 'region']
        indexes = [
            models.Index(fields=['product', 'season']),
            models.Index(fields=['season', 'region']),
            models.Index(fields=['average_rating']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.season} insights for {self.region}"


class PeerRecommendation(models.Model):
    """
    Farmer-to-farmer product endorsements and recommendations.
    Enables experienced farmers to recommend products to fellow farmers.
    """
    
    RECOMMENDATION_TYPE_CHOICES = [
        ('product_endorsement', 'Product Endorsement'),
        ('farmer_endorsement', 'Farmer Endorsement'),
        ('practice_sharing', 'Best Practice Sharing'),
        ('equipment_review', 'Equipment Review'),
        ('supplier_recommendation', 'Supplier Recommendation'),
    ]
    
    RECOMMENDATION_STRENGTH_CHOICES = [
        ('highly_recommend', 'Highly Recommend'),
        ('recommend', 'Recommend'),
        ('recommend_with_conditions', 'Recommend with Conditions'),
        ('neutral', 'Neutral'),
        ('not_recommend', 'Do Not Recommend'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recommender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='peer_recommendations_given')
    recommended_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='peer_recommendations_received', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='peer_recommendations')
    farmer_recommended = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farmer_endorsements', null=True, blank=True)
    
    # Recommendation details
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPE_CHOICES, default='product_endorsement')
    recommendation_strength = models.CharField(max_length=25, choices=RECOMMENDATION_STRENGTH_CHOICES, default='recommend')
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Experience-based insights
    experience_duration = models.CharField(max_length=50, blank=True, help_text="How long you've used this product/farmer")
    farm_context = models.TextField(blank=True, help_text="Your farm size, location, and growing conditions")
    results_achieved = models.TextField(blank=True, help_text="Results you achieved using this product/farmer")
    conditions_for_success = models.TextField(blank=True, help_text="Conditions needed for similar success")
    
    # Ratings specific to farmer experience
    value_for_farmers = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Value rating specifically for farmers"
    )
    ease_of_use = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="How easy it is to use/work with"
    )
    yield_impact = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Impact on crop yield (if applicable)"
    )
    cost_effectiveness = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Cost-effectiveness for farming operations"
    )
    
    # Peer validation
    peer_helpful_votes = models.IntegerField(default=0)
    peer_total_votes = models.IntegerField(default=0)
    verified_peer = models.BooleanField(default=False, help_text="Verified as experienced farmer")
    
    # Regional relevance
    relevant_regions = models.JSONField(default=list, blank=True, help_text="Regions where this recommendation applies")
    seasonal_relevance = models.JSONField(default=list, blank=True, help_text="Seasons when this recommendation is most relevant")
    
    # Status and moderation
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_peer_recommendations')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['recommender', '-created_at']),
            models.Index(fields=['recommendation_type']),
            models.Index(fields=['recommendation_strength']),
            models.Index(fields=['verified_peer']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        if self.recommendation_type == 'farmer_endorsement':
            return f"Farmer recommendation: {self.recommender.username} recommends {self.farmer_recommended.username}"
        return f"Product recommendation: {self.recommender.username} recommends {self.product.name}"
    
    @property
    def average_farmer_rating(self):
        """Calculate average of farmer-specific ratings"""
        ratings = [
            self.value_for_farmers, self.ease_of_use, self.cost_effectiveness
        ]
        if self.yield_impact:
            ratings.append(self.yield_impact)
        return sum(ratings) / len(ratings)
    
    @property
    def helpfulness_percentage(self):
        """Calculate how helpful other farmers found this recommendation"""
        if self.peer_total_votes == 0:
            return 0
        return (self.peer_helpful_votes / self.peer_total_votes) * 100


class PeerRecommendationVote(models.Model):
    """
    Voting system for peer recommendations - farmers vote on helpfulness
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recommendation = models.ForeignKey(PeerRecommendation, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='peer_recommendation_votes')
    is_helpful = models.BooleanField()
    comment = models.TextField(blank=True, help_text="Optional comment about the recommendation")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['recommendation', 'voter']
        indexes = [
            models.Index(fields=['recommendation', 'is_helpful']),
        ]
    
    def __str__(self):
        return f"Vote by {self.voter.username} on recommendation {self.recommendation.id}"


class FarmerNetwork(models.Model):
    """
    Farmer networking system - allows farmers to follow each other
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_farmers')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farmer_followers')
    
    # Network relationship details
    trust_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Trust'),
            ('medium', 'Medium Trust'),
            ('high', 'High Trust'),
            ('verified', 'Verified Partner'),
        ],
        default='medium'
    )
    
    # Interaction metrics
    recommendations_received = models.IntegerField(default=0)
    successful_recommendations = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower', 'trust_level']),
            models.Index(fields=['following', 'trust_level']),
        ]
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
    
    @property
    def success_rate(self):
        """Calculate success rate of recommendations from this farmer"""
        if self.recommendations_received == 0:
            return 0
        return (self.successful_recommendations / self.recommendations_received) * 100


class PeerRecommendationInteraction(models.Model):
    """
    Track interactions with peer recommendations (saves, shares, implementations)
    """
    
    INTERACTION_TYPE_CHOICES = [
        ('save', 'Saved for Later'),
        ('share', 'Shared with Others'),
        ('implement', 'Implemented Recommendation'),
        ('request_info', 'Requested More Information'),
        ('connect', 'Connected with Recommender'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recommendation = models.ForeignKey(PeerRecommendation, on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='peer_recommendation_interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES)
    notes = models.TextField(blank=True, help_text="User's notes about the interaction")
    
    # Implementation results (if applicable)
    implementation_success = models.BooleanField(null=True, blank=True)
    implementation_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['recommendation', 'user', 'interaction_type']
        indexes = [
            models.Index(fields=['recommendation', 'interaction_type']),
            models.Index(fields=['user', 'interaction_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.interaction_type} recommendation {self.recommendation.id}"
