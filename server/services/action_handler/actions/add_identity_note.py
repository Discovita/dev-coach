from apps.identities.models import Identity
from apps.coach_states.models import CoachState

def add_identity_note(coach_state: CoachState, params):
    """
    Append a note to the notes list of the specified Identity.
    """
    identity = Identity.objects.get(id=params["id"], user=coach_state.user)
    notes = identity.notes or []
    notes.append(params["note"])
    identity.notes = notes
    identity.save() 