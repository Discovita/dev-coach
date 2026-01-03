"""
Tests for get_user_identities function.
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.users.models import User
from apps.users.functions import get_user_identities
from apps.identities.models import Identity
from enums.identity_state import IdentityState
from enums.identity_category import IdentityCategory


class GetUserIdentitiesFunctionTests(TestCase):
    """Test the get_user_identities function directly."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        
        # Create accepted identity
        self.active_identity = Identity.objects.create(
            user=self.user,
            name="The Explorer",
            state=IdentityState.ACCEPTED,
            category=IdentityCategory.PASSIONS,
        )
        
        # Create proposed identity
        self.proposed_identity = Identity.objects.create(
            user=self.user,
            name="The Creator",
            state=IdentityState.PROPOSED,
            category=IdentityCategory.MONEY_MAKER,
        )
        
        # Create archived identity
        self.archived_identity = Identity.objects.create(
            user=self.user,
            name="The Old One",
            state=IdentityState.ARCHIVED,
            category=IdentityCategory.FAMILY,
        )

    def test_default_excludes_archived(self):
        """Test that archived identities are excluded by default."""
        identities = get_user_identities(self.user)
        
        self.assertEqual(identities.count(), 2)
        self.assertIn(self.active_identity, identities)
        self.assertIn(self.proposed_identity, identities)
        self.assertNotIn(self.archived_identity, identities)

    def test_include_archived_returns_all(self):
        """Test that include_archived=True returns all identities."""
        identities = get_user_identities(self.user, include_archived=True)
        
        self.assertEqual(identities.count(), 3)
        self.assertIn(self.active_identity, identities)
        self.assertIn(self.proposed_identity, identities)
        self.assertIn(self.archived_identity, identities)

    def test_archived_only_returns_only_archived(self):
        """Test that archived_only=True returns only archived identities."""
        identities = get_user_identities(self.user, archived_only=True)
        
        self.assertEqual(identities.count(), 1)
        self.assertIn(self.archived_identity, identities)
        self.assertNotIn(self.active_identity, identities)
        self.assertNotIn(self.proposed_identity, identities)

    def test_user_with_no_identities(self):
        """Test behavior with user who has no identities."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        
        identities = get_user_identities(other_user)
        
        self.assertEqual(identities.count(), 0)

    def test_does_not_return_other_users_identities(self):
        """Test that function only returns identities for the specified user."""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        Identity.objects.create(
            user=other_user,
            name="Other User Identity",
            state=IdentityState.ACCEPTED,
            category=IdentityCategory.PASSIONS,
        )
        
        identities = get_user_identities(self.user, include_archived=True)
        
        self.assertEqual(identities.count(), 3)  # Only self.user's identities


class GetUserIdentitiesAPITests(APITestCase):
    """Test the identities API endpoint."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        
        # Create identities
        self.active_identity = Identity.objects.create(
            user=self.user,
            name="The Explorer",
            state=IdentityState.ACCEPTED,
            category=IdentityCategory.PASSIONS,
        )
        self.archived_identity = Identity.objects.create(
            user=self.user,
            name="The Old One",
            state=IdentityState.ARCHIVED,
            category=IdentityCategory.FAMILY,
        )

    def test_api_default_excludes_archived(self):
        """Test API endpoint excludes archived by default."""
        response = self.client.get("/api/v1/user/me/identities")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "The Explorer")

    def test_api_include_archived(self):
        """Test API endpoint with include_archived=true."""
        response = self.client.get("/api/v1/user/me/identities?include_archived=true")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_api_archived_only(self):
        """Test API endpoint with archived_only=true."""
        response = self.client.get("/api/v1/user/me/identities?archived_only=true")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "The Old One")

    def test_api_requires_authentication(self):
        """Test that endpoint requires authentication."""
        self.client.force_authenticate(user=None)
        
        response = self.client.get("/api/v1/user/me/identities")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

