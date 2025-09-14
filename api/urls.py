from django.urls import path
from . import views, payment_views

urlpatterns = [
    # Existing URLs
    path('health/', views.health_check, name='health_check'),
    path('brochures/', views.get_brochures, name='get_brochures'),
    path('events/', views.get_timeline_events, name='get_timeline_events'),
    path('team/', views.get_team_leaders, name='get_team_leaders'),
    path('registration/create/', views.create_registration, name='create_registration'),
    path('registration/<int:registration_id>/', views.get_registration, name='get_registration'),
    
    # NEW Payment URLs
    path('payment/create-order/', payment_views.create_razorpay_order, name='create_razorpay_order'),
    path('payment/verify/', payment_views.verify_razorpay_payment, name='verify_razorpay_payment'),
]
