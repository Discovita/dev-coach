"""
Tests for CoachState model.
"""

from django.test import TestCase
from django.utils import timezone

from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from apps.users.models import User
from enums.coaching_phase import CoachingPhase
from enums.identity_category import IdentityCategory
from enums.get_to_know_you_questions import GetToKnowYouQuestions


class CoachStateModelTests(TestCase):
    """Tests for CoachState model methods and properties."""

    def setUp(self):
        """Create test user and coach state."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        # Signal automatically creates CoachState, so use that one
        self.coach_state = self.user.coach_state

    def test_str_returns_user_email_and_phase(self):
        """__str__ should return user email and current phase."""
        expected = f"CoachState for {self.user.email} ({CoachingPhase.INTRODUCTION})"
        self.assertEqual(str(self.coach_state), expected)

    def test_updated_at_is_set_on_creation(self):
        """updated_at should be automatically set when coach state is created."""
        self.assertIsNotNone(self.coach_state.updated_at)
        self.assertLessEqual(self.coach_state.updated_at, timezone.now())

    def test_updated_at_changes_on_update(self):
        """updated_at should change when coach state is updated."""
        original_updated_at = self.coach_state.updated_at
        
        # Wait a tiny bit to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        self.coach_state.current_phase = CoachingPhase.GET_TO_KNOW_YOU
        self.coach_state.save()
        
        self.assertGreater(self.coach_state.updated_at, original_updated_at)

    def test_one_to_one_relationship_with_user(self):
        """CoachState should have OneToOne relationship with User."""
        # Access via forward relation
        self.assertEqual(self.coach_state.user, self.user)
        
        # Access via reverse relation
        self.assertEqual(self.user.coach_state, self.coach_state)

    def test_cannot_create_multiple_coach_states_for_same_user(self):
        """Should not allow creating multiple coach states for the same user."""
        # User already has a coach state from signal, try to create another
        with self.assertRaises(Exception):  # IntegrityError or similar
            CoachState.objects.create(
                user=self.user,
                current_phase=CoachingPhase.GET_TO_KNOW_YOU,
            )

    def test_current_identity_can_be_null(self):
        """current_identity should be nullable."""
        self.assertIsNone(self.coach_state.current_identity)

    def test_current_identity_foreign_key(self):
        """current_identity should link to Identity model."""
        identity = Identity.objects.create(
            user=self.user,
            name="Test Identity",
            category=IdentityCategory.PASSIONS,
        )
        
        self.coach_state.current_identity = identity
        self.coach_state.save()
        
        self.assertEqual(self.coach_state.current_identity, identity)

    def test_current_identity_set_null_on_delete(self):
        """current_identity should be set to NULL when identity is deleted."""
        identity = Identity.objects.create(
            user=self.user,
            name="Test Identity",
            category=IdentityCategory.PASSIONS,
        )
        
        self.coach_state.current_identity = identity
        self.coach_state.save()
        
        identity.delete()
        
        # Refresh from database
        self.coach_state.refresh_from_db()
        self.assertIsNone(self.coach_state.current_identity)

    def test_identity_focus_defaults_to_passions(self):
        """identity_focus should default to PASSIONS."""
        self.assertEqual(self.coach_state.identity_focus, IdentityCategory.PASSIONS)

    def test_identity_focus_can_be_changed(self):
        """identity_focus can be set to different identity categories."""
        self.coach_state.identity_focus = IdentityCategory.HEALTH
        self.coach_state.save()
        
        self.assertEqual(self.coach_state.identity_focus, IdentityCategory.HEALTH)

    def test_skipped_identity_categories_defaults_to_empty_list(self):
        """skipped_identity_categories should default to empty list."""
        self.assertEqual(self.coach_state.skipped_identity_categories, [])

    def test_skipped_identity_categories_can_store_multiple(self):
        """skipped_identity_categories can store multiple categories."""
        self.coach_state.skipped_identity_categories = [
            IdentityCategory.HEALTH,
            IdentityCategory.FAMILY,
        ]
        self.coach_state.save()
        
        self.assertEqual(len(self.coach_state.skipped_identity_categories), 2)
        self.assertIn(IdentityCategory.HEALTH, self.coach_state.skipped_identity_categories)
        self.assertIn(IdentityCategory.FAMILY, self.coach_state.skipped_identity_categories)

    def test_who_you_are_defaults_to_empty_list(self):
        """who_you_are should default to empty list."""
        self.assertEqual(self.coach_state.who_you_are, [])

    def test_who_you_are_can_store_identities(self):
        """who_you_are can store list of identity strings."""
        identities = ["I am creative", "I am a problem solver"]
        self.coach_state.who_you_are = identities
        self.coach_state.save()
        
        self.assertEqual(self.coach_state.who_you_are, identities)

    def test_who_you_want_to_be_defaults_to_empty_list(self):
        """who_you_want_to_be should default to empty list."""
        self.assertEqual(self.coach_state.who_you_want_to_be, [])

    def test_who_you_want_to_be_can_store_identities(self):
        """who_you_want_to_be can store list of identity strings."""
        identities = ["I want to be confident", "I want to be a leader"]
        self.coach_state.who_you_want_to_be = identities
        self.coach_state.save()
        
        self.assertEqual(self.coach_state.who_you_want_to_be, identities)

    def test_asked_questions_defaults_to_empty_list(self):
        """asked_questions should default to empty list."""
        self.assertEqual(self.coach_state.asked_questions, [])

    def test_asked_questions_can_store_question_enums(self):
        """asked_questions can store list of GetToKnowYouQuestions enum values."""
        questions = [
            GetToKnowYouQuestions.HOBBIES_INTERESTS,
            GetToKnowYouQuestions.WORK_LIVING,
        ]
        self.coach_state.asked_questions = questions
        self.coach_state.save()
        
        self.assertEqual(len(self.coach_state.asked_questions), 2)
        self.assertIn(GetToKnowYouQuestions.HOBBIES_INTERESTS, self.coach_state.asked_questions)

    def test_metadata_defaults_to_empty_dict(self):
        """metadata should default to empty dict."""
        self.assertEqual(self.coach_state.metadata, {})

    def test_metadata_can_store_json_data(self):
        """metadata can store flexible JSON data."""
        metadata = {
            "custom_field": "value",
            "nested": {"key": "value"},
            "list": [1, 2, 3],
        }
        self.coach_state.metadata = metadata
        self.coach_state.save()
        
        self.coach_state.refresh_from_db()
        self.assertEqual(self.coach_state.metadata, metadata)

    def test_test_scenario_can_be_null(self):
        """test_scenario should be nullable."""
        self.assertIsNone(self.coach_state.test_scenario)

    def test_proposed_identity_can_be_null(self):
        """proposed_identity should be nullable."""
        self.assertIsNone(self.coach_state.proposed_identity)

    def test_proposed_identity_foreign_key(self):
        """proposed_identity should link to Identity model."""
        identity = Identity.objects.create(
            user=self.user,
            name="Proposed Identity",
            category=IdentityCategory.PASSIONS,
        )
        
        self.coach_state.proposed_identity = identity
        self.coach_state.save()
        
        self.assertEqual(self.coach_state.proposed_identity, identity)

    def test_proposed_identity_set_null_on_delete(self):
        """proposed_identity should be set to NULL when identity is deleted."""
        identity = Identity.objects.create(
            user=self.user,
            name="Proposed Identity",
            category=IdentityCategory.PASSIONS,
        )
        
        self.coach_state.proposed_identity = identity
        self.coach_state.save()
        
        identity.delete()
        
        # Refresh from database
        self.coach_state.refresh_from_db()
        self.assertIsNone(self.coach_state.proposed_identity)
