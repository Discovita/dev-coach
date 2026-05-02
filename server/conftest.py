"""
Shared pytest fixtures for the Discovita dev-coach backend test suite.

Provides reusable factory functions and pytest fixtures for creating common
test objects (User, CoachState, Prompt, ChatMessage, Identity, Action).
These fixtures reduce boilerplate across test files.

Also usable as plain helper functions from Django TestCase.setUp() via:
    from conftest import create_test_user, create_test_prompt, ...
"""

import pytest

from apps.users.models import User
from apps.prompts.models import Prompt
from apps.chat_messages.models import ChatMessage
from apps.identities.models import Identity
from enums.coaching_phase import CoachingPhase
from enums.identity_category import IdentityCategory
from enums.identity_state import IdentityState
from enums.message_role import MessageRole
from enums.prompt_type import PromptType
from enums.action_type import ActionType


def create_test_user(email="test@example.com", password="testpass123", **kwargs):
    """Create a test user. CoachState is auto-created by signal."""
    return User.objects.create_user(email=email, password=password, **kwargs)


def create_test_prompt(
    coaching_phase=CoachingPhase.INTRODUCTION,
    version=1,
    body="Test prompt body with {placeholder}",
    prompt_type=PromptType.COACH,
    is_active=True,
    allowed_actions=None,
    required_context_keys=None,
    **kwargs,
):
    """Create a test Prompt instance."""
    return Prompt.objects.create(
        coaching_phase=coaching_phase,
        version=version,
        name=kwargs.pop("name", f"Test Prompt v{version}"),
        body=body,
        prompt_type=prompt_type,
        is_active=is_active,
        allowed_actions=allowed_actions or [],
        required_context_keys=required_context_keys or [],
        **kwargs,
    )


def create_test_chat_message(user, role=MessageRole.USER, content="Hello", **kwargs):
    """Create a test ChatMessage instance."""
    return ChatMessage.objects.create(
        user=user,
        role=role,
        content=content,
        **kwargs,
    )


def create_test_identity(
    user,
    name="Test Identity",
    category=IdentityCategory.PASSIONS,
    state=IdentityState.PROPOSED,
    **kwargs,
):
    """Create a test Identity instance."""
    return Identity.objects.create(
        user=user,
        name=name,
        category=category,
        state=state,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Pytest fixtures (for tests run via pytest)
# ---------------------------------------------------------------------------


@pytest.fixture
def test_user(db):
    """Provide a test user with auto-created CoachState."""
    return create_test_user()


@pytest.fixture
def test_prompt(db):
    """Provide a basic active coach prompt."""
    return create_test_prompt()


@pytest.fixture
def coach_message(db, test_user):
    """Provide a coach ChatMessage."""
    return create_test_chat_message(
        test_user, role=MessageRole.COACH, content="Welcome!"
    )


@pytest.fixture
def user_message(db, test_user):
    """Provide a user ChatMessage."""
    return create_test_chat_message(
        test_user, role=MessageRole.USER, content="Hi there"
    )


@pytest.fixture
def test_identity(db, test_user):
    """Provide a test Identity."""
    return create_test_identity(test_user)
