"""
Tests for apps/coach/utils/get_recent_chat_messages_for_prompt.py

PR 11 changed the contract: the function now returns LLM-facing strings
(oldest → newest) rather than `ChatMessage` instances. Plain-text rows pass
through unchanged; component-bearing rows are rendered as bracketed
narration using `CoachState.shown_videos` and the `Break` table as sources
of truth. Default `count` was raised from 5 → 10.
"""

from django.test import TestCase
from django.utils import timezone

from apps.chat_messages.models import ChatMessage
from apps.coach.utils.get_recent_chat_messages_for_prompt import (
    get_recent_chat_messages_for_prompt,
)
from apps.coach_states.constants.session_videos import SESSION_VIDEOS
from apps.coach_states.models import Break
from apps.users.models import User
from enums.component_type import ComponentType
from enums.message_role import MessageRole


class TestGetRecentChatMessagesForPrompt(TestCase):
    """Tests for get_recent_chat_messages_for_prompt."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="coach@example.com", password="Pass1!"
        )

    def test_returns_empty_list_when_no_messages(self):
        """Returns an empty list when the user has no chat history."""
        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(result, [])

    def test_returns_list_of_strings(self):
        """Returns LLM-facing strings, not ChatMessage instances."""
        ChatMessage.objects.create(
            user=self.user, content="Hello", role=MessageRole.USER
        )
        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], str)

    def test_messages_ordered_oldest_first(self):
        """Messages are returned in chronological order (oldest → newest)."""
        ChatMessage.objects.create(
            user=self.user, content="First", role=MessageRole.USER
        )
        ChatMessage.objects.create(
            user=self.user, content="Second", role=MessageRole.COACH
        )
        ChatMessage.objects.create(
            user=self.user, content="Third", role=MessageRole.USER
        )
        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(result[0], "First")
        self.assertEqual(result[1], "Second")
        self.assertEqual(result[2], "Third")

    def test_default_count_is_10(self):
        """The default `count` parameter is 10 (raised from 5 in PR 11)."""
        for i in range(12):
            ChatMessage.objects.create(
                user=self.user, content=f"Message {i}", role=MessageRole.USER
            )
        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(len(result), 10)

    def test_explicit_count_override_still_works(self):
        """The count parameter controls how many messages are returned."""
        for i in range(15):
            ChatMessage.objects.create(
                user=self.user, content=f"Msg {i}", role=MessageRole.USER
            )
        result = get_recent_chat_messages_for_prompt(self.user, count=3)
        self.assertEqual(len(result), 3)

    def test_does_not_return_other_users_messages(self):
        """Messages belonging to other users are not included."""
        other_user = User.objects.create_user(
            email="other@example.com", password="Pass1!"
        )
        ChatMessage.objects.create(
            user=other_user, content="Not mine", role=MessageRole.USER
        )
        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(result, [])

    def test_normal_text_messages_passed_through_unchanged(self):
        """Plain text rows (no component_config) round-trip as-is."""
        ChatMessage.objects.create(
            user=self.user,
            content="Hello, how are you today?",
            role=MessageRole.USER,
        )
        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(result[0], "Hello, how are you today?")


class TestSessionVideoSerialization(TestCase):
    """Bracketed narration for SESSION_VIDEO rows."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="video@example.com", password="Pass1!"
        )
        self.coach_state = self.user.coach_state

    def _make_video_msg(self, video_key: str, text: str = "") -> ChatMessage:
        return ChatMessage.objects.create(
            user=self.user,
            content=text,
            role=MessageRole.COACH,
            component_config={
                "component_type": ComponentType.SESSION_VIDEO.value,
                "video_key": video_key,
            },
        )

    def test_unacked_session_video_serialized_as_bracketed_not_watched_text(self):
        """A SESSION_VIDEO row whose key isn't in shown_videos renders as 'has not watched'."""
        self._make_video_msg("welcome_session_intro")
        # shown_videos is empty by default
        result = get_recent_chat_messages_for_prompt(self.user)
        expected_name = SESSION_VIDEOS["welcome_session_intro"]["name"]
        self.assertEqual(
            result[0],
            f'[Showed user the "{expected_name}" video. User has not watched it yet.]',
        )

    def test_acked_session_video_serialized_as_bracketed_watched_text(self):
        """A SESSION_VIDEO row whose key IS in shown_videos renders as 'watched it'."""
        self._make_video_msg("welcome_session_intro")
        self.coach_state.shown_videos = ["welcome_session_intro"]
        self.coach_state.save()

        result = get_recent_chat_messages_for_prompt(self.user)
        expected_name = SESSION_VIDEOS["welcome_session_intro"]["name"]
        self.assertEqual(
            result[0],
            f'[Showed user the "{expected_name}" video. User watched it.]',
        )

    def test_serialization_uses_video_name_from_registry(self):
        """The bracket text uses the registry-defined display name, not the key."""
        self._make_video_msg("brainstorming_session_outro")
        result = get_recent_chat_messages_for_prompt(self.user)
        registry_name = SESSION_VIDEOS["brainstorming_session_outro"]["name"]
        self.assertIn(f'"{registry_name}"', result[0])
        # Sanity: the raw key is NOT in the bracket text.
        self.assertNotIn("brainstorming_session_outro", result[0])

    def test_coach_message_with_text_and_component_serialized_with_both(self):
        """When a coach message has both text and a component, both appear (text first)."""
        self._make_video_msg(
            "get_to_know_session_outro",
            text="Beautiful work — take a moment to reflect.",
        )
        result = get_recent_chat_messages_for_prompt(self.user)
        expected_name = SESSION_VIDEOS["get_to_know_session_outro"]["name"]
        self.assertEqual(
            result[0],
            (
                "Beautiful work — take a moment to reflect.\n"
                f'[Showed user the "{expected_name}" video. User has not watched it yet.]'
            ),
        )


class TestSessionBreakSerialization(TestCase):
    """Bracketed narration for SESSION_BREAK rows."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="breaks@example.com", password="Pass1!"
        )

    def _make_break_msg(self) -> ChatMessage:
        return ChatMessage.objects.create(
            user=self.user,
            content="",
            role=MessageRole.COACH,
            component_config={
                "component_type": ComponentType.SESSION_BREAK.value,
            },
        )

    def test_open_break_serialized_as_bracketed_not_returned_text(self):
        """A break with `ended_at IS NULL` renders as 'has not returned yet'."""
        msg = self._make_break_msg()
        Break.objects.create(
            user=self.user,
            triggered_by_session="get_to_know_session",
            coach_message=msg,
        )

        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(
            result[0],
            "[Offered user a break. User has not returned yet.]",
        )

    def test_closed_break_serialized_as_bracketed_returned_text(self):
        """A break with `ended_at` stamped renders as 'took it and returned'."""
        msg = self._make_break_msg()
        Break.objects.create(
            user=self.user,
            triggered_by_session="get_to_know_session",
            coach_message=msg,
            ended_at=timezone.now(),
        )

        result = get_recent_chat_messages_for_prompt(self.user)
        self.assertEqual(
            result[0],
            "[Offered user a break. User took it and returned when ready.]",
        )
