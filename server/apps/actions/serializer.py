from rest_framework import serializers
from .models import Action
from apps.chat_messages.serializer import ChatMessageSerializer


class ActionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Action model.
    
    Used in: API responses, admin interface, data validation
    Referenced in: Coach views, action tracking, conversation reconstruction
    """
    
    # Include related coach message data for context
    coach_message = ChatMessageSerializer(read_only=True)
    
    # Human-readable action type display
    action_type_display = serializers.CharField(
        source='get_action_type_display',
        read_only=True,
        help_text="Human-readable action type name."
    )
    
    # Formatted timestamp
    timestamp_formatted = serializers.SerializerMethodField(
        help_text="Timestamp formatted for display."
    )
    
    class Meta:
        model = Action
        fields = [
            'id',
            'user',
            'action_type',
            'action_type_display',
            'parameters',
            'timestamp',
            'timestamp_formatted',
            'coach_message',
            'test_scenario',
        ]
        read_only_fields = [
            'id',
            'timestamp',
            'timestamp_formatted',
            'action_type_display',
        ]
    
    def get_timestamp_formatted(self, obj):
        """
        Return a formatted timestamp string.
        """
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    def validate_parameters(self, value):
        """
        Validate that parameters is a valid JSON object.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Parameters must be a JSON object.")
        return value
    
    def validate(self, data):
        """
        Validate the action data.
        """
        # Ensure coach_message is a coach message, not a user message
        if 'coach_message' in data:
            coach_message = data['coach_message']
            if coach_message.role != 'coach':
                raise serializers.ValidationError(
                    "Actions can only be linked to coach messages."
                )
        
        return data


class ActionListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing actions.
    Used when you need to show many actions without full detail.
    """
    
    action_type_display = serializers.CharField(
        source='get_action_type_display',
        read_only=True,
    )
    
    coach_message_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Action
        fields = [
            'id',
            'action_type',
            'action_type_display',
            'timestamp',
            'coach_message_preview',
        ]
        read_only_fields = fields
    
    def get_coach_message_preview(self, obj):
        """
        Return a preview of the coach message content.
        """
        if obj.coach_message:
            content = obj.coach_message.content
            return content[:100] + "..." if len(content) > 100 else content
        return None


class ActionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new actions.
    Used by the action handler when creating action records.
    """
    
    class Meta:
        model = Action
        fields = [
            'user',
            'action_type',
            'parameters',
            'coach_message',
            'test_scenario',
        ]
    
    def validate_parameters(self, value):
        """
        Validate that parameters is a valid JSON object.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Parameters must be a JSON object.")
        return value
    
    def validate(self, data):
        """
        Validate the action creation data.
        """
        # Ensure coach_message is a coach message
        coach_message = data.get('coach_message')
        if coach_message and coach_message.role != 'coach':
            raise serializers.ValidationError(
                "Actions can only be linked to coach messages."
            )
        
        return data 