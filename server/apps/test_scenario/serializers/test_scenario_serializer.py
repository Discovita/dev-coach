"""
Model serializer for TestScenario CRUD operations.

See: apps/test_scenario/serializers/__init__.py
"""

from rest_framework import serializers

from apps.test_scenario.models import TestScenario


class TestScenarioSerializer(serializers.ModelSerializer):
    """
    Serializer for the TestScenario model.

    Enriches the ``template.user`` block on read with the live user's
    ``id``, ``email``, and default password so the frontend can display
    test-login credentials.
    """

    created_by = serializers.SerializerMethodField()

    class Meta:
        model = TestScenario
        fields = [
            "id",
            "name",
            "description",
            "template",
            "created_at",
            "updated_at",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]

    def get_created_by(self, obj) -> str | None:
        """Return the creator's full name, falling back to email."""
        user = obj.created_by
        if not user:
            return None
        full_name = user.get_full_name()
        return full_name if full_name else user.email

    def to_representation(self, instance):
        """Inject live user credentials into the template on read."""
        data = super().to_representation(instance)
        template = data.get("template", {})
        user = instance.user_set.first()
        if user:
            template_user = template.get("user", {})
            template_user["id"] = str(user.id)
            template_user["email"] = user.email
            template_user["password"] = "Coach123!"
            template["user"] = template_user
        else:
            if "user" not in template:
                template["user"] = {}
        data["template"] = template
        return data
