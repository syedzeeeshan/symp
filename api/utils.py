# backend/api/utils.py (REQUIRED FILE)
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def validate_registration_data(data):
    """Validate registration data"""
    errors = {}
    
    # Required fields
    required_fields = ['name', 'phone', 'email', 'college', 'department']
    for field in required_fields:
        if not data.get(field, '').strip():
            errors[field] = f'{field.title()} is required'
    
    # Email validation
    if data.get('email'):
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, data['email']):
            errors['email'] = 'Invalid email format'
    
    # Phone validation
    if data.get('phone'):
        phone_digits = ''.join(filter(str.isdigit, data['phone']))
        if len(phone_digits) != 10:
            errors['phone'] = 'Phone number must be 10 digits'
    
    return errors

def send_confirmation_emails(registration):
    """Send confirmation emails to user and admin"""
    try:
        # Email to user
        user_subject = f'Registration Confirmed - Zehinix Symposium'
        user_html_message = f"""
        <html>
        <body>
            <h2>Registration Confirmed!</h2>
            <p>Dear {registration.name},</p>
            <p>Thank you for registering for the Zehinix Symposium. Your registration has been confirmed.</p>
            
            <h3>Registration Details:</h3>
            <ul>
                <li><strong>Name:</strong> {registration.name}</li>
                <li><strong>Email:</strong> {registration.email}</li>
                <li><strong>Phone:</strong> {registration.phone}</li>
                <li><strong>College:</strong> {registration.college}</li>
                <li><strong>Department:</strong> {registration.department}</li>
                <li><strong>Registration Fee:</strong> ₹{registration.registration_fee}</li>
                <li><strong>Payment Status:</strong> Paid</li>
                <li><strong>Registration Date:</strong> {registration.registration_date.strftime('%B %d, %Y at %I:%M %p')}</li>
            </ul>
            
            <p>We look forward to seeing you at the symposium!</p>
            <p>Best regards,<br>Zehinix Symposium Team</p>
        </body>
        </html>
        """
        
        user_plain_message = strip_tags(user_html_message)
        
        send_mail(
            user_subject,
            user_plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [registration.email],
            html_message=user_html_message,
            fail_silently=True
        )
        
        print(f"✅ User confirmation email sent to {registration.email}")
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
