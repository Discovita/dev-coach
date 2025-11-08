from apps.users.models import User
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from apps.chat_messages.models import ChatMessage
from apps.user_notes.models import UserNote
from apps.actions.models import Action
import hashlib
import uuid
import os
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
                i_am_statement=identity_data.get("i_am_statement", ""),
                visualization=identity_data.get("visualization", ""),
                notes=identity_data.get("notes", []),
            )
            # Handle image copying from template URL
            image_url = identity_data.get("image")
            if image_url:
                from .utils import copy_image_from_url
                from django.core.files.storage import default_storage
                copied_key = copy_image_from_url(image_url)
                if copied_key:
                    # Open the copied file and assign to identity.image
                    copied_file = default_storage.open(copied_key, 'rb')
                    identity.image.save(
                        os.path.basename(copied_key),
                        copied_file,
                        save=False  # Don't save yet, we'll save the identity below
                    )
                    copied_file.close()
                    log.info(f"Copied image for identity {identity.name} from {image_url}")
                else:
                    log.warning(f"Failed to copy image for identity {identity.name} from {image_url}, continuing without image")
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
    # Create a mapping from original message data to new message objects for action linking
    original_to_new_message_mapping = {}
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
                # component_config is optional
                component_config=msg_data.get("component_config"),
            )
            created_chat_messages.append(chat_message)
            
            # Create mapping key from message data for action linking
            message_key = f"{msg_data.get('role')}|{msg_data.get('content')}|{msg_data.get('timestamp', '')}"
            original_to_new_message_mapping[message_key] = chat_message

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
            # Find the corresponding coach message using ID-based mapping (preferred) or content matching (fallback)
            coach_message = None
            
            # Try ID-based mapping first (new approach)
            if action_data.get("original_coach_message_id") and template.get("original_message_mapping"):
                # Get the original message data from the mapping
                original_msg_id = action_data["original_coach_message_id"]
                original_msg_data = template["original_message_mapping"].get(original_msg_id)
                
                if original_msg_data:
                    # Create the same mapping key used when creating messages
                    message_key = f"{original_msg_data.get('role')}|{original_msg_data.get('content')}|{original_msg_data.get('timestamp', '')}"
                    coach_message = original_to_new_message_mapping.get(message_key)
                    
                    if not coach_message:
                        log.warning(f"Could not find new message for original ID {original_msg_id}, using fallback")
                        # Fallback to most recent coach message
                        coach_message = ChatMessage.objects.filter(
                            user=created_user,
                            test_scenario=scenario,
                            role="coach"
                        ).order_by("-timestamp").first()
                else:
                    log.warning(f"Original message data not found for ID {original_msg_id}, using fallback")
                    # Fallback to most recent coach message
                    coach_message = ChatMessage.objects.filter(
                        user=created_user,
                        test_scenario=scenario,
                        role="coach"
                    ).order_by("-timestamp").first()
            
            # Fallback to content-based matching for old templates
            elif action_data.get("coach_message_content"):
                log.warning("Using deprecated coach_message_content field, consider updating template")
                # Use filter().first() instead of get() to handle multiple matches
                coach_messages = ChatMessage.objects.filter(
                    user=created_user,
                    test_scenario=scenario,
                    role="coach",
                    content=action_data["coach_message_content"]
                ).order_by("-timestamp")
                
                if coach_messages.exists():
                    coach_message = coach_messages.first()
                    # Log if we found multiple matches to help with debugging
                    if coach_messages.count() > 1:
                        log.warning(f"Found {coach_messages.count()} coach messages with same content, using most recent")
                else:
                    # If no exact match, try to find the most recent coach message
                    log.warning("No exact coach message match found, using fallback chat message for action relationship")
                    coach_message = ChatMessage.objects.filter(
                        user=created_user,
                        test_scenario=scenario,
                        role="coach"
                    ).order_by("-timestamp").first()
            
            # Final fallback
            else:
                log.warning("No coach message linking found, using fallback chat message for action relationship")
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
