from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    # Contracts API endpoints
    path('', views.contracts_api_root, name='contracts_api_root'),
    path('contracts/', views.get_contracts, name='get_contracts'),
    path('contracts/<int:contract_id>/', views.contract_detail, name='contract_detail'),
    path('contracts/<int:contract_id>/items/', views.contract_items, name='contract_items'),
]
