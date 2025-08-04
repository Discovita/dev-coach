from apps.users.models import User
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from apps.chat_messages.models import ChatMessage
from apps.user_notes.models import UserNote
from apps.actions.models import Action
import hashlib
import uuid
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def instantiate_test_scenario(
    scenario,
    create_user=True,
    create_chat_messages=False,
    create_identities=False,
    create_coach_state=False,
    create_user_notes=False,
    create_actions=False,
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
        password = "Coach123!"
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

    # Handle identities creation FIRST (before coach_state to ensure identities exist for linking)
    created_identities = {}
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
            # Store reference by name for later linking
            created_identities[identity.name] = identity

    # Handle coach_state creation AFTER identities are created
    if create_coach_state and template.get("coach_state") and created_user:
        coach_state_data = template["coach_state"].copy()
        # Remove any fields that are not in the model (defensive, in case template changes)
        allowed_fields = {f.name for f in CoachState._meta.get_fields()}

        # Handle current_identity reference - map name to Identity object
        current_identity_name = coach_state_data.pop("current_identity", None)
        # Remove proposed_identity as requested - we're not handling it
        coach_state_data.pop("proposed_identity", None)

        # Set required fields
        coach_state_data["test_scenario"] = scenario
        # Update the existing CoachState (created automatically by signal upon user creation)
        coach_state = CoachState.objects.get(user=created_user)
        for key, value in coach_state_data.items():
            if key in allowed_fields:
                setattr(coach_state, key, value)

        # Set current_identity reference if it exists and we have the identity
        if current_identity_name and current_identity_name in created_identities:
            coach_state.current_identity = created_identities[current_identity_name]
        elif current_identity_name:
            # Try to find existing identity if not just created
            try:
                current_identity = Identity.objects.get(
                    user=created_user,
                    test_scenario=scenario,
                    name=current_identity_name,
                )
                coach_state.current_identity = current_identity
            except Identity.DoesNotExist:
                # Log warning but don't fail - the identity might not exist yet
                print(
                    f"Warning: Current identity '{current_identity_name}' not found for user {created_user.id}"
                )

        coach_state.save()
        created_coach_state = coach_state

    # Handle chat messages creation
    created_chat_messages = []
    if create_chat_messages and template.get("chat_messages") and created_user:
        # Delete existing chat messages for this user and scenario
        ChatMessage.objects.filter(user=created_user, test_scenario=scenario).delete()
        for msg_data in template["chat_messages"]:
            chat_message = ChatMessage.objects.create(
                user=created_user,
                test_scenario=scenario,
                role=msg_data.get("role"),
                content=msg_data.get("content"),
                # timestamp is auto-set, but can be set if provided
                timestamp=(
                    msg_data.get("timestamp") if msg_data.get("timestamp") else None
                ),
            )
            created_chat_messages.append(chat_message)

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
                created_at=(
                    note_data.get("created_at") if note_data.get("created_at") else None
                ),
            )

    # Handle actions creation AFTER chat messages are created
    if create_actions and template.get("actions") and created_user:
        # Delete existing actions for this user and scenario
        Action.objects.filter(user=created_user, test_scenario=scenario).delete()
        
        for action_data in template["actions"]:
            # Find the corresponding coach message by content matching
            coach_message = None
            if action_data.get("coach_message_content"):
                # Try to find a coach message with matching content
                try:
                    coach_message = ChatMessage.objects.get(
                        user=created_user,
                        test_scenario=scenario,
                        role="coach",
                        content=action_data["coach_message_content"]
                    )
                except ChatMessage.DoesNotExist:
                    # If no exact match, try to find the most recent coach message
                    # This is a fallback for cases where content might have slight variations
                    log.warning("Using fallback chat message for action relationship")
                    coach_message = ChatMessage.objects.filter(
                        user=created_user,
                        test_scenario=scenario,
                        role="coach"
                    ).order_by("-timestamp").first()
            
            # Create the action
            action = Action(
                user=created_user,
                test_scenario=scenario,
                action_type=action_data.get("action_type"),
                parameters=action_data.get("parameters", {}),
                result_summary=action_data.get("result_summary", ""),
                timestamp=(
                    action_data.get("timestamp") if action_data.get("timestamp") else None
                ),
                coach_message=coach_message,
            )
            action.save()

    return {
        "user": created_user,
        "coach_state": created_coach_state,
        "email": unique_email,
    }
