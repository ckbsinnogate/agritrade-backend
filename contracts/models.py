from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Contract(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class ContractItem(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product_name} - {self.contract.title}"
