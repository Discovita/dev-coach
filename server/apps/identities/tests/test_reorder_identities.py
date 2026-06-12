"""
Tests for identity ordering: the auto-append `order` on creation, the
`reorder_user_identities` function, and the POST /api/v1/identities/reorder/
endpoint.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.identities.functions.public import reorder_user_identities
from apps.identities.models import Identity
from apps.users.models import User
from enums.identity_category import IdentityCategory
from enums.identity_state import IdentityState


def _make_identity(user, name, category=IdentityCategory.PASSIONS):
    return Identity.objects.create(user=user, name=name, category=category)


class IdentityOrderOnCreateTests(TestCase):
    """The save() override should append new identities to the end."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="orderer@example.com", password="testpass123"
        )

    def test_new_identities_get_incrementing_order(self):
        first = _make_identity(self.user, "First")
        second = _make_identity(self.user, "Second")
        third = _make_identity(self.user, "Third")

        self.assertEqual(first.order, 0)
        self.assertEqual(second.order, 1)
        self.assertEqual(third.order, 2)

    def test_order_is_scoped_per_user(self):
        other = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )
        _make_identity(self.user, "Mine A")
        _make_identity(self.user, "Mine B")
        other_first = _make_identity(other, "Theirs A")

        # Other user's first identity starts at 0, independent of self.user.
        self.assertEqual(other_first.order, 0)

    def test_default_meta_ordering_is_creation_order(self):
        a = _make_identity(self.user, "A")
        b = _make_identity(self.user, "B")
        c = _make_identity(self.user, "C")

        ordered = list(Identity.objects.filter(user=self.user))
        self.assertEqual(ordered, [a, b, c])


class ReorderFunctionTests(TestCase):
    """Direct tests for the reorder_user_identities business function."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="fn@example.com", password="testpass123"
        )
        self.a = _make_identity(self.user, "A")
        self.b = _make_identity(self.user, "B")
        self.c = _make_identity(self.user, "C")

    def test_reorder_assigns_index_as_order(self):
        reorder_user_identities(self.user, [self.c.id, self.a.id, self.b.id])

        self.a.refresh_from_db()
        self.b.refresh_from_db()
        self.c.refresh_from_db()
        self.assertEqual(self.c.order, 0)
        self.assertEqual(self.a.order, 1)
        self.assertEqual(self.b.order, 2)

        ordered = list(Identity.objects.filter(user=self.user))
        self.assertEqual(ordered, [self.c, self.a, self.b])


class ReorderEndpointTests(APITestCase):
    """Tests for POST /api/v1/identities/reorder/."""

    URL = "/api/v1/identities/reorder"

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="api@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.a = _make_identity(self.user, "A")
        self.b = _make_identity(self.user, "B")
        self.c = _make_identity(self.user, "C")

    def test_reorder_updates_order_and_returns_new_order(self):
        response = self.client.post(
            self.URL,
            {"ordered_ids": [str(self.b.id), str(self.c.id), str(self.a.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = [item["name"] for item in response.data]
        self.assertEqual(returned_names, ["B", "C", "A"])

        # And the list endpoint reflects the same order.
        list_response = self.client.get("/api/v1/user/me/identities")
        list_names = [item["name"] for item in list_response.data]
        self.assertEqual(list_names, ["B", "C", "A"])

    def test_order_field_is_read_only_via_patch(self):
        # Attempting to set order directly should be ignored (read-only).
        self.client.patch(
            f"/api/v1/identities/{self.a.id}",
            {"order": 99},
            format="json",
        )
        self.a.refresh_from_db()
        self.assertEqual(self.a.order, 0)

    def test_reorder_rejects_identity_from_another_user(self):
        other = User.objects.create_user(
            email="intruder@example.com", password="testpass123"
        )
        other_identity = _make_identity(other, "Not Yours")

        response = self.client.post(
            self.URL,
            {"ordered_ids": [str(self.a.id), str(other_identity.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reorder_rejects_duplicate_ids(self):
        response = self.client.post(
            self.URL,
            {"ordered_ids": [str(self.a.id), str(self.a.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reorder_rejects_empty_list(self):
        response = self.client.post(
            self.URL, {"ordered_ids": []}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reorder_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.URL,
            {"ordered_ids": [str(self.a.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminReorderEndpointTests(APITestCase):
    """Tests for POST /api/v1/admin/identities/reorder (admin impersonation)."""

    URL = "/api/v1/admin/identities/reorder"

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@example.com", password="testpass123", is_staff=True
        )
        self.target = User.objects.create_user(
            email="target@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.admin)
        self.a = _make_identity(self.target, "A")
        self.b = _make_identity(self.target, "B")
        self.c = _make_identity(self.target, "C")

    def test_admin_reorders_target_users_identities(self):
        response = self.client.post(
            self.URL,
            {
                "user_id": str(self.target.id),
                "ordered_ids": [str(self.c.id), str(self.a.id), str(self.b.id)],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["name"] for item in response.data], ["C", "A", "B"])

        self.a.refresh_from_db()
        self.b.refresh_from_db()
        self.c.refresh_from_db()
        self.assertEqual((self.c.order, self.a.order, self.b.order), (0, 1, 2))

    def test_missing_user_id_is_rejected(self):
        response = self.client.post(
            self.URL,
            {"ordered_ids": [str(self.a.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejects_identity_not_owned_by_target_user(self):
        other = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )
        other_identity = _make_identity(other, "Not Theirs")
        response = self.client.post(
            self.URL,
            {
                "user_id": str(self.target.id),
                "ordered_ids": [str(self.a.id), str(other_identity.id)],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_admin_is_forbidden(self):
        self.client.force_authenticate(user=self.target)
        response = self.client.post(
            self.URL,
            {"user_id": str(self.target.id), "ordered_ids": [str(self.a.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
