from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import UpdateIdentityParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

def update_identity(coach_state: CoachState, params: UpdateIdentityParams, coach_message: ChatMessage):
    """
    Update the fields of an existing Identity for the user.
    Only fields provided (not None) in params will be updated.
    Notes are appended to the existing notes list, not replaced.
    """
    # Prepare a dictionary of fields to update, skipping any that are None (except notes)
    update_fields = {}
    if params.name is not None:
        update_fields["name"] = params.name
    if params.i_am_statement is not None:
        update_fields["i_am_statement"] = params.i_am_statement
    if params.visualization is not None:
        update_fields["visualization"] = params.visualization
    if params.state is not None:
        update_fields["state"] = params.state
    if params.category is not None:
        update_fields["category"] = params.category

    # Update all fields except notes in bulk
    if update_fields:
        Identity.objects.filter(id=params.id, user=coach_state.user).update(
            **update_fields
        )

    # If notes are provided, append them to the existing notes list
    if params.notes is not None:
        identity = Identity.objects.get(id=params.id, user=coach_state.user)
        # Ensure notes is a list
        current_notes = identity.notes or []
        # Append each note from params.notes
        current_notes.extend(params.notes)
        identity.notes = current_notes
        identity.save()
    
    # Get the updated identity for logging
    identity = Identity.objects.get(id=params.id, user=coach_state.user)
    
    # Build a detailed summary of what was updated
    updated_fields = []
    if params.name is not None:
        updated_fields.append("name")
    if params.i_am_statement is not None:
        updated_fields.append("i_am_statement")
    if params.visualization is not None:
        updated_fields.append("visualization")
    if params.state is not None:
        updated_fields.append("state")
    if params.category is not None:
        updated_fields.append("category")
    if params.notes is not None:
        updated_fields.append("notes")
    
    # Create a more specific result summary
    if updated_fields:
        fields_text = ", ".join(updated_fields)
        result_summary = f"Updated identity '{identity.name}' fields: {fields_text}"
    else:
        result_summary = f"Updated identity '{identity.name}' (no changes made)"
    
    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.UPDATE_IDENTITY.value,
        parameters=params.model_dump(),
        result_summary=result_summary,
        coach_message=coach_message,
        test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
    )
