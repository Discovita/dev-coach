"""
Instantiate a test scenario by creating all DB objects from its template.

See: apps/test_scenario/functions/__init__.py
"""

import hashlib
import uuid

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from apps.test_scenario.utils.copy_image_from_url import copy_image_from_url
from apps.user_notes.models import UserNote
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__)


def instantiate_test_scenario(
    scenario,
    *,
    create_user: bool = True,
    create_chat_messages: bool = False,
    create_identities: bool = False,
    create_coach_state: bool = False,
    create_user_notes: bool = False,
    create_actions: bool = False,
) -> dict:
    """
    Create all DB objects described by *scenario.template*.

    Deletes any existing objects for this scenario before re-creating them,
    so calling this function is idempotent.

    Returns:
        A dict with keys ``user``, ``coach_state``, and ``email``.
    """
    template = scenario.template
    created_user = None
    created_coach_state = None
    unique_email = None

    if create_user:
        created_user, unique_email = _create_user(scenario, template)

    created_identities = {}
    if create_identities and template.get("identities"):
        created_identities = _create_identities(scenario, template, created_user)

    if create_coach_state and template.get("coach_state") and created_user:
        created_coach_state = _create_coach_state(
            scenario, template, created_user, created_identities
        )

    original_to_new_msg = {}
    if create_chat_messages and template.get("chat_messages") and created_user:
        original_to_new_msg = _create_chat_messages(scenario, template, created_user)

    if create_user_notes and template.get("user_notes") and created_user:
        _create_user_notes(scenario, template, created_user)

    if create_actions and template.get("actions") and created_user:
        _create_actions(scenario, template, created_user, original_to_new_msg)

    return {
        "user": created_user,
        "coach_state": created_coach_state,
        "email": unique_email,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _create_user(scenario, template: dict):
    """Delete any existing scenario user, then create a fresh one."""
    User.objects.filter(test_scenario=scenario).delete()
    user_data = dict(template.get("user") or {})
    password = "Coach123!"

    base_email = user_data.get("email")
    if not base_email or User.objects.filter(email=base_email).exists():
        hash_input = f"{scenario.id}-{uuid.uuid4()}"
        unique_email = f"test_user_{hashlib.sha256(hash_input.encode()).hexdigest()[:8]}@testscenario.com"
    else:
        unique_email = base_email

    user_data["email"] = unique_email

    # Strip fields that shouldn't reach the User constructor
    for key in (
        "password",
        "id",
        "user_id",
        "created_at",
        "updated_at",
        "last_login",
        "date_joined",
    ):
        user_data.pop(key, None)

    try:
        user = User(**user_data, test_scenario=scenario)
        user.set_password(password)
        user.save()
        return user, unique_email
    except Exception as e:
        raise ValueError(f"Failed to create user: {e}") from e


def _create_identities(scenario, template: dict, user) -> dict:
    """Create Identity objects, returning a name → Identity mapping."""
    if not user or not user.id:
        raise ValueError(
            "Cannot create identities: user creation failed or was skipped"
        )

    Identity.objects.filter(user=user, test_scenario=scenario).delete()
    created: dict[str, Identity] = {}

    for identity_data in template["identities"]:
        identity = Identity(
            user=user,
            test_scenario=scenario,
            name=identity_data.get("name"),
            category=identity_data.get("category"),
            state=identity_data.get("state"),
            i_am_statement=identity_data.get("i_am_statement", ""),
            visualization=identity_data.get("visualization", ""),
            notes=identity_data.get("notes", []),
        )

        image_url = identity_data.get("image")
        if image_url:
            copied_key = copy_image_from_url(image_url)
            if copied_key:
                image_path = (
                    copied_key[6:] if copied_key.startswith("media/") else copied_key
                )
                identity.image.name = image_path

        identity.save()
        created[identity.name] = identity

    return created


def _create_coach_state(scenario, template, user, created_identities):
    """Update the auto-created CoachState with template data."""
    coach_state_data = template["coach_state"].copy()
    allowed_fields = {f.name for f in CoachState._meta.get_fields()}

    current_identity_name = coach_state_data.pop("current_identity", None)
    coach_state_data.pop("proposed_identity", None)
    coach_state_data["test_scenario"] = scenario

    coach_state = CoachState.objects.get(user=user)
    for key, value in coach_state_data.items():
        if key in allowed_fields:
            setattr(coach_state, key, value)

    if current_identity_name:
        if current_identity_name in created_identities:
            coach_state.current_identity = created_identities[current_identity_name]
        else:
            try:
                coach_state.current_identity = Identity.objects.get(
                    user=user, test_scenario=scenario, name=current_identity_name
                )
            except Identity.DoesNotExist:
                log.warning(
                    f"Current identity '{current_identity_name}' not found for user {user.id}"
                )

    coach_state.save()
    return coach_state


def _create_chat_messages(scenario, template, user) -> dict:
    """Create ChatMessage objects, returning a message-key → ChatMessage mapping."""
    ChatMessage.objects.filter(user=user, test_scenario=scenario).delete()
    mapping: dict[str, ChatMessage] = {}

    for msg_data in template["chat_messages"]:
        msg = ChatMessage.objects.create(
            user=user,
            test_scenario=scenario,
            role=msg_data.get("role"),
            content=msg_data.get("content"),
            timestamp=msg_data.get("timestamp") or None,
            component_config=msg_data.get("component_config"),
        )
        key = f"{msg_data.get('role')}|{msg_data.get('content')}|{msg_data.get('timestamp', '')}"
        mapping[key] = msg

    return mapping


def _create_user_notes(scenario, template, user) -> None:
    """Create UserNote objects from the template."""
    UserNote.objects.filter(user=user, test_scenario=scenario).delete()
    for note_data in template["user_notes"]:
        UserNote.objects.create(
            user=user,
            test_scenario=scenario,
            note=note_data.get("note"),
            source_message=None,
            created_at=note_data.get("created_at") or None,
        )


def _create_actions(scenario, template, user, original_to_new_msg) -> None:
    """Create Action objects, linking to chat messages where possible."""
    Action.objects.filter(user=user, test_scenario=scenario).delete()

    for action_data in template["actions"]:
        coach_message = _resolve_coach_message(
            action_data, template, user, scenario, original_to_new_msg
        )
        Action(
            user=user,
            test_scenario=scenario,
            action_type=action_data.get("action_type"),
            parameters=action_data.get("parameters", {}),
            result_summary=action_data.get("result_summary", ""),
            timestamp=action_data.get("timestamp") or None,
            coach_message=coach_message,
        ).save()


def _resolve_coach_message(action_data, template, user, scenario, original_to_new_msg):
    """
    Find the ChatMessage to link an Action to.

    Tries ID-based mapping first, then content matching, then falls
    back to the most recent coach message.
    """

    def fallback():
        return (
            ChatMessage.objects.filter(user=user, test_scenario=scenario, role="coach")
            .order_by("-timestamp")
            .first()
        )

    # ID-based mapping (preferred)
    if action_data.get("original_coach_message_id") and template.get(
        "original_message_mapping"
    ):
        original_msg_data = template["original_message_mapping"].get(
            action_data["original_coach_message_id"]
        )
        if original_msg_data:
            key = f"{original_msg_data.get('role')}|{original_msg_data.get('content')}|{original_msg_data.get('timestamp', '')}"
            msg = original_to_new_msg.get(key)
            if msg:
                return msg
        return fallback()

    # Content-based matching (deprecated)
    if action_data.get("coach_message_content"):
        qs = ChatMessage.objects.filter(
            user=user,
            test_scenario=scenario,
            role="coach",
            content=action_data["coach_message_content"],
        ).order_by("-timestamp")
        if qs.exists():
            return qs.first()
        return fallback()

    return fallback()
