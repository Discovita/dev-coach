from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from apps.identities.models import Identity
from enums.action_type import ActionType
from enums.identity_state import IdentityState
from enums.coaching_phase import CoachingPhase
from services.action_handler.models import NestIdentityParams
from services.action_handler.utils import (
    set_current_identity_to_next_pending_commitment,
)
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def nest_identity(
    coach_state: CoachState, params: NestIdentityParams, coach_message: ChatMessage
):
    """
    Nest an identity under a parent identity.
    
    Step-by-step:
    1. Validates both identities exist and belong to the user
    2. Adds a note to the parent identity indicating the nested identity was nested under it
    3. Copies all notes from nested identity to parent identity with "[from {nested_name}]:" prefix
    4. Archives the nested identity
    5. Adds a note to the archived identity indicating it was nested under the parent
    6. No name changes are made to either identity
    """
    nested_identity_id = params.nested_identity_id
    parent_identity_id = params.parent_identity_id

    if nested_identity_id == parent_identity_id:
        raise ValueError("nest_identity requires two distinct identity IDs")

    # Fetch both identities
    identities = list(
        Identity.objects.filter(
            user=coach_state.user, id__in=[nested_identity_id, parent_identity_id]
        )
    )
    
    if len(identities) != 2:
        raise ValueError("nest_identity requires exactly two valid identities for the user")

    # Map identities
    identity_map = {str(i.id): i for i in identities}
    nested_identity = identity_map.get(nested_identity_id)
    parent_identity = identity_map.get(parent_identity_id)

    if nested_identity is None or parent_identity is None:
        raise ValueError("Could not resolve both identities for nesting")

    nested_identity_name = nested_identity.name or "Unnamed Identity"
    parent_identity_name = parent_identity.name or "Unnamed Identity"
    
    log.debug(
        f"Nesting identity '{nested_identity_name}' ({nested_identity_id}) under '{parent_identity_name}' ({parent_identity_id})"
    )

    # Copy all notes from nested identity to parent identity
    parent_notes = list(parent_identity.notes or [])
    nested_notes = list(nested_identity.notes or [])
    
    # Add a note indicating that we nested the nested identity under this parent
    parent_notes.append(f"Nested '{nested_identity_name}' identity under this identity.")
    
    # Append nested notes with prefix indicating they came from the nested identity
    prefixed_nested_notes = [f"[from {nested_identity_name}]: {note}" for note in nested_notes]
    parent_notes.extend(prefixed_nested_notes)
    
    parent_identity.notes = parent_notes
    parent_identity.save(update_fields=["notes", "updated_at"])

    # Archive the nested identity and add note about nesting
    archive_notes = list(nested_identity.notes or [])
    archive_notes.append(f"[Nested under {parent_identity_name}]: This identity was nested under '{parent_identity_name}'.")
    nested_identity.notes = archive_notes
    nested_identity.state = IdentityState.ARCHIVED
    nested_identity.save(update_fields=["state", "notes", "updated_at"])

    log.debug(f"Nested identity '{nested_identity_name}' under '{parent_identity_name}'")
    log.debug(f"Parent identity notes count: {len(parent_identity.notes)}")

    # Log the action
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.NEST_IDENTITY.value,
        parameters=params.model_dump(),
        result_summary=(
            f"Nested identity '{nested_identity_name}' under '{parent_identity_name}'. "
            f"Copied {len(nested_notes)} notes to parent identity."
        ),
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    # Set current_identity to the next pending identity based on current phase
    if coach_state.current_phase == CoachingPhase.IDENTITY_COMMITMENT.value:
        set_current_identity_to_next_pending_commitment(coach_state)

    return None

