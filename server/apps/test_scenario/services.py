from apps.users.models import User
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from apps.chat_messages.models import ChatMessage
from apps.user_notes.models import UserNote
import hashlib
import uuid


def instantiate_test_scenario(
    scenario,
    create_user=True,
    create_chat_messages=False,
    create_identities=False,
    create_coach_state=False,
    create_user_notes=False,
):
    """
    Instantiates a test scenario from its template.
    For now, only handles user creation (incremental step).
    Deletes any existing user(s) for this scenario, then creates a new one.
    Now also handles coach state creation if requested.
    """
    template = scenario.template
    created_user = None
    created_coach_state = None
    if create_user:
        # Delete any existing user(s) for this scenario
        User.objects.filter(test_scenario=scenario).delete()
        user_data = template.get("user") or {}
        # Always set password to 'Coach123!'
        password = 'Coach123!'
        # Generate a unique email if not provided or not unique
        base_email = user_data.get("email")
        unique_email = None
        if not base_email or User.objects.filter(email=base_email).exists():
            # Use scenario id and a uuid4 for uniqueness
            hash_input = f"{scenario.id}-{uuid.uuid4()}"
            hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
            unique_email = f"test_user_{hash_digest}@testscenario.com"
        else:
            unique_email = base_email
        user_data["email"] = unique_email
        user_data["password"] = password
        # Remove password from user_data to set it properly
        user_data.pop("password", None)
        user = User(**user_data, test_scenario=scenario)
        user.set_password(password)
        user.save()
        created_user = user

    # Handle coach_state creation
    if create_coach_state and template.get("coach_state") and created_user:
        coach_state_data = template["coach_state"].copy()
        # Remove any fields that are not in the model (defensive, in case template changes)
        allowed_fields = {f.name for f in CoachState._meta.get_fields()}
        # Remove foreign key fields that require objects, not IDs (current_identity, proposed_identity)
        coach_state_data.pop("current_identity", None)
        coach_state_data.pop("proposed_identity", None)
        # Set required fields
        coach_state_data["test_scenario"] = scenario
        # Update the existing CoachState (created automatically by signal upon user creation)
        coach_state = CoachState.objects.get(user=created_user)
        for key, value in coach_state_data.items():
            if key in allowed_fields:
                setattr(coach_state, key, value)
        coach_state.save()
        created_coach_state = coach_state

    # Handle identities creation
    if create_identities and template.get("identities") and created_user:
        # Delete existing identities for this user and scenario
        Identity.objects.filter(user=created_user, test_scenario=scenario).delete()
        for identity_data in template["identities"]:
            identity = Identity(
                user=created_user,
                test_scenario=scenario,
                name=identity_data.get("name"),
                category=identity_data.get("category"),
                state=identity_data.get("state"),
                affirmation=identity_data.get("affirmation", ""),
                visualization=identity_data.get("visualization", ""),
                notes=identity_data.get("notes", []),
            )
            identity.save()

    # Handle chat messages creation
    if create_chat_messages and template.get("chat_messages") and created_user:
        # Delete existing chat messages for this user and scenario
        ChatMessage.objects.filter(user=created_user, test_scenario=scenario).delete()
        for msg_data in template["chat_messages"]:
            ChatMessage.objects.create(
                user=created_user,
                test_scenario=scenario,
                role=msg_data.get("role"),
                content=msg_data.get("content"),
                # timestamp is auto-set, but can be set if provided
                timestamp=msg_data.get("timestamp") if msg_data.get("timestamp") else None,
            )

    # Handle user notes creation
    if create_user_notes and template.get("user_notes") and created_user:
        # Delete existing user notes for this user and scenario
        UserNote.objects.filter(user=created_user, test_scenario=scenario).delete()
        for note_data in template["user_notes"]:
            UserNote.objects.create(
                user=created_user,
                test_scenario=scenario,
                note=note_data.get("note"),
                source_message=None,  # Could be linked if message IDs are handled
                created_at=note_data.get("created_at") if note_data.get("created_at") else None,
            )
    return {"user": created_user, "coach_state": created_coach_state, "email": unique_email}
