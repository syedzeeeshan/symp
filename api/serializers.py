from rest_framework import serializers
from .models import Brochure, Event, TeamLeader, Registration


class BrochureSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    page_1_image_url = serializers.SerializerMethodField()
    page_2_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Brochure
        fields = [
            'id', 'title', 'description', 'cover_image', 'cover_image_url',
            'page_1_image', 'page_1_image_url', 'page_2_image', 'page_2_image_url',
            'upload_date', 'is_active', 'order'
        ]
    
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
        return None
    
    def get_page_1_image_url(self, obj):
        if obj.page_1_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.page_1_image.url)
        return None
    
    def get_page_2_image_url(self, obj):
        if obj.page_2_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.page_2_image.url)
        return None


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'event_date', 'event_time', 'duration', 'location', 'order']


class TeamLeaderSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamLeader
        fields = ['id', 'name', 'role', 'photo', 'photo_url', 'bio', 'email', 'linkedin', 'order']
    
    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
        return None


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = [
            'id', 'name', 'phone', 'email', 'college', 'department', 
            'registration_fee', 'payment_status', 'registration_date', 'payment_date',
            'num_events', 'selected_events', 'event_details'
        ]
        read_only_fields = ['id', 'payment_status', 'registration_date', 'payment_date', 'num_events']

    def create(self, validated_data):
        # Auto-set num_events based on selected_events length
        selected_events = validated_data.get('selected_events', [])
        validated_data['num_events'] = len(selected_events)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Auto-update num_events when selected_events changes
        selected_events = validated_data.get('selected_events', instance.selected_events)
        validated_data['num_events'] = len(selected_events)
        return super().update(instance, validated_data)


class RegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = [
            'name', 'phone', 'email', 'college', 'department', 
            'selected_events', 'event_details'
        ]
    
    def validate_selected_events(self, value):
        """Validate that selected events are within valid range (1-12)"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Selected events must be a list.")
        
        for event_id in value:
            if not isinstance(event_id, int) or event_id < 1 or event_id > 12:
                raise serializers.ValidationError(f"Invalid event ID: {event_id}. Must be between 1 and 12.")
        
        if len(value) == 0:
            raise serializers.ValidationError("Please select at least one event.")
        
        if len(value) > 12:
            raise serializers.ValidationError("Cannot select more than 12 events.")
        
        return value
    
    def validate_event_details(self, value):
        """Validate event details structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Event details must be a list.")
        
        for detail in value:
            if not isinstance(detail, dict):
                raise serializers.ValidationError("Each event detail must be an object.")
            
            if 'eventId' not in detail or 'subOption' not in detail:
                raise serializers.ValidationError("Each event detail must have eventId and subOption.")
        
        return value
    
    def create(self, validated_data):
        # Auto-set num_events based on selected_events
        selected_events = validated_data.get('selected_events', [])
        validated_data['num_events'] = len(selected_events)
        return super().create(validated_data)


class RegistrationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for payment and receipt purposes"""
    selected_event_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Registration
        fields = [
            'id', 'name', 'phone', 'email', 'college', 'department', 
            'registration_fee', 'payment_status', 'registration_date', 'payment_date',
            'num_events', 'selected_events', 'event_details', 'selected_event_names'
        ]
    
    def get_selected_event_names(self, obj):
        """Map event IDs to names for display purposes"""
        event_names = {
            1: "AI Workshop",
            2: "Blockchain Summit", 
            3: "Web3 Development",
            4: "Cybersecurity Lab",
            5: "Cloud Computing",
            6: "Data Science",
            7: "Startup Pitch",
            8: "Leadership Talk",
            9: "Design Thinking",
            10: "Career Growth",
            11: "Networking Hub",
            12: "Innovation Panel"
        }
        
        selected_events = []
        for event_id in (obj.selected_events or []):
            event_name = event_names.get(event_id, "Unknown Event")
            
            # Find sub-option for this event
            sub_option = ""
            for detail in (obj.event_details or []):
                if detail.get('eventId') == event_id:
                    sub_option = detail.get('subOption', '')
                    break
            
            selected_events.append({
                'id': event_id,
                'name': event_name,
                'sub_option': sub_option
            })
        
        return selected_events
