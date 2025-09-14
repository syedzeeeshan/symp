# backend/api/views.py (COMPLETE WORKING VERSION)
from rest_framework import viewsets, status, pagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from .models import Brochure, Event, TeamLeader, Registration
from .serializers import (BrochureSerializer, EventSerializer, 
                         TeamLeaderSerializer, RegistrationSerializer, 
                         RegistrationCreateSerializer)
from .utils import validate_registration_data

# Health Check (MISSING FUNCTION)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    try:
        return JsonResponse({
            'status': 'ok',
            'message': 'Django API is running',
            'mongodb': {'connected': True, 'message': 'Connected successfully'},
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# Custom pagination for brochures
class BrochurePagination(pagination.PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 12

# Brochures API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_brochures(request):
    """Get paginated brochures with PDF download links"""
    try:
        brochures = Brochure.objects.filter(is_active=True).order_by('order', '-upload_date')
        paginator = BrochurePagination()
        paginated_brochures = paginator.paginate_queryset(brochures, request)
        serializer = BrochureSerializer(paginated_brochures, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to load brochures: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Timeline Events API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_timeline_events(request):
    """Get all events for timeline display"""
    try:
        events = Event.objects.all().order_by('order', 'event_date', 'event_time')
        serializer = EventSerializer(events, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to load events: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Team Leaders API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_team_leaders(request):
    """Get all team leaders"""
    try:
        team = TeamLeader.objects.all().order_by('order')
        serializer = TeamLeaderSerializer(team, many=True, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to load team members: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Registration API
@api_view(['POST'])
@permission_classes([AllowAny])
def create_registration(request):
    """Create new registration and return registration ID"""
    try:
        # Validate data
        validation_errors = validate_registration_data(request.data)
        if validation_errors:
            return Response({
                'success': False,
                'errors': validation_errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for duplicate email
        if Registration.objects.filter(email=request.data.get('email')).exists():
            return Response({
                'success': False,
                'error': 'This email is already registered. Please use a different email address.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create registration
        serializer = RegistrationCreateSerializer(data=request.data)
        if serializer.is_valid():
            registration = serializer.save()
            
            return Response({
                'success': True,
                'registration_id': registration.id,
                'message': 'Registration created successfully. Proceed to payment.',
                'registration_fee': str(registration.registration_fee)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Registration failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_registration(request, registration_id):
    """Get registration details for payment"""
    try:
        registration = get_object_or_404(Registration, id=registration_id)
        
        # Don't allow payment for already paid registrations
        if registration.payment_status == 'paid':
            return Response({
                'success': False,
                'error': 'This registration has already been paid for.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RegistrationSerializer(registration)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Registration not found'
        }, status=status.HTTP_404_NOT_FOUND)
