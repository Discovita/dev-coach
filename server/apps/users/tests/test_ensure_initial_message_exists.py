"""
Tests for ensure_initial_message_exists utility.

Covers both the legacy `INITIAL_MESSAGE`-text seed path (flag off) and the
PR 12 SESSION_VIDEO welcome-card seed path (flag on, gated by
`settings.COACHING_PHASE_VIDEOS_ENABLED`).
"""

from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.chat_messages.models import ChatMessage
from apps.chat_messages.utils import ensure_initial_message_exists
from apps.chat_messages.utils.ensure_initial_message_exists import (
    WELCOME_VIDEO_KEY,
)
from apps.users.models import User
from enums.action_type import ActionType
from enums.component_type import ComponentType
from enums.message_role import MessageRole


class EnsureInitialMessageExistsTests(TestCase):
    """Test the ensure_initial_message_exists utility function."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    @patch(
        "apps.chat_messages.utils.ensure_initial_message_exists.INITIAL_MESSAGE",
        "Welcome!",
    )
    def test_adds_message_when_chat_empty(self):
        """Test that message is added when chat is empty."""
        result = ensure_initial_message_exists(self.user)

        self.assertTrue(result)
        messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages.first().content, "Welcome!")
        self.assertEqual(messages.first().role, MessageRole.COACH)

    @patch(
        "apps.chat_messages.utils.ensure_initial_message_exists.INITIAL_MESSAGE",
        "Welcome!",
    )
    def test_does_not_add_when_messages_exist(self):
        """Test that message is not added when chat already has messages."""
        ChatMessage.objects.create(
            user=self.user,
            content="Existing message",
            role=MessageRole.USER,
        )

        result = ensure_initial_message_exists(self.user)

        self.assertFalse(result)
        messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages.first().content, "Existing message")

    @patch(
        "apps.chat_messages.utils.ensure_initial_message_exists.INITIAL_MESSAGE",
        "",
    )
    def test_returns_false_when_no_initial_configured(self):
        """Test that function returns False when no initial message is configured."""
        result = ensure_initial_message_exists(self.user)

        self.assertFalse(result)
        messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(messages.count(), 0)

    @patch(
        "apps.chat_messages.utils.ensure_initial_message_exists.INITIAL_MESSAGE",
        "Welcome!",
    )
    def test_does_not_affect_other_users(self):
        """Test that function only affects the specified user."""
        other_user = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )

        ensure_initial_message_exists(self.user)

        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 1)
        self.assertEqual(ChatMessage.objects.filter(user=other_user).count(), 0)


class EnsureInitialMessageFlagGatedTests(TestCase):
    """
    Test the PR 12 flag-gated behavior of `ensure_initial_message_exists`.

    When `COACHING_PHASE_VIDEOS_ENABLED` is True, the seeded coach message
    carries empty text and a `SESSION_VIDEO(welcome_session_intro)`
    component_config (so the welcome video card renders as the first
    message). When False, behavior matches the legacy `INITIAL_MESSAGE`
    text seed.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email="flag@example.com", password="testpass123"
        )

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=False)
    def test_flag_off_seeds_initial_message_text_only(self):
        """Regression: flag off → first message is the legacy INITIAL_MESSAGE text."""
        result = ensure_initial_message_exists(self.user)

        self.assertTrue(result)
        messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(messages.count(), 1)
        only = messages.first()
        self.assertEqual(only.role, MessageRole.COACH)
        self.assertTrue(only.content)
        self.assertIsNone(only.component_config)

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_flag_on_seeds_session_video_welcome_card_with_empty_text(self):
        """Flag on → first message has empty text + SESSION_VIDEO component_config."""
        result = ensure_initial_message_exists(self.user)

        self.assertTrue(result)
        messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(messages.count(), 1)
        only = messages.first()
        self.assertEqual(only.role, MessageRole.COACH)
        self.assertEqual(only.content, "")
        self.assertIsNotNone(only.component_config)
        self.assertEqual(
            only.component_config["component_type"],
            ComponentType.SESSION_VIDEO.value,
        )

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_flag_on_component_config_uses_welcome_session_intro_key(self):
        """The welcome card's component_config carries the welcome_session_intro video_key."""
        ensure_initial_message_exists(self.user)

        only = ChatMessage.objects.get(user=self.user)
        self.assertEqual(only.component_config["video_key"], WELCOME_VIDEO_KEY)
        self.assertEqual(WELCOME_VIDEO_KEY, "welcome_session_intro")

    @override_settings(
        COACHING_PHASE_VIDEOS_ENABLED=True,
        AWS_STORAGE_BUCKET_NAME="test-bucket-foo",
    )
    def test_flag_on_component_config_embeds_video_name_and_video_url(self):
        """PR 20: welcome card carries video_name + video_url so the FE
        renders without its own registry lookup."""
        ensure_initial_message_exists(self.user)

        only = ChatMessage.objects.get(user=self.user)
        self.assertEqual(only.component_config["video_name"], "Welcome")
        self.assertEqual(
            only.component_config["video_url"],
            "https://test-bucket-foo.s3.amazonaws.com/"
            "media/session-videos/01-welcome-session-intro.mov",
        )

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_flag_on_welcome_card_carries_continue_button_with_ack_action(self):
        """PR 17: the welcome card's buttons[0] is a Continue button
        whose only action is ACKNOWLEDGE_SESSION_VIDEO(welcome_session_intro).

        Without this, the FE modal's Continue click has nothing to dispatch.
        Welcome is intro-only — no START_BREAK — so the action list has length 1.
        """
        ensure_initial_message_exists(self.user)

        only = ChatMessage.objects.get(user=self.user)
        buttons = only.component_config["buttons"]
        self.assertIsNotNone(buttons)
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0]["label"], "Continue")
        actions = buttons[0]["actions"]
        self.assertEqual(len(actions), 1)
        self.assertEqual(
            actions[0]["action"], ActionType.ACKNOWLEDGE_SESSION_VIDEO.value
        )
        self.assertEqual(actions[0]["params"], {"video_key": WELCOME_VIDEO_KEY})

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)
    def test_idempotent_when_initial_message_already_exists_flag_on(self):
        """Calling twice with the flag on does not create a second message."""
        first = ensure_initial_message_exists(self.user)
        second = ensure_initial_message_exists(self.user)

        self.assertTrue(first)
        self.assertFalse(second)
        self.assertEqual(
            ChatMessage.objects.filter(user=self.user).count(), 1
        )

    @override_settings(COACHING_PHASE_VIDEOS_ENABLED=False)
    def test_idempotent_when_initial_message_already_exists_flag_off(self):
        """Calling twice with the flag off does not create a second message."""
        first = ensure_initial_message_exists(self.user)
        second = ensure_initial_message_exists(self.user)

        self.assertTrue(first)
        self.assertFalse(second)
        self.assertEqual(
            ChatMessage.objects.filter(user=self.user).count(), 1
        )
