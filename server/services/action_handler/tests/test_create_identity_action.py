"""
Tests for services.action_handler.actions.create_identity.

Integration tests that verify Identity creation, duplicate detection,
and Action audit logging.
"""

from django.test import TestCase

from apps.actions.models import Action
from apps.identities.models import Identity
from apps.users.models import User
from enums.action_type import ActionType
from enums.identity_category import IdentityCategory
from enums.message_role import MessageRole
from conftest import create_test_user, create_test_chat_message
from services.action_handler.actions.create_identity import create_identity
from services.action_handler.models import CreateIdentityParams


class CreateIdentityActionTests(TestCase):
    """Tests for the create_identity action handler."""

    def setUp(self):
        self.user = create_test_user()
        self.coach_state = self.user.coach_state
        self.coach_message = create_test_chat_message(
            self.user, role=MessageRole.COACH, content="Let's create an identity."
        )

    def test_creates_identity_with_correct_fields(self):
        """Should create an Identity with the given name, note, and category."""
        params = CreateIdentityParams(
            name="Creative Visionary",
            note="Loves to create art",
            category=IdentityCategory.PASSIONS,
        )

        identity = create_identity(self.coach_state, params, self.coach_message)

        self.assertIsNotNone(identity)
        self.assertEqual(identity.name, "Creative Visionary")
        self.assertEqual(identity.notes, ["Loves to create art"])
        self.assertEqual(identity.category, IdentityCategory.PASSIONS)
        self.assertEqual(identity.user, self.user)

    def test_logs_action_in_action_table(self):
        """Should create an Action audit record."""
        params = CreateIdentityParams(
            name="Money Maker",
            note="Earns a living",
            category=IdentityCategory.MONEY_MAKER,
        )

        create_identity(self.coach_state, params, self.coach_message)

        action = Action.objects.filter(
            user=self.user, action_type=ActionType.CREATE_IDENTITY.value
        ).first()
        self.assertIsNotNone(action)
        self.assertEqual(action.coach_message, self.coach_message)
        self.assertIn("Money Maker", action.result_summary)

    def test_duplicate_name_returns_none(self):
        """Should return None if an identity with the same name already exists (case-insensitive)."""
        params = CreateIdentityParams(
            name="Creative Visionary",
            note="First attempt",
            category=IdentityCategory.PASSIONS,
        )
        create_identity(self.coach_state, params, self.coach_message)

        duplicate_params = CreateIdentityParams(
            name="creative visionary",
            note="Second attempt",
            category=IdentityCategory.PASSIONS,
        )
        result = create_identity(self.coach_state, duplicate_params, self.coach_message)

        self.assertIsNone(result)
        self.assertEqual(
            Identity.objects.filter(user=self.user, name__iexact="Creative Visionary").count(),
            1,
        )

    def test_duplicate_does_not_create_action_record(self):
        """Duplicate identity should not log an Action."""
        params = CreateIdentityParams(
            name="Duplicate Test",
            note="First",
            category=IdentityCategory.PASSIONS,
        )
        create_identity(self.coach_state, params, self.coach_message)
        initial_count = Action.objects.count()

        duplicate = CreateIdentityParams(
            name="DUPLICATE TEST",
            note="Second",
            category=IdentityCategory.PASSIONS,
        )
        create_identity(self.coach_state, duplicate, self.coach_message)

        self.assertEqual(Action.objects.count(), initial_count)

    def test_different_names_create_separate_identities(self):
        """Identities with different names should both be created."""
        params_a = CreateIdentityParams(
            name="Identity A", note="Note A", category=IdentityCategory.PASSIONS
        )
        params_b = CreateIdentityParams(
            name="Identity B", note="Note B", category=IdentityCategory.HEALTH
        )

        create_identity(self.coach_state, params_a, self.coach_message)
        create_identity(self.coach_state, params_b, self.coach_message)

        self.assertEqual(Identity.objects.filter(user=self.user).count(), 2)
