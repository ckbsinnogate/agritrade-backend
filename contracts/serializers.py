from rest_framework import serializers
from .models import Contract, ContractItem


class ContractItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractItem
        fields = ['id', 'product_name', 'quantity', 'created_at']


class ContractSerializer(serializers.ModelSerializer):
    items = ContractItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Contract
        fields = ['id', 'title', 'description', 'created_at', 'items']


class ContractSummarySerializer(serializers.ModelSerializer):
    """Simplified summary serializer for contract lists"""
    class Meta:
        model = Contract
        fields = ['id', 'title', 'created_at']
