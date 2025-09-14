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
    """Send confirmation emails to user with event details"""
    try:
        # Event mapping
        event_names = {
            1: "AI Workshop", 2: "Blockchain Summit", 3: "Web3 Development",
            4: "Cybersecurity Lab", 5: "Cloud Computing", 6: "Data Science",
            7: "Startup Pitch", 8: "Leadership Talk", 9: "Design Thinking",
            10: "Career Growth", 11: "Networking Hub", 12: "Innovation Panel"
        }
        
        # Build selected events list
        selected_events_html = ""
        selected_events = registration.selected_events or []
        
        if selected_events:
            selected_events_html = "<h3>🎯 Your Selected Events:</h3><ul>"
            for event_id in selected_events:
                event_name = event_names.get(event_id, f"Event #{event_id}")
                
                # Find sub-option for this event
                sub_option = ""
                for detail in (registration.event_details or []):
                    if detail.get('eventId') == event_id:
                        sub_option = f" - {detail.get('subOption', '')}"
                        break
                
                selected_events_html += f"<li><strong>{event_name}</strong>{sub_option}</li>"
            selected_events_html += "</ul>"
        else:
            selected_events_html = "<p><em>No events selected</em></p>"

        # Email to user
        user_subject = f'Registration Confirmed - Zehinix Symposium 2025'
        user_html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #B8860B; text-align: center;">🎉 Registration Confirmed!</h2>
                <p>Dear <strong>{registration.name}</strong>,</p>
                <p>Thank you for registering for the <strong>Zehinix Symposium 2025</strong>! Your registration has been confirmed and we're excited to have you join us.</p>
                
                {selected_events_html}
                
                <h3>📋 Registration Details:</h3>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin: 8px 0;"><strong>📝 Name:</strong> {registration.name}</li>
                        <li style="margin: 8px 0;"><strong>📧 Email:</strong> {registration.email}</li>
                        <li style="margin: 8px 0;"><strong>📱 Phone:</strong> {registration.phone}</li>
                        <li style="margin: 8px 0;"><strong>🏫 College:</strong> {registration.college}</li>
                        <li style="margin: 8px 0;"><strong>🎓 Department:</strong> {registration.department}</li>
                        <li style="margin: 8px 0;"><strong>💰 Registration Fee:</strong> ₹{registration.registration_fee}</li>
                        <li style="margin: 8px 0;"><strong>✅ Payment Status:</strong> <span style="color: green;">Paid</span></li>
                        <li style="margin: 8px 0;"><strong>📅 Registration Date:</strong> {registration.registration_date.strftime('%B %d, %Y at %I:%M %p')}</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="background: linear-gradient(45deg, #FFD700, #FFA500); color: #1a1a1a; padding: 15px; border-radius: 8px; font-weight: bold;">
                        🎊 We look forward to seeing you at the symposium! 🎊
                    </p>
                </div>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>Zehinix Symposium Team</strong><br>
                    <em>Innovation • Technology • Future</em>
                </p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666; text-align: center;">
                    Please save this email as your registration confirmation.
                </p>
            </div>
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
