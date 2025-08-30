from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, Product, ProductVariation, ProductImage, 
    Certification, TraceabilityRecord
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)} if hasattr(Category, 'slug') else {}
    ordering = ['name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary']


class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 0
    fields = ['name', 'value', 'price_adjustment', 'stock_quantity']


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0
    fields = ['certification_type', 'issued_by', 'issue_date', 'expiry_date', 'is_valid']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'seller', 'product_type', 'organic_status', 
        'price_per_unit', 'stock_quantity', 'status', 'created_at'
    ]
    list_filter = [
        'product_type', 'organic_status', 'status', 'category', 
        'origin_country', 'created_at'
    ]
    search_fields = ['name', 'description', 'seller__username', 'seller__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'views_count']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'seller')
        }),
        ('Product Classification', {
            'fields': ('product_type', 'organic_status', 'status')
        }),
        ('Pricing & Inventory', {
            'fields': ('price_per_unit', 'unit', 'minimum_order_quantity', 'stock_quantity')
        }),
        ('Dates', {
            'fields': ('harvest_date', 'expiry_date', 'processing_date')
        }),
        ('Location', {
            'fields': ('origin_country', 'origin_region', 'origin_city')
        }),
        ('Quality & Certifications', {
            'fields': ('quality_grade', 'nutritional_info', 'storage_instructions')
        }),
        ('SEO & Analytics', {
            'fields': ('meta_description', 'meta_keywords', 'views_count'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [ProductImageInline, ProductVariationInline, CertificationInline]
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('category', 'seller')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary', 'image_preview']
    list_filter = ['is_primary']
    search_fields = ['product__name', 'alt_text']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'certification_type', 'issuing_body', 
        'issue_date', 'expiry_date', 'is_valid', 'status_color'
    ]
    list_filter = ['certification_type', 'status', 'issue_date', 'expiry_date']
    search_fields = ['product__name', 'issuing_body', 'certificate_number']
    date_hierarchy = 'issue_date'
    
    def status_color(self, obj):
        color = 'green' if obj.is_valid() else 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            'Valid' if obj.is_valid() else 'Invalid'
        )
    status_color.short_description = 'Status'


@admin.register(TraceabilityRecord)
class TraceabilityRecordAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'stage', 'location', 'actor', 
        'timestamp', 'blockchain_hash'
    ]
    list_filter = ['stage', 'timestamp', 'location']
    search_fields = ['product__name', 'location', 'actor__username']
    readonly_fields = ['blockchain_hash', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('product', 'actor')
