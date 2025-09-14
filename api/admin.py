from django.contrib import admin
from .models import Brochure, Event, TeamLeader, Registration

@admin.register(Brochure)
class BrochureAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_active', 'order', 'upload_date')
    list_filter = ('is_active', 'upload_date')
    search_fields = ('title', 'description')
    readonly_fields = ('upload_date',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'event_date', 'event_time', 'order')
    list_filter = ('event_date',)
    search_fields = ('title', 'description')

@admin.register(TeamLeader)
class TeamLeaderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'role', 'order')
    search_fields = ('name', 'role')

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'college', 'payment_status', 'registration_date', 'num_events')
    list_filter = ('payment_status', 'registration_date', 'college')
    search_fields = ('name', 'email', 'phone', 'college')
    readonly_fields = ('registration_date', 'payment_date', 'num_events', 'selected_event_names')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone', 'college', 'department')
        }),
        ('Event Selection', {
            'fields': ('selected_events', 'event_details', 'num_events', 'selected_event_names'),
            'description': 'Events selected by the user'
        }),
        ('Payment Information', {
            'fields': ('registration_fee', 'payment_status', 'payment_id', 'stripe_payment_intent_id', 'payment_date')
        }),
        ('Timestamps', {
            'fields': ('registration_date',)
        }),
    )
    
    def selected_event_names(self, obj):
        """Display selected event names in a readable format"""
        if not obj.selected_events:
            return "No events selected"
        
        event_names = {
            1: "AI Workshop", 2: "Blockchain Summit", 3: "Web3 Development",
            4: "Cybersecurity Lab", 5: "Cloud Computing", 6: "Data Science",
            7: "Startup Pitch", 8: "Leadership Talk", 9: "Design Thinking",
            10: "Career Growth", 11: "Networking Hub", 12: "Innovation Panel"
        }
        
        selected_names = []
        for event_id in obj.selected_events:
            event_name = event_names.get(event_id, f"Event {event_id}")
            
            # Find sub-option for this event
            sub_option = ""
            for detail in (obj.event_details or []):
                if detail.get('eventId') == event_id:
                    sub_option = f" - {detail.get('subOption', '')}"
                    break
            
            selected_names.append(f"{event_name}{sub_option}")
        
        return "\n".join([f"• {name}" for name in selected_names])
    
    selected_event_names.short_description = "Selected Events"
    selected_event_names.allow_tags = True
    
    def get_readonly_fields(self, request, obj=None):
        """Make payment fields readonly after payment is made"""
        readonly = list(self.readonly_fields)
        if obj and obj.payment_status == 'paid':
            readonly.extend(['payment_status', 'payment_id', 'stripe_payment_intent_id'])
        return readonly
