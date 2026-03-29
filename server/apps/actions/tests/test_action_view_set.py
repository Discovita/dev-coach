"""
HTTP tests for ActionViewSet-backed routes.
"""

import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.users.models import User
from enums.action_type import ActionType
from enums.message_role import MessageRole


class ActionViewSetTests(APITestCase):
    """Covers authentication, scoping, and custom list actions."""

    def setUp(self):
        self.user_a = User.objects.create_user(
            email="a@example.com", password="pass12345"
        )
        self.user_b = User.objects.create_user(
            email="b@example.com", password="pass12345"
        )
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="pass12345",
            is_staff=True,
        )
        self.msg_a = ChatMessage.objects.create(
            user=self.user_a,
            content="Coach reply",
            role=MessageRole.COACH,
        )
        self.msg_b = ChatMessage.objects.create(
            user=self.user_b,
            content="Other coach",
            role=MessageRole.COACH,
        )
        self.action_a = Action.objects.create(
            user=self.user_a,
            action_type=ActionType.CREATE_IDENTITY,
            parameters={"k": "v"},
            coach_message=self.msg_a,
        )
        self.action_b = Action.objects.create(
            user=self.user_b,
            action_type=ActionType.UPDATE_IDENTITY,
            parameters={},
            coach_message=self.msg_b,
        )
        self.list_url = "/api/v1/actions"
        self.for_user_url = "/api/v1/actions/for-user"
        self.by_msg_url = "/api/v1/actions/by-coach-message"

    def test_list_requires_authentication(self):
        """Anonymous requests receive 401."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_scoped_to_owner(self):
        """Regular users only see their own actions."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row["id"] for row in response.data}
        self.assertEqual(ids, {str(self.action_a.id)})

    def test_staff_list_sees_all(self):
        """Staff queryset includes every action."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row["id"] for row in response.data}
        self.assertEqual(ids, {str(self.action_a.id), str(self.action_b.id)})

    def test_retrieve_forbidden_for_other_users_action(self):
        """Non-staff cannot load another user's action by primary key."""
        self.client.force_authenticate(user=self.user_a)
        url = f"{self.list_url}/{self.action_b.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_for_user_requires_privilege(self):
        """Non-staff cannot call for-user."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.for_user_url, {"user_id": str(self.user_b.id)})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_for_user_staff_returns_target_actions(self):
        """Staff can pass user_id to read another user's actions."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(self.for_user_url, {"user_id": str(self.user_b.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row["id"] for row in response.data}
        self.assertEqual(ids, {str(self.action_b.id)})

    def test_for_user_unknown_user_404(self):
        """Missing user returns 404."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(
            self.for_user_url,
            {"user_id": str(uuid.uuid4())},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_by_coach_message_scoped(self):
        """Users may only query messages that belong to them."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.by_msg_url, {"message_id": str(self.msg_b.id)})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_by_coach_message_returns_actions(self):
        """Owner receives ordered actions for that coach message."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.by_msg_url, {"message_id": str(self.msg_a.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.action_a.id))
