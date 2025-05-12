from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from services.action_handler.models import UpdateIdentityParams


def update_identity(coach_state: CoachState, params: UpdateIdentityParams):
    """
    Update the fields of an existing Identity for the user.
    Only fields provided (not None) in params will be updated.
    Notes are appended to the existing notes list, not replaced.
    """
    # Prepare a dictionary of fields to update, skipping any that are None (except notes)
    update_fields = {}
    if params.name is not None:
        update_fields["name"] = params.name
    if params.affirmation is not None:
        update_fields["affirmation"] = params.affirmation
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
