from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

User = get_user_model()


class Contract(models.Model):
    CONTRACT_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    CONTRACT_TYPE_CHOICES = [
        ('supply', 'Supply Agreement'),
        ('purchase', 'Purchase Order'),
        ('service', 'Service Contract'),
        ('lease', 'Lease Agreement'),
    ]
    
    title = models.CharField(max_length=200)
    contract_number = models.CharField(max_length=50, unique=True)
    institution = models.ForeignKey(
        'users.InstitutionProfile',
        on_delete=models.CASCADE,
        related_name='contracts'
    )
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='supplier_contracts'
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer_contracts'
    )
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES, default='supply')
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS_CHOICES, default='draft')
    start_date = models.DateField()
    end_date = models.DateField()
    total_value = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_contracts'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['contract_number']),
        ]

    def __str__(self):
        return f"{self.contract_number} - {self.title}"

    @property
    def is_active(self):
        today = timezone.now().date()
        return (
            self.status == 'active' and 
            self.start_date <= today <= self.end_date
        )

    @property
    def days_remaining(self):
        if self.status == 'active':
            today = timezone.now().date()
            if today <= self.end_date:
                return (self.end_date - today).days
        return 0


class ContractItem(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_date = models.DateField(null=True, blank=True)
    delivered_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.product_name} - {self.contract.contract_number}"

    @property
    def pending_quantity(self):
        return max(0, self.quantity - self.delivered_quantity)

    def save(self, *args, **kwargs):
        # Auto-calculate total_price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
