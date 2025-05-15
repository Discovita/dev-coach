from rest_framework import serializers
from .models import Prompt

class PromptSerializer(serializers.ModelSerializer):
    """
    Serializer for the Prompt model.
    Used in API endpoints to serialize/deserialize Prompt instances.
    Fields:
        - id: UUID of the prompt
        - owner: User who owns the prompt
        - version: Version number of the prompt
        - name: Name of the prompt
        - description: Description of the prompt
        - body: The prompt body
        - required_context_keys: List of required context keys
        - allowed_actions: List of allowed action types
        - is_active: Whether the prompt is active
        - created_at: Timestamp when created
        - updated_at: Timestamp when last updated
    Used by: server/apps/prompts/views.py (PromptViewSet)
    """
    class Meta:
        model = Prompt
        fields = '__all__'  # Expose all fields for API usage 