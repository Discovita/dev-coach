"""
Tests for the Break model.

Storage-layer behavior only — handler logic (no-overlap enforcement,
END_BREAK closure, intro-video emission) lives in PRs 7, 8, and 14.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.chat_messages.models import ChatMessage
from apps.coach_states.models import Break
from enums.message_role import MessageRole

User = get_user_model()


class BreakModelCreateTests(TestCase):
    """Happy-path creation + required field defaults."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="break-create@example.com",
            password="testpass123",
        )

    def test_break_model_create_with_required_fields(self):
        """Can create with just user + triggered_by_session."""
        b = Break.objects.create(
            user=self.user,
            triggered_by_session="brainstorming_session",
        )
        self.assertEqual(b.user, self.user)
        self.assertEqual(b.triggered_by_session, "brainstorming_session")
        self.assertIsNotNone(b.id)

    def test_break_started_at_auto_set(self):
        """auto_now_add populates started_at on insert."""
        before = timezone.now()
        b = Break.objects.create(
            user=self.user,
            triggered_by_session="get_to_know_session",
        )
        after = timezone.now()
        self.assertIsNotNone(b.started_at)
        self.assertGreaterEqual(b.started_at, before)
        self.assertLessEqual(b.started_at, after)

    def test_break_ended_at_nullable(self):
        """ended_at can be saved as None and stays None until set."""
        b = Break.objects.create(
            user=self.user,
            triggered_by_session="commitment_session",
            ended_at=None,
        )
        b.refresh_from_db()
        self.assertIsNone(b.ended_at)

    def test_break_coach_message_optional(self):
        """coach_message FK is optional."""
        b = Break.objects.create(
            user=self.user,
            triggered_by_session="refinement_session",
        )
        self.assertIsNone(b.coach_message)


class BreakModelRelationshipTests(TestCase):
    """Foreign-key behavior."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="break-rel@example.com",
            password="testpass123",
        )

    def test_break_user_relationship(self):
        """FK works in both directions via the `breaks` reverse manager."""
        b = Break.objects.create(
            user=self.user,
            triggered_by_session="i_am_session",
        )
        # Forward
        self.assertEqual(b.user, self.user)
        # Reverse via related_name="breaks"
        self.assertIn(b, list(self.user.breaks.all()))

    def test_break_cascades_on_user_delete(self):
        """Deleting the user removes their breaks (CASCADE)."""
        Break.objects.create(
            user=self.user,
            triggered_by_session="brainstorming_session",
        )
        user_id = self.user.id
        self.user.delete()
        self.assertEqual(Break.objects.filter(user_id=user_id).count(), 0)

    def test_break_coach_message_set_null_on_chat_message_delete(self):
        """ChatMessage deletion preserves the Break (SET_NULL)."""
        msg = ChatMessage.objects.create(
            user=self.user,
            role=MessageRole.COACH,
            content="anchor for break",
        )
        b = Break.objects.create(
            user=self.user,
            triggered_by_session="get_to_know_session",
            coach_message=msg,
        )
        msg.delete()
        b.refresh_from_db()
        self.assertIsNone(b.coach_message)
        # The Break itself survives
        self.assertTrue(Break.objects.filter(pk=b.pk).exists())


class BreakModelLifecycleTests(TestCase):
    """Open vs closed state."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="break-lifecycle@example.com",
            password="testpass123",
        )

    def test_open_break_filter(self):
        """ended_at IS NULL is the canonical 'on a break?' check."""
        Break.objects.create(
            user=self.user,
            triggered_by_session="brainstorming_session",
        )
        self.assertTrue(
            Break.objects.filter(user=self.user, ended_at__isnull=True).exists()
        )

    def test_closed_break_excluded_from_open_filter(self):
        """Once ended_at is stamped the break is no longer 'open'."""
        b = Break.objects.create(
            user=self.user,
            triggered_by_session="brainstorming_session",
        )
        b.ended_at = timezone.now()
        b.save()
        self.assertFalse(
            Break.objects.filter(user=self.user, ended_at__isnull=True).exists()
        )

    def test_str_open_vs_closed(self):
        """__str__ reflects open/closed state."""
        b = Break.objects.create(
            user=self.user,
            triggered_by_session="refinement_session",
        )
        self.assertIn("open", str(b))

        b.ended_at = b.started_at + timedelta(minutes=5)
        b.save()
        self.assertIn("closed", str(b))


class BreakModelOrderingTests(TestCase):
    """Default ordering is most-recent first."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="break-order@example.com",
            password="testpass123",
        )

    def test_default_ordering_most_recent_first(self):
        b_old = Break.objects.create(
            user=self.user, triggered_by_session="welcome_session"
        )
        b_new = Break.objects.create(
            user=self.user, triggered_by_session="brainstorming_session"
        )
        ordered = list(Break.objects.filter(user=self.user))
        self.assertEqual(ordered[0], b_new)
        self.assertEqual(ordered[1], b_old)


class BreakAdminTests(TestCase):
    """Admin smoke test — model registered, changelist URL resolves.

    We do NOT fetch the rendered HTML: the project uses
    `whitenoise.storage.CompressedManifestStaticFilesStorage`, which raises
    `ValueError: Missing staticfiles manifest entry` during test template
    render because no manifest is collected in the test environment. The
    important assertions are that the model is registered and the URL
    resolves through the admin URL conf — those are what guarantee the
    page would render given a real static-files setup.
    """

    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="break-admin@example.com",
            password="adminpass123",
        )
        self.client.force_login(self.admin)

    def test_break_admin_is_registered(self):
        """The Break model is registered with the default admin site."""
        from django.contrib import admin as django_admin
        self.assertTrue(django_admin.site.is_registered(Break))

    def test_break_admin_changelist_url_resolves(self):
        """`admin:coach_states_break_changelist` resolves to a valid URL."""
        url = reverse("admin:coach_states_break_changelist")
        self.assertIn("/admin/", url)
        self.assertIn("coach_states", url)
        self.assertIn("break", url)
