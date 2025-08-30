"""
AgriConnect Payment System Admin Interface
Comprehensive admin interface for managing payment gateways, transactions, escrow accounts, and disputes
"""

from django.contrib import admin

# Admin site customization
admin.site.site_header = "AgriConnect Payment Administration"
admin.site.site_title = "AgriConnect Payments"
admin.site.index_title = "Payment System Management"

# TODO: Enable admin models once API is stable
# All admin classes temporarily commented out for initial testing
# Will be re-enabled once the basic payment API is working properly
