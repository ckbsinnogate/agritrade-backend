from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Contract, ContractItem
from .serializers import ContractSerializer, ContractSummarySerializer, ContractItemSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contracts_api_root(request, format=None):
    """
    API root for contracts endpoints
    """
    return Response({
        'message': 'Contracts API',
        'endpoints': {
            'contracts': '/api/v1/contracts/',
            'contract_detail': '/api/v1/contracts/{id}/',
            'contract_items': '/api/v1/contracts/{id}/items/',
        }
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_contracts(request):
    """
    GET: List all contracts for the user's institution
    POST: Create a new contract
    """
    if request.method == 'GET':
        try:
            # Get user's institution
            institution_profile = getattr(request.user, 'institutionprofile', None)
            if not institution_profile:
                return Response({
                    'error': 'User is not associated with an institution',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)

            # Filter contracts by institution
            contracts = Contract.objects.filter(
                Q(institution=institution_profile) |
                Q(buyer=request.user) |
                Q(supplier=request.user)
            ).select_related('institution', 'supplier', 'buyer').prefetch_related('items')

            # Apply filters
            contract_status = request.query_params.get('status')
            contract_type = request.query_params.get('type')
            search = request.query_params.get('search')

            if contract_status:
                contracts = contracts.filter(status=contract_status)
            if contract_type:
                contracts = contracts.filter(contract_type=contract_type)
            if search:
                contracts = contracts.filter(
                    Q(title__icontains=search) |
                    Q(contract_number__icontains=search) |
                    Q(description__icontains=search)
                )

            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            start = (page - 1) * page_size
            end = start + page_size

            contracts_page = contracts[start:end]
            
            # Use summary serializer for list view
            serializer = ContractSummarySerializer(contracts_page, many=True)

            # Get contract statistics
            stats = contracts.aggregate(
                total_contracts=Count('id'),
                total_value=Sum('total_value'),
                active_contracts=Count('id', filter=Q(status='active')),
                pending_contracts=Count('id', filter=Q(status='pending')),
                completed_contracts=Count('id', filter=Q(status='completed')),
                avg_contract_value=Avg('total_value')
            )

            # Status breakdown
            status_breakdown = list(contracts.values('status').annotate(
                count=Count('id'),
                total_value=Sum('total_value')
            ).order_by('status'))

            return Response({
                'data': serializer.data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': contracts.count(),
                    'has_next': end < contracts.count(),
                    'has_previous': page > 1
                },
                'summary': {
                    'total_contracts': stats['total_contracts'] or 0,
                    'total_value': float(stats['total_value'] or 0),
                    'active_contracts': stats['active_contracts'] or 0,
                    'pending_contracts': stats['pending_contracts'] or 0,
                    'completed_contracts': stats['completed_contracts'] or 0,
                    'average_contract_value': float(stats['avg_contract_value'] or 0),
                },
                'status_breakdown': status_breakdown
            })

        except Exception as e:
            return Response({
                'error': str(e),
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'POST':
        try:
            # Ensure user has institution
            institution_profile = getattr(request.user, 'institutionprofile', None)
            if not institution_profile:
                return Response({
                    'error': 'User is not associated with an institution'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Set institution for the contract
            data = request.data.copy()
            data['institution'] = institution_profile.id
            
            serializer = ContractSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                contract = serializer.save()
                return Response(
                    ContractSerializer(contract).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def contract_detail(request, contract_id):
    """
    GET, PUT, DELETE a specific contract
    """
    try:
        # Get user's institution
        institution_profile = getattr(request.user, 'institutionprofile', None)
        if not institution_profile:
            return Response({
                'error': 'User is not associated with an institution'
            }, status=status.HTTP_400_BAD_REQUEST)        # Get contract with permission check
        contract = Contract.objects.select_related('institution', 'supplier', 'buyer').filter(
            id=contract_id
        ).filter(
            Q(institution=institution_profile) |
            Q(buyer=request.user) |
            Q(supplier=request.user)
        ).first()
        
        if not contract:
            return Response({
                'error': 'Contract not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = ContractSerializer(contract)
            return Response({'data': serializer.data})

        elif request.method == 'PUT':
            serializer = ContractSerializer(
                contract, 
                data=request.data, 
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response({'data': serializer.data})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            contract.delete()
            return Response({
                'message': 'Contract deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)

    except Contract.DoesNotExist:
        return Response({
            'error': 'Contract not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def contract_items(request, contract_id):
    """
    GET: List items for a specific contract
    POST: Add item to contract
    """
    try:
        # Get user's institution
        institution_profile = getattr(request.user, 'institutionprofile', None)
        if not institution_profile:
            return Response({
                'error': 'User is not associated with an institution'
            }, status=status.HTTP_400_BAD_REQUEST)        # Get contract with permission check
        contract = Contract.objects.filter(
            id=contract_id
        ).filter(
            Q(institution=institution_profile) |
            Q(buyer=request.user) |
            Q(supplier=request.user)
        ).first()
        
        if not contract:
            return Response({
                'error': 'Contract not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            items = ContractItem.objects.filter(contract=contract)
            serializer = ContractItemSerializer(items, many=True)
            
            # Get items summary
            items_summary = items.aggregate(
                total_items=Count('id'),
                total_quantity=Sum('quantity'),
                delivered_quantity=Sum('delivered_quantity'),
                total_value=Sum('total_price')
            )

            return Response({
                'data': serializer.data,
                'summary': {
                    'total_items': items_summary['total_items'] or 0,
                    'total_quantity': items_summary['total_quantity'] or 0,
                    'delivered_quantity': items_summary['delivered_quantity'] or 0,
                    'pending_quantity': (items_summary['total_quantity'] or 0) - (items_summary['delivered_quantity'] or 0),
                    'total_value': float(items_summary['total_value'] or 0)
                }
            })

        elif request.method == 'POST':
            data = request.data.copy()
            data['contract'] = contract.id
            
            serializer = ContractItemSerializer(data=data)
            if serializer.is_valid():
                item = serializer.save()
                return Response(
                    ContractItemSerializer(item).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Contract.DoesNotExist:
        return Response({
            'error': 'Contract not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
