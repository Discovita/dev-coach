"""
Tests for services.action_handler.actions.acknowledge_session_video.

The handler appends a `video_key` to `coach_state.shown_videos` after the
user clicks Continue on a session video card. It is a user-button-only
action — the LLM never emits it — and it must be idempotent, validate the
key against the SESSION_VIDEOS registry, and never return a ComponentConfig
(so PR 10's skip-LLM rule does not fire from this action alone).
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.actions.models import Action
from apps.coach_states.models import CoachState
from conftest import create_test_chat_message, create_test_user
from enums.action_type import ActionType
from enums.message_role import MessageRole
from models.components.ComponentConfig import ComponentAction
from services.action_handler.actions.acknowledge_session_video import (
    acknowledge_session_video,
)
from services.action_handler.handler import apply_component_actions
from services.action_handler.models import AcknowledgeSessionVideoParams


class AcknowledgeSessionVideoActionTests(TestCase):
    """Tests for the acknowledge_session_video action handler."""

    def setUp(self):
        self.user = create_test_user()
        self.coach_state = self.user.coach_state
        # Sanity: PR 3 migration default is an empty list
        self.assertEqual(self.coach_state.shown_videos, [])
        self.coach_message = create_test_chat_message(
            self.user, role=MessageRole.COACH, content="Here is a video for you."
        )

    def test_ack_appends_video_key_to_shown_videos(self):
        """Calling the handler should append the key to shown_videos."""
        params = AcknowledgeSessionVideoParams(video_key="welcome_session_intro")

        acknowledge_session_video(self.coach_state, params, self.coach_message)

        self.assertEqual(
            self.coach_state.shown_videos, ["welcome_session_intro"]
        )

    def test_ack_is_idempotent(self):
        """Calling twice with the same key should not duplicate the entry."""
        params = AcknowledgeSessionVideoParams(
            video_key="brainstorming_session_intro"
        )

        acknowledge_session_video(self.coach_state, params, self.coach_message)
        acknowledge_session_video(self.coach_state, params, self.coach_message)

        self.coach_state.refresh_from_db()
        self.assertEqual(
            self.coach_state.shown_videos, ["brainstorming_session_intro"]
        )
        # And only the first call should have written an Action row.
        action_count = Action.objects.filter(
            user=self.user,
            action_type=ActionType.ACKNOWLEDGE_SESSION_VIDEO.value,
        ).count()
        self.assertEqual(action_count, 1)

    def test_ack_persists_to_db(self):
        """The change should survive a refresh_from_db."""
        params = AcknowledgeSessionVideoParams(video_key="get_to_know_session_outro")

        acknowledge_session_video(self.coach_state, params, self.coach_message)

        reloaded = CoachState.objects.get(pk=self.coach_state.pk)
        self.assertIn("get_to_know_session_outro", reloaded.shown_videos)

    def test_ack_raises_validation_error_for_unknown_video_key(self):
        """Unknown keys should raise ValidationError and not touch state."""
        params = AcknowledgeSessionVideoParams(video_key="not_a_real_video_key")

        with self.assertRaises(ValidationError):
            acknowledge_session_video(
                self.coach_state, params, self.coach_message
            )

        self.coach_state.refresh_from_db()
        self.assertEqual(self.coach_state.shown_videos, [])
        self.assertFalse(
            Action.objects.filter(
                user=self.user,
                action_type=ActionType.ACKNOWLEDGE_SESSION_VIDEO.value,
            ).exists()
        )

    def test_ack_returns_no_component_config(self):
        """The handler must return None so the skip-LLM rule does not fire."""
        params = AcknowledgeSessionVideoParams(video_key="i_am_session_intro")

        result = acknowledge_session_video(
            self.coach_state, params, self.coach_message
        )

        self.assertIsNone(result)

    def test_ack_dispatchable_through_action_handler(self):
        """End-to-end: apply_component_actions should route the action to
        our handler and produce the same shown_videos mutation."""
        component_action = ComponentAction(
            action=ActionType.ACKNOWLEDGE_SESSION_VIDEO.value,
            params={"video_key": "commitment_session_intro"},
        )

        apply_component_actions(
            self.coach_state, [component_action], self.coach_message
        )

        self.coach_state.refresh_from_db()
        self.assertIn("commitment_session_intro", self.coach_state.shown_videos)
        self.assertTrue(
            Action.objects.filter(
                user=self.user,
                action_type=ActionType.ACKNOWLEDGE_SESSION_VIDEO.value,
            ).exists()
        )
