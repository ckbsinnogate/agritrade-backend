# Generated manually for AgriConnect new user types: Agents, Financial Partners, Government Officials

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create AgentProfile
        migrations.CreateModel(
            name='AgentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(blank=True, max_length=20, unique=True)),
                ('agent_type', models.CharField(choices=[('sales_representative', 'Sales Representative'), ('field_officer', 'Field Officer'), ('area_manager', 'Area Manager'), ('territory_lead', 'Territory Lead')], default='sales_representative', max_length=30)),
                ('assigned_regions', models.JSONField(default=list, help_text='List of assigned regions or territories')),
                ('specialization', models.CharField(choices=[('crops', 'Crop Sales'), ('livestock', 'Livestock Sales'), ('equipment', 'Equipment Sales'), ('general', 'General Sales'), ('technical_support', 'Technical Support')], default='general', max_length=20)),
                ('performance_rating', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Performance rating out of 5.00', max_digits=3, validators=[django.core.validators.MinValueValidator(Decimal('0.00')), django.core.validators.MaxValueValidator(Decimal('5.00'))])),
                ('commission_rate', models.DecimalField(decimal_places=4, default=Decimal('0.0500'), help_text='Commission rate as decimal (e.g., 0.05 for 5%)', max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0.0000')), django.core.validators.MaxValueValidator(Decimal('1.0000'))])),
                ('sales_target_monthly', models.DecimalField(decimal_places=2, help_text='Monthly sales target in local currency', max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('languages_spoken', models.JSONField(default=list, help_text='Languages spoken for customer communication')),
                ('vehicle_access', models.BooleanField(default=False, help_text='Has access to vehicle for field visits')),
                ('employment_status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('probation', 'On Probation'), ('suspended', 'Suspended')], default='active', max_length=20)),
                ('hire_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='agent_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Agent Profile',
                'verbose_name_plural': 'Agent Profiles',
            },
        ),
        
        # Create FinancialPartnerProfile
        migrations.CreateModel(
            name='FinancialPartnerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution_name', models.CharField(max_length=200)),
                ('institution_type', models.CharField(choices=[('bank', 'Commercial Bank'), ('mobile_money', 'Mobile Money Operator'), ('microfinance', 'Microfinance Institution'), ('cooperative', 'Financial Cooperative'), ('insurance', 'Insurance Company'), ('payment_processor', 'Payment Processor')], max_length=30)),
                ('registration_number', models.CharField(blank=True, max_length=100, unique=True)),
                ('license_number', models.CharField(blank=True, max_length=100)),
                ('api_credentials', models.JSONField(default=dict, help_text='API credentials and configuration (encrypted)')),
                ('supported_currencies', models.JSONField(default=list, help_text='List of supported currency codes')),
                ('transaction_limit_daily', models.DecimalField(decimal_places=2, help_text='Daily transaction limit', max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('transaction_limit_monthly', models.DecimalField(decimal_places=2, help_text='Monthly transaction limit', max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('minimum_transaction', models.DecimalField(decimal_places=2, default=Decimal('1.00'), help_text='Minimum transaction amount', max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('transaction_fee_percentage', models.DecimalField(decimal_places=4, default=Decimal('0.0250'), help_text='Transaction fee as percentage', max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0.0000')), django.core.validators.MaxValueValidator(Decimal('1.0000'))])),
                ('integration_status', models.CharField(choices=[('pending', 'Integration Pending'), ('testing', 'Testing Phase'), ('active', 'Active'), ('suspended', 'Suspended'), ('terminated', 'Terminated')], default='pending', max_length=20)),
                ('supported_regions', models.JSONField(default=list, help_text='Regions where services are available')),
                ('contact_person', models.CharField(blank=True, max_length=200)),
                ('technical_contact_email', models.EmailField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='financial_partner_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Financial Partner Profile',
                'verbose_name_plural': 'Financial Partner Profiles',
            },
        ),
        
        # Create GovernmentOfficialProfile
        migrations.CreateModel(
            name='GovernmentOfficialProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(blank=True, max_length=20, unique=True)),
                ('official_title', models.CharField(max_length=200)),
                ('department', models.CharField(max_length=200)),
                ('ministry', models.CharField(choices=[('agriculture', 'Ministry of Agriculture'), ('trade', 'Ministry of Trade'), ('finance', 'Ministry of Finance'), ('health', 'Ministry of Health'), ('environment', 'Ministry of Environment'), ('rural_development', 'Rural Development'), ('food_security', 'Food Security'), ('livestock', 'Livestock Department'), ('fisheries', 'Fisheries Department'), ('forestry', 'Forestry Department'), ('other', 'Other Ministry/Department')], default='agriculture', max_length=30)),
                ('position_level', models.CharField(choices=[('director_general', 'Director General'), ('director', 'Director'), ('deputy_director', 'Deputy Director'), ('manager', 'Manager'), ('senior_officer', 'Senior Officer'), ('officer', 'Officer'), ('assistant', 'Assistant'), ('advisor', 'Advisor'), ('coordinator', 'Coordinator')], max_length=20)),
                ('jurisdiction_level', models.CharField(choices=[('national', 'National Level'), ('regional', 'Regional Level'), ('district', 'District Level'), ('local', 'Local Level')], default='district', max_length=20)),
                ('assigned_regions', models.JSONField(default=list, help_text='Assigned regions, districts, or areas')),
                ('authorization_level', models.CharField(choices=[('view_only', 'View Only'), ('basic_approval', 'Basic Approvals'), ('advanced_approval', 'Advanced Approvals'), ('full_authority', 'Full Authority')], default='view_only', max_length=20)),
                ('areas_of_responsibility', models.JSONField(default=list, help_text='Areas of responsibility and oversight')),
                ('can_approve_subsidies', models.BooleanField(default=False)),
                ('can_approve_certifications', models.BooleanField(default=False)),
                ('can_issue_permits', models.BooleanField(default=False)),
                ('can_conduct_inspections', models.BooleanField(default=False)),
                ('employment_status', models.CharField(choices=[('active', 'Active'), ('temporary', 'Temporary Assignment'), ('transferred', 'Transferred'), ('retired', 'Retired')], default='active', max_length=20)),
                ('appointment_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='government_official_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Government Official Profile',
                'verbose_name_plural': 'Government Official Profiles',
            },
        ),
    ]
