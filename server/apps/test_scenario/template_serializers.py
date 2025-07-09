from rest_framework import serializers

class ForbidExtraFieldsMixin:
    """
    Mixin to forbid extra/unknown fields in template serializers.
    Raises a validation error if any field is present in the input that is not explicitly defined.
    """
    def to_internal_value(self, data):
        allowed = set(self.fields)
        extra = set(data) - allowed
        if extra:
            raise serializers.ValidationError({f: "Unknown field." for f in extra})
        return super().to_internal_value(data)

class TemplateUserSerializer(ForbidExtraFieldsMixin, serializers.Serializer):
    """
    Serializer for user data in a test scenario template.
    Only includes fields required for user creation in a scenario.
    This must be kept in sync with the user creation logic in UserManager and User model.
    """
    email = serializers.EmailField(required=False, help_text="User's email address. If not provided or not unique, a unique test email will be generated automatically.")
    password = serializers.CharField(required=False, help_text="Password for the test user. Not required; always set to 'Coach123!' by the backend.")
    first_name = serializers.CharField(help_text="First name of the user. Required.")
    last_name = serializers.CharField(help_text="Last name of the user. Required.")
    # Optional fields for user creation (add as needed)
    is_active = serializers.BooleanField(required=False, help_text="Is the user active?")
    is_superuser = serializers.BooleanField(required=False, help_text="Is the user a superuser?")
    is_staff = serializers.BooleanField(required=False, help_text="Is the user staff?")
    verification_token = serializers.CharField(required=False, allow_blank=True, help_text="Token for email verification.")
    email_verification_sent_at = serializers.DateTimeField(required=False, allow_null=True, help_text="When the last verification email was sent.")

class TemplateCoachStateSerializer(ForbidExtraFieldsMixin, serializers.Serializer):
    """
    Serializer for coach state data in a test scenario template.
    Only includes fields required for coach state creation.
    """
    current_phase = serializers.CharField(help_text="Current phase of the coaching session. Required.")
    identity_focus = serializers.CharField(help_text="Identity focus for the coaching session. Required.")
    who_you_are = serializers.ListField(child=serializers.CharField(), help_text="List of 'who you are' identities. Required.")
    who_you_want_to_be = serializers.ListField(child=serializers.CharField(), help_text="List of 'who you want to be' identities. Required.")
    skipped_identity_categories = serializers.ListField(child=serializers.CharField(), required=False, help_text="List of skipped identity categories.")
    current_identity = serializers.CharField(required=False, allow_null=True, help_text="ID of the current identity being refined.")
    proposed_identity = serializers.CharField(required=False, allow_null=True, help_text="ID of the currently proposed identity.")
    metadata = serializers.DictField(required=False, help_text="Additional metadata for the coaching session.")

class TemplateIdentitySerializer(ForbidExtraFieldsMixin, serializers.Serializer):
    """
    Serializer for identity data in a test scenario template.
    Only includes fields required for identity creation.
    """
    name = serializers.CharField(help_text="Name of the identity. Required.")
    category = serializers.CharField(help_text="Category this identity belongs to. Required.")
    state = serializers.CharField(help_text="Current state of the identity. Required.")
    affirmation = serializers.CharField(required=False, allow_blank=True, help_text="Affirmation statement for the identity.")
    visualization = serializers.CharField(required=False, allow_blank=True, help_text="Visualization for the identity.")
    notes = serializers.ListField(child=serializers.CharField(), required=False, help_text="List of notes about the identity.")

class TemplateChatMessageSerializer(ForbidExtraFieldsMixin, serializers.Serializer):
    """
    Serializer for chat message data in a test scenario template.
    Only includes fields required for chat message creation.
    """
    role = serializers.CharField(help_text="Role of the message sender (user or coach). Required.")
    content = serializers.CharField(help_text="Content of the message. Required.")
    timestamp = serializers.DateTimeField(required=False, help_text="When the message was sent.")

class TemplateUserNoteSerializer(ForbidExtraFieldsMixin, serializers.Serializer):
    """
    Serializer for user note data in a test scenario template.
    Only includes fields required for user note creation.
    """
    note = serializers.CharField(help_text="A note about the user, extracted from chat. Required.")
    source_message = serializers.CharField(required=False, allow_null=True, help_text="ID of the chat message that prompted this note.")
    created_at = serializers.DateTimeField(required=False, help_text="Timestamp when this note was created.") 