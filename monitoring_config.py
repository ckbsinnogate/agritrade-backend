
# Ghana Production Monitoring Configuration

# Key Performance Indicators (KPIs)
GHANA_KPIs = {
    "target_daily_transactions": 1000,
    "target_monthly_farmers": 5000,
    "target_transaction_value": 500000,  # GHS 500K monthly
    "mobile_money_adoption": 0.70,       # 70% mobile money usage
    "success_rate_target": 0.95          # 95% payment success rate
}

# Alert Thresholds
ALERT_THRESHOLDS = {
    "payment_failure_rate": 0.05,        # Alert if >5% failure rate
    "response_time": 5000,               # Alert if >5 seconds
    "database_connections": 80,          # Alert if >80% DB connections used
    "webhook_failures": 0.02             # Alert if >2% webhook failures
}

# Regional Monitoring (Ghana Regions)
GHANA_REGIONS = [
    "Greater Accra", "Ashanti", "Northern", "Western", "Eastern",
    "Central", "Volta", "Upper East", "Upper West", "Brong Ahafo"
]
