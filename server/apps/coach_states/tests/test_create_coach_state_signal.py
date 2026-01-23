"""
Tests for create_coach_state_for_new_user signal handler.
"""

from django.test import TestCase

from apps.coach_states.models import CoachState
from apps.users.models import User
from enums.coaching_phase import CoachingPhase


class CreateCoachStateSignalTests(TestCase):
    """Tests for create_coach_state_for_new_user signal handler."""

    def test_creates_coach_state_for_new_user(self):
        """Creating a new user should auto-create CoachState."""
        user = User.objects.create_user(
            email="newuser@example.com",
            password="testpass123",
        )
        
        # Signal should have created the coach state
        self.assertTrue(hasattr(user, "coach_state"))
        self.assertIsInstance(user.coach_state, CoachState)

    def test_coach_state_has_correct_default_phase(self):
        """CoachState should be created with INTRODUCTION phase."""
        user = User.objects.create_user(
            email="newuser@example.com",
            password="testpass123",
        )
        
        self.assertEqual(user.coach_state.current_phase, CoachingPhase.INTRODUCTION)

    def test_does_not_create_coach_state_on_user_update(self):
        """Updating an existing user should not create a new coach state."""
        user = User.objects.create_user(
            email="existing@example.com",
            password="testpass123",
        )
        
        # Get initial count
        initial_count = CoachState.objects.count()
        
        # Update user
        user.first_name = "Updated"
        user.save()
        
        # Count should not have changed
        self.assertEqual(CoachState.objects.count(), initial_count)

    def test_does_not_duplicate_coach_state(self):
        """Signal should not create duplicate coach state if one already exists."""
        user = User.objects.create_user(
            email="newuser@example.com",
            password="testpass123",
        )
        
        # Get the coach state created by signal
        coach_state_id = user.coach_state.id
        
        # Manually save user again (should not trigger creation)
        user.save()
        
        # Should still be the same coach state
        user.refresh_from_db()
        self.assertEqual(user.coach_state.id, coach_state_id)
        
        # Should only be one coach state for this user
        self.assertEqual(CoachState.objects.filter(user=user).count(), 1)

    def test_each_user_gets_own_coach_state(self):
        """Each new user should get their own coach state."""
        user1 = User.objects.create_user(
            email="user1@example.com",
            password="testpass123",
        )
        user2 = User.objects.create_user(
            email="user2@example.com",
            password="testpass123",
        )
        
        # Each should have their own coach state
        self.assertIsNotNone(user1.coach_state)
        self.assertIsNotNone(user2.coach_state)
        self.assertNotEqual(user1.coach_state.id, user2.coach_state.id)

    def test_coach_state_has_default_values(self):
        """CoachState should be created with appropriate default values."""
        user = User.objects.create_user(
            email="newuser@example.com",
            password="testpass123",
        )
        
        coach_state = user.coach_state
        
        # Check defaults
        self.assertEqual(coach_state.current_phase, CoachingPhase.INTRODUCTION)
        self.assertIsNone(coach_state.current_identity)
        self.assertEqual(coach_state.skipped_identity_categories, [])
        self.assertEqual(coach_state.who_you_are, [])
        self.assertEqual(coach_state.who_you_want_to_be, [])
        self.assertEqual(coach_state.asked_questions, [])
        self.assertEqual(coach_state.metadata, {})
        self.assertIsNone(coach_state.test_scenario)
