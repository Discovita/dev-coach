"""
Serializers for the test_scenario app.

Exports:
    TestScenarioSerializer: Model serializer for TestScenario CRUD.
    ForbidExtraFieldsMixin: Mixin that rejects unknown fields in template data.
    TemplateUserSerializer: Validates user block in a scenario template.
    TemplateCoachStateSerializer: Validates coach_state block in a scenario template.
    TemplateIdentitySerializer: Validates identity entries in a scenario template.
    TemplateChatMessageSerializer: Validates chat_message entries in a scenario template.
    TemplateUserNoteSerializer: Validates user_note entries in a scenario template.
    TemplateActionSerializer: Validates action entries in a scenario template.
"""

from apps.test_scenario.serializers.template_serializers import (
    ForbidExtraFieldsMixin,
    TemplateActionSerializer,
    TemplateBreakSerializer,
    TemplateChatMessageSerializer,
    TemplateCoachStateSerializer,
    TemplateIdentitySerializer,
    TemplateUserNoteSerializer,
    TemplateUserSerializer,
)
from apps.test_scenario.serializers.test_scenario_serializer import (
    TestScenarioSerializer,
)

__all__ = [
    "TestScenarioSerializer",
    "ForbidExtraFieldsMixin",
    "TemplateUserSerializer",
    "TemplateCoachStateSerializer",
    "TemplateIdentitySerializer",
    "TemplateChatMessageSerializer",
    "TemplateUserNoteSerializer",
    "TemplateActionSerializer",
    "TemplateBreakSerializer",
]
