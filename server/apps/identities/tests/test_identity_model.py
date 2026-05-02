"""
Tests for apps.identities.models.Identity.

Verifies model creation, field defaults, constraints, relationships,
and string representation for the core Identity model.
"""

from django.test import TestCase

from apps.identities.models import Identity
from apps.users.models import User
from conftest import create_test_user, create_test_identity
from enums.identity_category import IdentityCategory
from enums.identity_state import IdentityState


class IdentityModelTests(TestCase):
    """Tests for the Identity model."""

    def setUp(self):
        self.user = create_test_user()

    def test_create_identity_with_required_fields(self):
        """Should create an Identity with user and category."""
        identity = Identity.objects.create(
            user=self.user,
            name="Creative Visionary",
            category=IdentityCategory.PASSIONS,
        )
        self.assertIsNotNone(identity.id)
        self.assertEqual(identity.user, self.user)
        self.assertEqual(identity.name, "Creative Visionary")
        self.assertEqual(identity.category, IdentityCategory.PASSIONS)

    def test_id_is_uuid(self):
        """Identity ID should be a UUID."""
        import uuid

        identity = create_test_identity(self.user)
        self.assertIsInstance(identity.id, uuid.UUID)

    def test_default_state_is_proposed(self):
        """Default state should be PROPOSED."""
        identity = Identity.objects.create(
            user=self.user,
            name="Test",
            category=IdentityCategory.PASSIONS,
        )
        self.assertEqual(identity.state, IdentityState.PROPOSED)

    def test_notes_default_to_empty_list(self):
        """notes should default to an empty list."""
        identity = Identity.objects.create(
            user=self.user,
            name="Test",
            category=IdentityCategory.PASSIONS,
        )
        self.assertEqual(identity.notes, [])

    def test_notes_can_store_multiple_entries(self):
        """notes should store a list of strings."""
        notes = ["First note", "Second note", "Third note"]
        identity = Identity.objects.create(
            user=self.user,
            name="Noted Identity",
            category=IdentityCategory.PASSIONS,
            notes=notes,
        )
        identity.refresh_from_db()
        self.assertEqual(identity.notes, notes)

    def test_optional_fields_nullable(self):
        """Optional fields should accept null values."""
        identity = Identity.objects.create(
            user=self.user,
            category=IdentityCategory.PASSIONS,
        )
        self.assertIsNone(identity.name)
        self.assertIsNone(identity.i_am_statement)
        self.assertIsNone(identity.visualization)
        self.assertIsNone(identity.clothing)
        self.assertIsNone(identity.mood)
        self.assertIsNone(identity.setting)

    def test_i_am_statement_can_be_set(self):
        """i_am_statement should accept text."""
        identity = create_test_identity(
            self.user, i_am_statement="I am a creative force"
        )
        self.assertEqual(identity.i_am_statement, "I am a creative force")

    def test_visualization_fields(self):
        """Visualization-related fields should be settable."""
        identity = create_test_identity(
            self.user,
            visualization="Standing on a mountaintop",
            clothing="Flowing robes",
            mood="Triumphant",
            setting="Mountain peak at sunrise",
        )
        self.assertEqual(identity.visualization, "Standing on a mountaintop")
        self.assertEqual(identity.clothing, "Flowing robes")
        self.assertEqual(identity.mood, "Triumphant")
        self.assertEqual(identity.setting, "Mountain peak at sunrise")

    def test_state_transitions(self):
        """State should be updatable through the identity lifecycle."""
        identity = create_test_identity(self.user)
        lifecycle_states = [
            IdentityState.PROPOSED,
            IdentityState.ACCEPTED,
            IdentityState.REFINEMENT_COMPLETE,
            IdentityState.COMMITMENT_COMPLETE,
            IdentityState.I_AM_COMPLETE,
            IdentityState.VISUALIZATION_COMPLETE,
        ]
        for state in lifecycle_states:
            identity.state = state
            identity.save()
            identity.refresh_from_db()
            self.assertEqual(identity.state, state)

    def test_archived_state(self):
        """Identity should be archivable."""
        identity = create_test_identity(self.user)
        identity.state = IdentityState.ARCHIVED
        identity.save()
        identity.refresh_from_db()
        self.assertEqual(identity.state, IdentityState.ARCHIVED)

    def test_all_categories_valid(self):
        """Should accept all IdentityCategory values."""
        for category in IdentityCategory:
            identity = Identity.objects.create(
                user=self.user,
                name=f"Identity for {category.label}",
                category=category,
            )
            self.assertEqual(identity.category, category)

    def test_str_representation(self):
        """__str__ should include name, category display, and state display."""
        identity = create_test_identity(
            self.user,
            name="Creative Visionary",
            category=IdentityCategory.PASSIONS,
        )
        result = str(identity)
        self.assertIn("Creative Visionary", result)
        self.assertIn("Passions and Talents", result)
        self.assertIn("Proposed", result)

    def test_str_truncates_long_name(self):
        """__str__ should truncate names longer than 30 characters."""
        long_name = "A" * 50
        identity = create_test_identity(self.user, name=long_name)
        result = str(identity)
        self.assertIn("A" * 30, result)
        self.assertNotIn("A" * 50, result)

    def test_timestamps_set_on_creation(self):
        """created_at and updated_at should be set automatically."""
        identity = create_test_identity(self.user)
        self.assertIsNotNone(identity.created_at)
        self.assertIsNotNone(identity.updated_at)

    def test_cascade_deletes_with_user(self):
        """Identities should be deleted when user is deleted."""
        create_test_identity(self.user)
        create_test_identity(
            self.user, name="Second", category=IdentityCategory.HEALTH
        )
        self.assertEqual(Identity.objects.filter(user=self.user).count(), 2)

        self.user.delete()
        self.assertEqual(Identity.objects.count(), 0)

    def test_user_can_have_multiple_identities(self):
        """A user should be able to have multiple identities."""
        for i, category in enumerate(IdentityCategory):
            Identity.objects.create(
                user=self.user,
                name=f"Identity {i}",
                category=category,
            )
        self.assertEqual(
            Identity.objects.filter(user=self.user).count(),
            len(IdentityCategory),
        )

    def test_test_scenario_is_optional(self):
        """test_scenario FK should be nullable."""
        identity = create_test_identity(self.user)
        self.assertIsNone(identity.test_scenario)

    def test_inherits_image_mixin_fields(self):
        """Should have image and image_ppoi fields from ImageMixin."""
        identity = create_test_identity(self.user)
        self.assertTrue(hasattr(identity, "image"))
        self.assertTrue(hasattr(identity, "image_ppoi"))
