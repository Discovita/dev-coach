"""
Capture ("freeze") a live user session as a new test scenario.

See: apps/test_scenario/functions/__init__.py
"""

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from apps.test_scenario.functions.instantiate_test_scenario import (
    instantiate_test_scenario,
)
from apps.test_scenario.models import TestScenario
from apps.test_scenario.utils.duplicate_s3_image import duplicate_s3_image
from apps.test_scenario.utils.validate_scenario_template import (
    validate_scenario_template,
)
from apps.user_notes.models import UserNote
from services.logger import configure_logging

User = get_user_model()
log = configure_logging(__name__)


class FreezeSessionError(Exception):
    """Raised when freezing a session fails for a domain-level reason."""

    def __init__(self, detail: str, *, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


def freeze_user_session(
    *,
    user_id: str,
    name: str,
    description: str = "",
    first_name: str = "",
    last_name: str = "",
    created_by=None,
) -> TestScenario:
    """
    Capture the current state of a user session as a new TestScenario.

    Steps:
        1. Validate inputs (user exists, name is unique).
        2. Gather all user state (CoachState, Identities, ChatMessages, etc.).
        3. Build & validate a scenario template dict.
        4. Create the TestScenario and instantiate it.

    Args:
        user_id: PK of the user whose session to freeze.
        name: Unique name for the new scenario.
        description: Optional description.
        first_name: Override for the template user's first name.
        last_name: Override for the template user's last name.
        created_by: The admin user who is freezing the session.

    Returns:
        The newly created ``TestScenario`` instance.

    Raises:
        FreezeSessionError: On validation failures (missing user, duplicate
            name, template validation errors).
    """
    # --- Validate inputs ---
    if not user_id or not name:
        raise FreezeSessionError("user_id and name are required.")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise FreezeSessionError("User not found.", status_code=404)

    if TestScenario.objects.filter(name=name).exists():
        raise FreezeSessionError("A scenario with this name already exists.")

    # --- Build template ---
    template = _build_template(
        user,
        first_name=first_name,
        last_name=last_name,
    )

    # --- Validate template ---
    errors = validate_scenario_template(template)
    if errors:
        raise FreezeSessionError(f"Template validation failed: {errors}")

    # --- Persist ---
    scenario = TestScenario.objects.create(
        name=name,
        description=description,
        template=template,
        created_by=created_by,
    )
    instantiate_test_scenario(
        scenario,
        create_user=True,
        create_coach_state=True,
        create_identities=True,
        create_chat_messages=True,
        create_user_notes=True,
        create_actions=True,
    )
    return scenario


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _build_template(user, *, first_name: str, last_name: str) -> dict:
    """Assemble the full template dict from the user's current DB state."""
    template: dict = {"user": _gather_user_section(user, first_name, last_name)}

    coach_state_section = _gather_coach_state(user)
    if coach_state_section:
        template["coach_state"] = coach_state_section

    identities_section = _gather_identities(user)
    if identities_section:
        template["identities"] = identities_section

    messages_section, original_mapping = _gather_chat_messages(user)
    if messages_section:
        template["chat_messages"] = messages_section
    if original_mapping:
        template["original_message_mapping"] = original_mapping

    notes_section = _gather_user_notes(user)
    if notes_section:
        template["user_notes"] = notes_section

    actions_section = _gather_actions(user)
    if actions_section:
        template["actions"] = actions_section

    return template


def _gather_user_section(user, first_name: str, last_name: str) -> dict:
    return {
        "email": user.email,
        "first_name": first_name.strip() or user.first_name or "Test",
        "last_name": last_name.strip() or user.last_name or "User",
    }


def _gather_coach_state(user) -> dict | None:
    try:
        cs = CoachState.objects.get(user=user)
    except CoachState.DoesNotExist:
        return None

    section: dict = {
        "current_phase": cs.current_phase,
        "identity_focus": cs.identity_focus,
        "who_you_are": cs.who_you_are,
        "who_you_want_to_be": cs.who_you_want_to_be,
    }
    if getattr(cs, "skipped_identity_categories", None):
        section["skipped_identity_categories"] = cs.skipped_identity_categories
    if getattr(cs, "current_identity", None):
        section["current_identity"] = str(cs.current_identity.id)
    if getattr(cs, "proposed_identity", None):
        section["proposed_identity"] = str(cs.proposed_identity.id)
    if getattr(cs, "asked_questions", None):
        section["asked_questions"] = cs.asked_questions
    if getattr(cs, "metadata", None):
        section["metadata"] = cs.metadata
    return section


def _gather_identities(user) -> list[dict]:
    section: list[dict] = []
    for identity in Identity.objects.filter(user=user):
        entry: dict = {"name": identity.name, "category": identity.category}
        if identity.state:
            entry["state"] = identity.state
        if identity.i_am_statement:
            entry["i_am_statement"] = identity.i_am_statement
        if identity.visualization:
            entry["visualization"] = identity.visualization
        if identity.notes:
            entry["notes"] = identity.notes
        if identity.image:
            dup_key = duplicate_s3_image(identity.image)
            if dup_key:
                entry["image"] = default_storage.url(dup_key)
        section.append(entry)
    return section


def _gather_chat_messages(user) -> tuple[list[dict], dict]:
    section: list[dict] = []
    mapping: dict = {}
    for msg in ChatMessage.objects.filter(user=user).order_by("timestamp"):
        entry: dict = {"role": msg.role, "content": msg.content}
        if msg.timestamp:
            entry["timestamp"] = msg.timestamp.isoformat()
        if msg.component_config:
            entry["component_config"] = msg.component_config
        section.append(entry)
        mapping[str(msg.id)] = {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
            "component_config": msg.component_config,
        }
    return section, mapping


def _gather_user_notes(user) -> list[dict]:
    section: list[dict] = []
    for note in UserNote.objects.filter(user=user):
        entry: dict = {"note": note.note}
        if note.source_message:
            entry["source_message"] = str(note.source_message.id)
        if note.created_at:
            entry["created_at"] = note.created_at.isoformat()
        section.append(entry)
    return section


def _gather_actions(user) -> list[dict]:
    section: list[dict] = []
    for action in Action.objects.filter(user=user).order_by("timestamp"):
        entry: dict = {
            "action_type": action.action_type,
            "parameters": action.parameters,
        }
        if action.result_summary:
            entry["result_summary"] = action.result_summary
        if action.timestamp:
            entry["timestamp"] = action.timestamp.isoformat()
        if action.coach_message:
            entry["original_coach_message_id"] = str(action.coach_message.id)
        section.append(entry)
    return section
