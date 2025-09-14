# backend/api/payment_views.py (COMPLETE RAZORPAY VERSION)
import razorpay
import json
import hmac
import hashlib
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Registration
from .utils import send_confirmation_emails

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@api_view(['POST'])
@permission_classes([AllowAny])
def create_razorpay_order(request):
    """Create Razorpay order for registration payment"""
    try:
        registration_id = request.data.get('registration_id')
        
        if not registration_id:
            return Response({
                'success': False,
                'error': 'Registration ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        registration = Registration.objects.get(id=registration_id)
        
        # Amount in paise (₹500 = 50000 paise)
        amount = int(registration.registration_fee * 100)
        
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1'  # Auto-capture payment
        })
        
        # Store order ID in registration
        registration.razorpay_order_id = razorpay_order['id']
        registration.save()
        
        return Response({
            'success': True,
            'order_id': razorpay_order['id'],
            'amount': amount,
            'currency': 'INR',
            'key': settings.RAZORPAY_KEY_ID,
            'name': 'Zehinix Symposium',
            'description': f'Registration for {registration.name}',
            'prefill': {
                'name': registration.name,
                'email': registration.email,
                'contact': registration.phone
            }
        })
        
    except Registration.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Registration not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Order creation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_razorpay_payment(request):
    """Verify Razorpay payment and update registration status"""
    try:
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response({
                'success': False,
                'error': 'Missing payment parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            return Response({
                'success': False,
                'error': 'Payment signature verification failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find registration by order ID
        registration = Registration.objects.get(razorpay_order_id=razorpay_order_id)
        
        # Update registration
        registration.payment_status = 'paid'
        registration.razorpay_payment_id = razorpay_payment_id
        registration.razorpay_signature = razorpay_signature
        registration.payment_date = timezone.now()
        registration.save()
        
        # Send confirmation emails
        send_confirmation_emails(registration)
        
        return Response({
            'success': True,
            'message': 'Payment verified successfully',
            'registration_id': registration.id
        })
        
    except Registration.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Registration not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Payment verification failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
def razorpay_webhook(request):
    """Handle Razorpay webhooks"""
    webhook_secret = settings.RAZORPAY_KEY_SECRET.encode()
    webhook_signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')
    
    try:
        # Verify webhook signature
        payload = request.body
        expected_signature = hmac.new(
            webhook_secret,
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_signature, webhook_signature):
            return HttpResponse(status=400)
        
        # Process webhook data
        webhook_data = json.loads(payload)
        event = webhook_data.get('event')
        
        if event == 'payment.captured':
            payment_entity = webhook_data['payload']['payment']['entity']
            order_id = payment_entity['order_id']
            payment_id = payment_entity['id']
            
            try:
                registration = Registration.objects.get(razorpay_order_id=order_id)
                if registration.payment_status != 'paid':
                    registration.payment_status = 'paid'
                    registration.razorpay_payment_id = payment_id
                    registration.payment_date = timezone.now()
                    registration.save()
                    
                    # Send emails if not already sent
                    send_confirmation_emails(registration)
            except Registration.DoesNotExist:
                pass
        
        return HttpResponse(status=200)
        
    except Exception as e:
        return HttpResponse(status=400)
