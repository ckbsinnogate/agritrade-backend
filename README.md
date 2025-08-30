# AgriTrade - Advanced Agricultural Trading Platform

A comprehensive Django-based platform for agricultural trading, featuring farmer onboarding, product management, marketplace functionality, and AI-powered features.

## Features

- **17 Django Applications** for complete agricultural trading ecosystem
- **Multi-User Types**: Farmers, Processors, Quality Inspectors, Warehouse Managers, etc.
- **Payment Integration**: Paystack integration for secure transactions
- **AI Services**: Disease detection, crop recommendations, weather integration
- **Real-time Communication**: SMS OTP, email notifications
- **Blockchain Traceability**: Product tracking from farm to consumer
- **Admin Dashboard**: Comprehensive management interface

## Production Deployment

This application is configured for deployment on DigitalOcean App Platform with:

- Python 3.11.5 runtime
- PostgreSQL database
- Auto-scaling web service
- Health check monitoring
- Static file serving

## Environment Variables Required

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False for production
- `ALLOWED_HOSTS`: Your domain(s)
- `DATABASE_URL`: PostgreSQL connection string (auto-provided by App Platform)

## Health Check

The application includes a health check endpoint at `/api/health/` for App Platform monitoring.

## API Documentation

API endpoints are available at `/api/v1/` with comprehensive Django REST Framework integration.
