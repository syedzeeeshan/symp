from django.db import models
from django.utils import timezone
# Remove this line: from django.contrib.postgres.fields import ArrayField


class Brochure(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Original PDF (optional, for backup)
    pdf_file = models.FileField(upload_to='brochures/pdfs/', blank=True, null=True)
    
    # Cover image for circular button
    cover_image = models.ImageField(upload_to='brochures/covers/', blank=True, null=True)
    
    # Page images for card flip detailed view
    page_1_image = models.ImageField(upload_to='brochures/pages/', blank=True, null=True)
    page_2_image = models.ImageField(upload_to='brochures/pages/', blank=True, null=True)
    
    upload_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', '-upload_date']


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateField()
    event_time = models.TimeField()
    duration = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', 'event_date', 'event_time']


class TeamLeader(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.role}"

    class Meta:
        ordering = ['order']


class Registration(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    
    # Personal Information
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    college = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    
    # Payment Information
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_id = models.CharField(max_length=100, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    registration_date = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Event Selection Fields (PERFECT FOR MONGODB)
    num_events = models.PositiveIntegerField(default=0)
    selected_events = models.JSONField(
        default=list,
        blank=True,
        help_text="List of event IDs selected by user (works perfectly with MongoDB)"
    )
    event_details = models.JSONField(
        default=list,
        blank=True,
        help_text="Detailed event selections with sub-options (MongoDB native)"
    )
    
    def save(self, *args, **kwargs):
        # Auto-update num_events based on selected_events
        if isinstance(self.selected_events, list):
            self.num_events = len(self.selected_events)
        else:
            self.num_events = 0
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.email} ({self.payment_status})"

    class Meta:
        ordering = ['-registration_date']
        db_table = 'registrations'
