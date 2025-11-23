from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from apps.identities.models import Identity
from enums.action_type import ActionType
from enums.identity_category import IdentityCategory
from enums.identity_state import IdentityState
from services.action_handler.models.params import (
    CombineIdentitiesParams,
)
from services.logger import configure_logging
log = configure_logging(__name__, log_level="DEBUG")


def combine_identities(
    coach_state: CoachState, params: CombineIdentitiesParams, coach_message: ChatMessage
):
    """
    Combines two identities into one by merging their names and notes.
    The identity that gets archived (based on category rules) is marked as archived
    instead of being deleted, preserving it in the database for historical reference.
    """

    identity_id_a = params.identity_id_a
    identity_id_b = params.identity_id_b

    if identity_id_a == identity_id_b:
        raise ValueError("combine_identities requires two distinct identity IDs")

    identities = list(
        Identity.objects.filter(
            user=coach_state.user, id__in=[identity_id_a, identity_id_b]
        )
    )
    if len(identities) != 2:
        raise ValueError("combine_identities requires exactly two valid identities for the user")

    # Map them back to A and B for deterministic rule application
    identity_map = {str(i.id): i for i in identities}
    identity_a = identity_map.get(identity_id_a)
    identity_b = identity_map.get(identity_id_b)

    if identity_a is None or identity_b is None:
        raise ValueError("Could not resolve both identities for merging")

    category_a = identity_a.category
    category_b = identity_b.category
    log.debug(
        f"Preparing to combine identities {identity_id_a} ({category_a}) and {identity_id_b} ({category_b})"
    )

    # Determine which identity to archive vs keep per rules
    passions_value = IdentityCategory.PASSIONS.value
    if (category_a == passions_value) ^ (category_b == passions_value):
        # Exactly one is Passions and Talents → archive that one, edit the other
        if category_a == passions_value:
            archive_identity = identity_a
            save_identity = identity_b
        else:
            archive_identity = identity_b
            save_identity = identity_a
    else:
        # Neither or both are Passions and Talents → edit A, archive B
        save_identity = identity_a
        archive_identity = identity_b

    # Build resulting name "A/B" using original names, handle None
    name_a = identity_a.name or ""
    name_b = identity_b.name or ""
    combined_name = f"{name_a}/{name_b}" if name_a or name_b else ""

    # Merge notes: prepend source marker and append to save_identity notes
    save_notes = list(save_identity.notes or [])
    source_name = archive_identity.name or "Unnamed Identity"
    merged_notes = [f"[Merged from {source_name}]: {note}" for note in (archive_identity.notes or [])]
    save_identity.notes = save_notes + merged_notes

    # Apply name change and save
    save_identity.name = combined_name
    save_identity.save(update_fields=["name", "notes", "updated_at"])

    # Archive the other identity instead of deleting it
    archived_identity_id = str(archive_identity.id)
    archived_identity_name = archive_identity.name or ""
    save_identity_name = save_identity.name or "Unnamed Identity"
    
    # Add note to archived identity indicating it was combined/nested
    archive_notes = list(archive_identity.notes or [])
    archive_notes.append(f"[Combined/Nested with {save_identity_name}]: This identity was combined or nested with '{save_identity_name}'.")
    archive_identity.notes = archive_notes
    archive_identity.state = IdentityState.ARCHIVED
    archive_identity.save(update_fields=["state", "notes", "updated_at"])
    
    log.debug(f"Merged Identity Name: {save_identity.name}")
    log.debug(f"Merged Identity Notes: {save_identity.notes}")
    log.debug(f"Archived Identity: {archived_identity_name} ({archived_identity_id})")

    # Log the action
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.COMBINE_IDENTITIES.value,
        parameters=params.model_dump(),
        result_summary=(
            f"Combined identities into '{save_identity.name}'. Archived '{archived_identity_name}' ({archived_identity_id})."
        ),
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    return None


