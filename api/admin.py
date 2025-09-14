# backend/api/admin.py (FIXED VERSION)
from django.contrib import admin
from .models import Brochure, Event, TeamLeader, Registration

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'college', 'payment_status', 'registration_fee', 'registration_date']
    list_filter = ['payment_status', 'registration_date', 'college']
    search_fields = ['name', 'email', 'college', 'phone']
    readonly_fields = ['registration_date', 'payment_date', 'stripe_payment_intent_id']
    ordering = ['-registration_date']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Academic Information', {
            'fields': ('college', 'department')
        }),
        ('Payment Information', {
            'fields': ('registration_fee', 'payment_status', 'stripe_payment_intent_id', 'payment_date')
        }),
        ('Registration Information', {
            'fields': ('registration_date',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(Brochure)
class BrochureAdmin(admin.ModelAdmin):
    list_display = ['title', 'upload_date', 'is_active', 'order']
    list_filter = ['is_active', 'upload_date']
    search_fields = ['title', 'description']
    ordering = ['order', '-upload_date']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'pdf_file', 'is_active', 'order')
        }),
    )

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'event_time', 'location', 'order']
    list_filter = ['event_date']
    search_fields = ['title', 'description', 'location']
    ordering = ['order', 'event_date', 'event_time']
    
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'order')
        }),
        ('Schedule', {
            'fields': ('event_date', 'event_time', 'duration', 'location')
        }),
    )

@admin.register(TeamLeader)
class TeamLeaderAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'email', 'order']
    search_fields = ['name', 'role', 'email']
    ordering = ['order']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'role', 'email', 'photo', 'order')
        }),
        ('Additional Information', {
            'fields': ('bio', 'linkedin'),
            'classes': ('collapse',)
        }),
    )
