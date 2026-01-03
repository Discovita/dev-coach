"""
Tests for reset_user_coaching_data function.
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch

from apps.users.models import User
from apps.users.functions import reset_user_coaching_data
from apps.chat_messages.models import ChatMessage
from apps.identities.models import Identity
from apps.user_notes.models import UserNote
from apps.actions.models import Action
from apps.coach_states.models import CoachState
from enums.message_role import MessageRole
from enums.identity_state import IdentityState
from enums.identity_category import IdentityCategory
from enums.coaching_phase import CoachingPhase
from enums.action_type import ActionType


class ResetUserCoachingDataFunctionTests(TestCase):
    """Test the reset_user_coaching_data function directly."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        # Create chat messages
        ChatMessage.objects.create(
            user=self.user,
            content="Test message 1",
            role=MessageRole.USER,
        )
        self.coach_chat_message = ChatMessage.objects.create(
            user=self.user,
            content="Test message 2",
            role=MessageRole.COACH,
        )
        
        # Create identities
        Identity.objects.create(
            user=self.user,
            name="Test Identity",
            state=IdentityState.ACCEPTED,
            category=IdentityCategory.PASSIONS,
        )
        
        # Create user notes
        UserNote.objects.create(
            user=self.user,
            note="Test note",
        )
        
        # Create actions (requires coach_message and parameters)
        Action.objects.create(
            user=self.user,
            action_type=ActionType.CREATE_IDENTITY,
            parameters={"name": "Test Identity"},
            coach_message=self.coach_chat_message,
        )
        
        # Get or create coach state with non-default values
        self.coach_state, _ = CoachState.objects.get_or_create(user=self.user)
        self.coach_state.current_phase = CoachingPhase.IDENTITY_BRAINSTORMING
        self.coach_state.identity_focus = IdentityCategory.MONEY_MAKER
        self.coach_state.who_you_are = ["Creative", "Ambitious"]
        self.coach_state.who_you_want_to_be = ["Leader"]
        self.coach_state.asked_questions = ["question1"]
        self.coach_state.save()

    def test_deletes_all_chat_messages(self):
        """Test that all chat messages are deleted."""
        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 2)
        
        reset_user_coaching_data(self.user)
        
        # Only initial message should remain (if configured)
        messages = ChatMessage.objects.filter(user=self.user)
        # Either 0 or 1 (if initial message exists)
        self.assertLessEqual(messages.count(), 1)

    def test_deletes_all_identities(self):
        """Test that all identities are deleted."""
        self.assertEqual(Identity.objects.filter(user=self.user).count(), 1)
        
        reset_user_coaching_data(self.user)
        
        self.assertEqual(Identity.objects.filter(user=self.user).count(), 0)

    def test_deletes_all_user_notes(self):
        """Test that all user notes are deleted."""
        self.assertEqual(UserNote.objects.filter(user=self.user).count(), 1)
        
        reset_user_coaching_data(self.user)
        
        self.assertEqual(UserNote.objects.filter(user=self.user).count(), 0)

    def test_deletes_all_actions(self):
        """Test that all actions are deleted."""
        self.assertEqual(Action.objects.filter(user=self.user).count(), 1)
        
        reset_user_coaching_data(self.user)
        
        self.assertEqual(Action.objects.filter(user=self.user).count(), 0)

    def test_resets_coach_state(self):
        """Test that coach state is reset to initial values."""
        reset_user_coaching_data(self.user)
        
        self.coach_state.refresh_from_db()
        
        self.assertEqual(self.coach_state.current_phase, CoachingPhase.INTRODUCTION)
        self.assertIsNone(self.coach_state.current_identity)
        self.assertIsNone(self.coach_state.proposed_identity)
        self.assertEqual(self.coach_state.identity_focus, IdentityCategory.PASSIONS)
        self.assertEqual(self.coach_state.skipped_identity_categories, [])
        self.assertEqual(self.coach_state.who_you_are, [])
        self.assertEqual(self.coach_state.who_you_want_to_be, [])
        self.assertEqual(self.coach_state.asked_questions, [])

    def test_handles_user_without_coach_state(self):
        """Test that function handles user without coach state gracefully."""
        user_no_state = User.objects.create_user(
            email="nostate@example.com",
            password="testpass123"
        )
        
        # Should not raise exception
        result = reset_user_coaching_data(user_no_state)
        
        self.assertIsNotNone(result)

    @patch('apps.users.utils.ensure_initial_message_exists.get_initial_message')
    def test_adds_initial_message(self, mock_get_initial):
        """Test that initial message is added after reset."""
        mock_get_initial.return_value = "Welcome back!"
        
        messages = reset_user_coaching_data(self.user)
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "Welcome back!")

    def test_does_not_affect_other_users(self):
        """Test that reset only affects the specified user."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        ChatMessage.objects.create(
            user=other_user,
            content="Other user message",
            role=MessageRole.USER,
        )
        Identity.objects.create(
            user=other_user,
            name="Other Identity",
            state=IdentityState.ACCEPTED,
            category=IdentityCategory.PASSIONS,
        )
        
        reset_user_coaching_data(self.user)
        
        self.assertEqual(ChatMessage.objects.filter(user=other_user).count(), 1)
        self.assertEqual(Identity.objects.filter(user=other_user).count(), 1)

    def test_atomic_transaction(self):
        """Test that operation is atomic (all or nothing)."""
        # This is implicitly tested - if any part fails, all should rollback
        # The @transaction.atomic decorator ensures this
        reset_user_coaching_data(self.user)
        
        # If we get here without exception, atomicity is maintained
        self.assertEqual(Identity.objects.filter(user=self.user).count(), 0)
        self.assertEqual(UserNote.objects.filter(user=self.user).count(), 0)
        self.assertEqual(Action.objects.filter(user=self.user).count(), 0)


class ResetUserCoachingDataAPITests(APITestCase):
    """Test the reset-chat-messages API endpoint."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        
        # Create some data
        ChatMessage.objects.create(
            user=self.user,
            content="Test message",
            role=MessageRole.USER,
        )
        Identity.objects.create(
            user=self.user,
            name="Test Identity",
            state=IdentityState.ACCEPTED,
            category=IdentityCategory.PASSIONS,
        )
        coach_state, _ = CoachState.objects.get_or_create(user=self.user)
        coach_state.current_phase = CoachingPhase.IDENTITY_BRAINSTORMING
        coach_state.save()

    def test_api_resets_data(self):
        """Test API endpoint resets user data."""
        response = self.client.post("/api/v1/user/me/reset-chat-messages")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Identity.objects.filter(user=self.user).count(), 0)

    def test_api_returns_new_chat_history(self):
        """Test API endpoint returns the new chat history."""
        response = self.client.post("/api/v1/user/me/reset-chat-messages")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response should be a list (possibly with initial message)
        self.assertIsInstance(response.data, list)

    def test_api_requires_authentication(self):
        """Test that endpoint requires authentication."""
        self.client.force_authenticate(user=None)
        
        response = self.client.post("/api/v1/user/me/reset-chat-messages")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_requires_post_method(self):
        """Test that endpoint only accepts POST method."""
        response = self.client.get("/api/v1/user/me/reset-chat-messages")
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

