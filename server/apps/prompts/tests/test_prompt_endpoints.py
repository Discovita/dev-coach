"""
Endpoint tests for the PromptViewSet.

Covers CRUD operations, soft_delete, latest, and permission enforcement.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.prompts.models import Prompt
from apps.users.models import User
from enums.coaching_phase import CoachingPhase
from enums.prompt_type import PromptType


class PromptPermissionTests(APITestCase):
    """Verify that non-admin users are rejected from all endpoints."""

    def setUp(self):
        self.regular_user = User.objects.create_user(
            email="regular@example.com", password="TestPass1!"
        )
        self.prompt = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            body="Test body",
        )

    def test_unauthenticated_user_rejected(self):
        """Unauthenticated requests are rejected."""
        response = self.client.get("/api/v1/prompts")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_non_admin_user_rejected(self):
        """Authenticated non-admin users are rejected."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/v1/prompts")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_rejected_on_create(self):
        """Non-admin cannot create prompts."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            "/api/v1/prompts",
            {"body": "New prompt", "coaching_phase": CoachingPhase.INTRODUCTION},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_rejected_on_delete(self):
        """Non-admin cannot delete prompts."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(f"/api/v1/prompts/{self.prompt.id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PromptListTests(APITestCase):
    """Tests for GET /api/v1/prompts (list endpoint)."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="TestPass1!", is_staff=True
        )
        self.client.force_authenticate(user=self.admin)

        self.active_prompt = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            body="Active prompt",
            is_active=True,
        )
        self.inactive_prompt = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=2,
            body="Inactive prompt",
            is_active=False,
        )

    def test_list_returns_only_active_prompts(self):
        """GET /prompts only returns is_active=True prompts."""
        response = self.client.get("/api/v1/prompts")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data]
        self.assertIn(str(self.active_prompt.id), ids)
        self.assertNotIn(str(self.inactive_prompt.id), ids)

    def test_list_returns_expected_fields(self):
        """Each item in list response contains all serializer fields."""
        response = self.client.get("/api/v1/prompts")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data[0]
        expected_fields = {
            "id",
            "coaching_phase",
            "version",
            "name",
            "description",
            "body",
            "required_context_keys",
            "allowed_actions",
            "prompt_type",
            "is_active",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(item.keys()), expected_fields)


class PromptRetrieveTests(APITestCase):
    """Tests for GET /api/v1/prompts/{id} (retrieve endpoint)."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="TestPass1!", is_staff=True
        )
        self.client.force_authenticate(user=self.admin)

        self.prompt = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            body="Retrieve me",
        )

    def test_retrieve_by_id(self):
        """Fetching a prompt by ID returns its full data."""
        response = self.client.get(f"/api/v1/prompts/{self.prompt.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["body"], "Retrieve me")

    def test_retrieve_inactive_prompt(self):
        """Inactive prompts can still be retrieved directly by ID."""
        self.prompt.is_active = False
        self.prompt.save()

        response = self.client.get(f"/api/v1/prompts/{self.prompt.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_nonexistent_returns_404(self):
        """Fetching a non-existent ID returns 404."""
        response = self.client.get(
            "/api/v1/prompts/00000000-0000-0000-0000-000000000000"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PromptCreateTests(APITestCase):
    """Tests for POST /api/v1/prompts (create endpoint)."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="TestPass1!", is_staff=True
        )
        self.client.force_authenticate(user=self.admin)

    def test_create_prompt(self):
        """Creating a prompt returns 201 with auto-assigned version=1."""
        response = self.client.post(
            "/api/v1/prompts",
            {
                "body": "New prompt body",
                "coaching_phase": CoachingPhase.INTRODUCTION,
                "prompt_type": PromptType.COACH,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["version"], 1)
        self.assertEqual(response.data["body"], "New prompt body")
        self.assertTrue(Prompt.objects.filter(id=response.data["id"]).exists())

    def test_create_auto_increments_version(self):
        """Second prompt for same scope gets version=2."""
        Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            body="v1",
        )

        response = self.client.post(
            "/api/v1/prompts",
            {
                "body": "v2 body",
                "coaching_phase": CoachingPhase.INTRODUCTION,
                "prompt_type": PromptType.COACH,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["version"], 2)

    def test_create_ignores_client_version(self):
        """Client-supplied version is overridden by auto-assignment."""
        response = self.client.post(
            "/api/v1/prompts",
            {
                "body": "Should be v1",
                "coaching_phase": CoachingPhase.INTRODUCTION,
                "prompt_type": PromptType.COACH,
                "version": 999,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["version"], 1)

    def test_create_without_coaching_phase(self):
        """Prompts like sentinel can be created without coaching_phase."""
        response = self.client.post(
            "/api/v1/prompts",
            {
                "body": "Sentinel body",
                "prompt_type": PromptType.SENTINEL,
                "coaching_phase": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["coaching_phase"])

    def test_create_without_body_returns_400(self):
        """Missing body field should return 400."""
        response = self.client.post(
            "/api/v1/prompts",
            {"coaching_phase": CoachingPhase.INTRODUCTION},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PromptUpdateTests(APITestCase):
    """Tests for PUT and PATCH /api/v1/prompts/{id}."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="TestPass1!", is_staff=True
        )
        self.client.force_authenticate(user=self.admin)

        self.prompt = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            body="Original body",
            name="Original name",
        )

    def test_full_update(self):
        """PUT replaces the prompt's writable fields."""
        response = self.client.put(
            f"/api/v1/prompts/{self.prompt.id}",
            {
                "body": "Updated body",
                "coaching_phase": CoachingPhase.INTRODUCTION,
                "prompt_type": PromptType.COACH,
                "name": "Updated name",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["body"], "Updated body")
        self.assertEqual(response.data["name"], "Updated name")

    def test_partial_update(self):
        """PATCH updates only the supplied fields."""
        response = self.client.patch(
            f"/api/v1/prompts/{self.prompt.id}",
            {"name": "Patched name"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Patched name")
        self.assertEqual(response.data["body"], "Original body")


class PromptDestroyTests(APITestCase):
    """Tests for DELETE /api/v1/prompts/{id}."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="TestPass1!", is_staff=True
        )
        self.client.force_authenticate(user=self.admin)

        self.prompt = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            body="Delete me",
        )

    def test_hard_delete(self):
        """DELETE removes the prompt from the database."""
        response = self.client.delete(f"/api/v1/prompts/{self.prompt.id}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Prompt.objects.filter(id=self.prompt.id).exists())

    def test_delete_nonexistent_returns_404(self):
        """DELETE on non-existent ID returns 404."""
        response = self.client.delete(
            "/api/v1/prompts/00000000-0000-0000-0000-000000000000"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PromptSoftDeleteTests(APITestCase):
    """Tests for POST /api/v1/prompts/{id}/soft_delete."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="TestPass1!", is_staff=True
        )
        self.client.force_authenticate(user=self.admin)

        self.prompt = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            body="Soft delete me",
            is_active=True,
        )

    def test_soft_delete_sets_inactive(self):
        """POST soft_delete sets is_active=False and returns the prompt."""
        response = self.client.post(f"/api/v1/prompts/{self.prompt.id}/soft_delete")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_active"])

        self.prompt.refresh_from_db()
        self.assertFalse(self.prompt.is_active)

    def test_soft_delete_nonexistent_returns_404(self):
        """Soft-deleting a non-existent prompt returns 404."""
        response = self.client.post(
            "/api/v1/prompts/00000000-0000-0000-0000-000000000000/soft_delete"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PromptLatestTests(APITestCase):
    """Tests for GET /api/v1/prompts/latest?coaching_phase=..."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", password="TestPass1!", is_staff=True
        )
        self.client.force_authenticate(user=self.admin)

        self.v1 = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=1,
            body="Intro v1",
            is_active=True,
        )
        self.v2 = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=2,
            body="Intro v2",
            is_active=True,
        )
        self.v3_inactive = Prompt.objects.create(
            coaching_phase=CoachingPhase.INTRODUCTION,
            prompt_type=PromptType.COACH,
            version=3,
            body="Intro v3 (inactive)",
            is_active=False,
        )

    def test_returns_latest_active_prompt(self):
        """Returns the highest-version active prompt for the given phase."""
        response = self.client.get(
            "/api/v1/prompts/latest",
            {"coaching_phase": CoachingPhase.INTRODUCTION},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["version"], 2)
        self.assertEqual(response.data["body"], "Intro v2")

    def test_missing_coaching_phase_returns_400(self):
        """Omitting coaching_phase returns 400."""
        response = self.client.get("/api/v1/prompts/latest")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_coaching_phase_returns_400(self):
        """An unrecognized coaching_phase returns 400."""
        response = self.client.get(
            "/api/v1/prompts/latest",
            {"coaching_phase": "not_a_real_phase"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_active_prompt_returns_404(self):
        """Returns 404 when no active prompts exist for the given phase."""
        response = self.client.get(
            "/api/v1/prompts/latest",
            {"coaching_phase": CoachingPhase.GET_TO_KNOW_YOU},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
