from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Registration
from .utils import send_confirmation_emails

@receiver(post_save, sender=Registration)
def registration_created(sender, instance, created, **kwargs):
    """Send notification when registration is created"""
    if created:
        print(f"🔔 New registration: {instance.name} ({instance.email})")
        
        # Send immediate email notification to admin
        from django.core.mail import send_mail
        from django.conf import settings
        
        send_mail(
            f'🔔 New Registration Alert - {instance.name}',
            f'New registration received from {instance.name} ({instance.email}) from {instance.college}',
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True
        )

@receiver(post_save, sender=Registration)
def payment_completed(sender, instance, created, **kwargs):
    """Send emails when payment is completed"""
    if not created and instance.payment_status == 'paid':
        print(f"💳 Payment completed for: {instance.name}")
        send_confirmation_emails(instance)
