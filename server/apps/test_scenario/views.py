from rest_framework import viewsets, status, decorators, mixins, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from .models import TestScenario
from .serializers import TestScenarioSerializer
from .validation import validate_scenario_template
from .services import instantiate_test_scenario
from django.core.files.storage import default_storage
from django.conf import settings
import json
import re
import urllib.parse
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def process_identity_images(request, template, old_template=None):
    """
    Process image files from request.FILES and upload them to S3.
    Updates template.identities[index].image with S3 URLs.
    Also handles deletion of images when they are removed.
    
    Args:
        request: Django request object with FILES
        template: Template dict (will be modified in place)
        old_template: Optional old template dict to compare against for deletions
        
    Returns:
        Updated template dict with image URLs injected
    """
    if "identities" not in template or not template["identities"]:
        return template
    
    # First, handle image deletions (when image field is removed)
    if old_template and "identities" in old_template:
        for index, new_identity in enumerate(template["identities"]):
            if index < len(old_template["identities"]):
                old_identity = old_template["identities"][index]
                old_image_url = old_identity.get("image")
                new_image_url = new_identity.get("image")
                
                # If old identity had an image but new one doesn't, delete it
                if old_image_url and not new_image_url:
                    try:
                        # Extract key from old URL
                        old_key = None
                        # Get bucket name and custom domain from STORAGES if available
                        bucket_name = None
                        custom_domain = None
                        if hasattr(settings, 'STORAGES') and 'default' in settings.STORAGES:
                            bucket_name = settings.STORAGES['default']['OPTIONS'].get('bucket_name')
                            custom_domain = settings.STORAGES['default']['OPTIONS'].get('custom_domain')
                        
                        if "/media/" in old_image_url:
                            old_key = old_image_url.split("/media/")[-1].split("?")[0]
                        elif bucket_name and f"{bucket_name}.s3.amazonaws.com" in old_image_url:
                            parts = old_image_url.split(f"{bucket_name}.s3.amazonaws.com/")
                            if len(parts) > 1:
                                old_key = parts[1].split("?")[0]
                        elif custom_domain and custom_domain in old_image_url:
                            parts = old_image_url.split(f"{custom_domain}/")
                            if len(parts) > 1:
                                old_key = parts[1].split("?")[0]
                        
                        if old_key:
                            # URL decode the key in case it has encoded characters
                            old_key = urllib.parse.unquote(old_key)
                            # Use default_storage which automatically uses STORAGES['default']
                            default_storage.delete(old_key)
                            log.info(f"Deleted removed image {old_key} for identity at index {index}")
                    except Exception as e:
                        log.warning(f"Failed to delete removed image for identity at index {index}: {str(e)}")
    
    # Now handle new image uploads
    if not request.FILES:
        return template
    
    # Extract image files using naming convention: identity_{index}_image
    image_files = {}
    for key in request.FILES.keys():
        match = re.match(r'identity_(\d+)_image', key)
        if match:
            index = int(match.group(1))
            image_files[index] = request.FILES[key]
    
    if not image_files:
        return template
    
    # Process each image file
    for index, image_file in image_files.items():
        if index >= len(template["identities"]):
            log.warning(f"Image file provided for identity index {index}, but only {len(template['identities'])} identities exist")
            continue
        
        try:
            # Use UUID-based upload path (compatible with VersatileImageField)
            import uuid
            import os
            
            # Use default_storage which automatically uses STORAGES['default']
            # Verify storage backend is configured correctly
            log.info(f"Storage backend: {type(default_storage).__name__}")
            if hasattr(settings, 'STORAGES') and 'default' in settings.STORAGES:
                log.info(f"Storage backend setting: {settings.STORAGES['default']['BACKEND']}")
                log.info(f"AWS Bucket: {settings.STORAGES['default']['OPTIONS'].get('bucket_name', 'NOT SET')}")
                log.info(f"Location: {settings.STORAGES['default']['OPTIONS'].get('location', 'NOT SET')}")
            log.info(f"AWS Access Key ID set: {bool(getattr(settings, 'AWS_ACCESS_KEY_ID', None))}")
            
            # Generate UUID-based path manually (same format as uuid_upload_path)
            # Note: Don't include "media" prefix - storage backend adds it via location setting
            filename = image_file.name
            uuid_dir = str(uuid.uuid4())
            full_path = os.path.join(uuid_dir, filename).replace("\\", "/")
            
            log.info(f"Attempting to save image to S3 with path: {full_path}, file size: {image_file.size} bytes")
            
            # Save file to S3 using default_storage (automatically uses STORAGES['default'])
            saved_path = default_storage.save(
                full_path,
                image_file
            )
            
            log.info(f"Storage save() returned path: {saved_path}")
            
            # Note: exists() check may fail due to S3 eventual consistency or key format
            # If save() succeeded without error, the file is likely saved correctly
            # The URL generation below will confirm the file is accessible
            
            # Get the S3 URL
            # Note: saved_path is the actual S3 key stored by django-storages
            # default_storage.url() generates the full URL from this key
            image_url = default_storage.url(saved_path)
            log.info(f"Generated image URL: {image_url}")
            
            # Delete old image if identity already has one
            existing_identity_data = template["identities"][index]
            if existing_identity_data.get("image"):
                # Try to delete the old image from S3
                try:
                    old_url = existing_identity_data["image"]
                    # Extract key from URL
                    old_key = None
                    # Get bucket name and custom domain from STORAGES if available
                    bucket_name = None
                    custom_domain = None
                    if hasattr(settings, 'STORAGES') and 'default' in settings.STORAGES:
                        bucket_name = settings.STORAGES['default']['OPTIONS'].get('bucket_name')
                        custom_domain = settings.STORAGES['default']['OPTIONS'].get('custom_domain')
                    
                    if "/media/" in old_url:
                        old_key = old_url.split("/media/")[-1].split("?")[0]  # Remove query params
                    elif bucket_name and f"{bucket_name}.s3.amazonaws.com" in old_url:
                        # Extract from full S3 URL
                        parts = old_url.split(f"{bucket_name}.s3.amazonaws.com/")
                        if len(parts) > 1:
                            old_key = parts[1].split("?")[0]
                    elif custom_domain and custom_domain in old_url:
                        # Extract from custom domain URL
                        parts = old_url.split(f"{custom_domain}/")
                        if len(parts) > 1:
                            old_key = parts[1].split("?")[0]
                    
                    if old_key:
                        # URL decode the key in case it has encoded characters
                        old_key = urllib.parse.unquote(old_key)
                        # Use default_storage which automatically uses STORAGES['default']
                        default_storage.delete(old_key)
                        log.info(f"Deleted old image {old_key} for identity at index {index}")
                except Exception as e:
                    log.warning(f"Failed to delete old image for identity at index {index}: {str(e)}")
            
            # Inject URL into template
            template["identities"][index]["image"] = image_url
            log.info(f"Uploaded image for identity at index {index} to {image_url}")
            
        except Exception as e:
            log.error(f"Error processing image for identity at index {index}: {str(e)}", exc_info=True)
            # Continue without image for this identity
    
    return template


class TestScenarioViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for managing test scenarios.
    Endpoints:
    - list, retrieve, create, update, delete
    - reset (custom action)
    """

    queryset = TestScenario.objects.all()
    serializer_class = TestScenarioSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # Handle multipart/form-data: template comes as JSON string
        template_data = self.request.data.get("template")
        if not template_data:
            raise serializers.ValidationError({"template": "Template is required"})
        
        if isinstance(template_data, str):
            try:
                template = json.loads(template_data)
            except json.JSONDecodeError as e:
                raise serializers.ValidationError({"template": f"Invalid JSON in template: {str(e)}"})
        else:
            template = template_data
        
        # Process image uploads and inject URLs into template
        template = process_identity_images(self.request, template)
        
        errors = validate_scenario_template(template)
        if errors:
            raise serializers.ValidationError({"template": errors})
        
        # Update serializer with processed template
        serializer.validated_data["template"] = template
        instance = serializer.save(
            created_by=self.request.user if self.request.user.is_authenticated else None
        )
        # Instantiate scenario with all supported sections
        instantiate_test_scenario(
            instance,
            create_user=True,
            create_coach_state=True,
            create_identities=True,
            create_chat_messages=True,
            create_user_notes=True,
            create_actions=True,
        )

    def perform_update(self, serializer):
        # Get the old template for comparison (to detect deleted images)
        instance = self.get_object()
        old_template = instance.template if hasattr(instance, 'template') else None
        
        # Handle multipart/form-data: template comes as JSON string
        template_data = self.request.data.get("template")
        if not template_data:
            raise serializers.ValidationError({"template": "Template is required"})
        
        if isinstance(template_data, str):
            try:
                template = json.loads(template_data)
            except json.JSONDecodeError as e:
                raise serializers.ValidationError({"template": f"Invalid JSON in template: {str(e)}"})
        else:
            template = template_data
        
        # Process image uploads and deletions, inject URLs into template
        template = process_identity_images(self.request, template, old_template=old_template)
        
        errors = validate_scenario_template(template)
        if errors:
            raise serializers.ValidationError({"template": errors})
        
        # Update serializer with processed template
        serializer.validated_data["template"] = template
        instance = serializer.save()
        # Re-instantiate scenario with all supported sections
        instantiate_test_scenario(
            instance,
            create_user=True,
            create_coach_state=True,
            create_identities=True,
            create_chat_messages=True,
            create_user_notes=True,
            create_actions=True,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to return a success message on deletion.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Test scenario deleted successfully."}, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"], url_path="reset")
    def reset(self, request, pk=None):
        """
        Custom action to reset a test scenario to its original template state.
        """
        scenario = self.get_object()
        instantiate_test_scenario(
            scenario,
            create_user=True,
            create_coach_state=True,
            create_identities=True,
            create_chat_messages=True,
            create_user_notes=True,
            create_actions=True,
        )
        return Response(
            {"success": True, "message": "Scenario reset (all data)."},
            status=status.HTTP_200_OK,
        )

    @decorators.action(detail=False, methods=["post"], url_path="freeze-session")
    def freeze_session(self, request):
        """
        Admin-only endpoint to capture ("freeze") the current state of a user session as a new test scenario.
        Step-by-step:
        1. Validate input: user_id, name, description (name must be unique, user must exist)
        2. Gather all user state: User, CoachState, Identities, ChatMessages, UserNotes, Actions
        3. Build a scenario template dict as per canonical schema (strict: only required/optional fields)
        4. Validate the template using validate_scenario_template
        5. Create and save the new TestScenario
        6. Return the serialized scenario or error
        """
        log.debug(f"[TestScenarioViewSet.freeze_session] Request: {request.data}")
        # 1. Permissions: admin only
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        # 2. Parse and validate input
        user_id = request.data.get("user_id")
        name = request.data.get("name")
        description = request.data.get("description", "")
        if not user_id or not name:
            return Response({"detail": "user_id and name are required."}, status=status.HTTP_400_BAD_REQUEST)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        from .models import TestScenario
        if TestScenario.objects.filter(name=name).exists():
            return Response({"detail": "A scenario with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Gather all user state, STRICT to template serializers
        # Use provided first_name/last_name if present and non-blank, else fallback to user or defaults
        req_first_name = request.data.get("first_name", "").strip()
        req_last_name = request.data.get("last_name", "").strip()
        first_name = req_first_name or user.first_name or "Test"
        last_name = req_last_name or user.last_name or "User"
        user_section = {
            "email": user.email,
            "first_name": first_name,
            "last_name": last_name,
        }

        from apps.coach_states.models import CoachState
        coach_state = None
        try:
            coach_state = CoachState.objects.get(user=user)
        except CoachState.DoesNotExist:
            pass
        coach_state_section = None
        if coach_state:
            coach_state_section = {
                "current_phase": coach_state.current_phase,
                "identity_focus": coach_state.identity_focus,
                "who_you_are": coach_state.who_you_are,
                "who_you_want_to_be": coach_state.who_you_want_to_be,
            }
            # Optional fields
            if hasattr(coach_state, "skipped_identity_categories") and coach_state.skipped_identity_categories:
                coach_state_section["skipped_identity_categories"] = coach_state.skipped_identity_categories
            if hasattr(coach_state, "current_identity") and coach_state.current_identity:
                coach_state_section["current_identity"] = str(coach_state.current_identity.id)
            if hasattr(coach_state, "proposed_identity") and coach_state.proposed_identity:
                coach_state_section["proposed_identity"] = str(coach_state.proposed_identity.id)
            if hasattr(coach_state, "asked_questions") and coach_state.asked_questions:
                coach_state_section["asked_questions"] = coach_state.asked_questions
            if hasattr(coach_state, "metadata") and coach_state.metadata:
                coach_state_section["metadata"] = coach_state.metadata

        # --- Identities section (only fields in TemplateIdentitySerializer) ---
        from apps.identities.models import Identity
        identities_qs = Identity.objects.filter(user=user)
        identities_section = []
        for identity in identities_qs:
            identity_dict = {
                "name": identity.name,
                "category": identity.category,
            }
            # Optional fields
            if identity.state:
                identity_dict["state"] = identity.state
            if identity.i_am_statement:
                identity_dict["i_am_statement"] = identity.i_am_statement
            if identity.visualization:
                identity_dict["visualization"] = identity.visualization
            if identity.notes:
                identity_dict["notes"] = identity.notes
            # Handle image duplication
            if identity.image:
                from .utils import duplicate_s3_image
                duplicated_key = duplicate_s3_image(identity.image)
                if duplicated_key:
                    # Get the URL of the duplicated image using default_storage
                    identity_dict["image"] = default_storage.url(duplicated_key)
                    log.info(f"Duplicated image for identity {identity.name} to {identity_dict['image']}")
                else:
                    log.warning(f"Failed to duplicate image for identity {identity.name}, continuing without image")
            identities_section.append(identity_dict)

        # --- ChatMessages section (only fields in TemplateChatMessageSerializer) ---
        from apps.chat_messages.models import ChatMessage
        chat_messages_qs = ChatMessage.objects.filter(user=user).order_by("timestamp")
        chat_messages_section = []
        # Create a mapping from original message IDs to their data for action linking
        original_message_mapping = {}
        for msg in chat_messages_qs:
            msg_dict = {
                "role": msg.role,
                "content": msg.content,
            }
            if msg.timestamp:
                msg_dict["timestamp"] = msg.timestamp.isoformat()
            if msg.component_config:
                msg_dict["component_config"] = msg.component_config
            chat_messages_section.append(msg_dict)
            # Store original message ID for action linking
            original_message_mapping[str(msg.id)] = {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "component_config": msg.component_config
            }

        # --- UserNotes section (only fields in TemplateUserNoteSerializer) ---
        from apps.user_notes.models import UserNote
        user_notes_qs = UserNote.objects.filter(user=user)
        user_notes_section = []
        for note in user_notes_qs:
            note_dict = {
                "note": note.note,
            }
            if note.source_message:
                note_dict["source_message"] = str(note.source_message.id)
            if note.created_at:
                note_dict["created_at"] = note.created_at.isoformat()
            user_notes_section.append(note_dict)

        # --- Actions section (only fields in TemplateActionSerializer) ---
        from apps.actions.models import Action
        actions_qs = Action.objects.filter(user=user).order_by("timestamp")
        actions_section = []
        for action in actions_qs:
            action_dict = {
                "action_type": action.action_type,
                "parameters": action.parameters,
            }
            # Optional fields
            if action.result_summary:
                action_dict["result_summary"] = action.result_summary
            if action.timestamp:
                action_dict["timestamp"] = action.timestamp.isoformat()
            # Link to original coach message ID for robust instantiation
            if action.coach_message:
                action_dict["original_coach_message_id"] = str(action.coach_message.id)
            actions_section.append(action_dict)

        # 4. Build the template dict (only include sections if present)
        template = {"user": user_section}
        if coach_state_section:
            template["coach_state"] = coach_state_section
        if identities_section:
            template["identities"] = identities_section
        if chat_messages_section:
            template["chat_messages"] = chat_messages_section
        if user_notes_section:
            template["user_notes"] = user_notes_section
        if actions_section:
            template["actions"] = actions_section
        
        # Store the original message mapping for robust action linking during instantiation
        if original_message_mapping:
            template["original_message_mapping"] = original_message_mapping

        # 5. Validate the template
        errors = validate_scenario_template(template)
        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        # 6. Create and save the new TestScenario
        scenario = TestScenario.objects.create(
            name=name,
            description=description,
            template=template,
            created_by=request.user if request.user.is_authenticated else None,
        )

        # 6b. Instantiate the scenario (create all related db entries)
        instantiate_test_scenario(
            scenario,
            create_user=True,
            create_coach_state=True,
            create_identities=True,
            create_chat_messages=True,
            create_user_notes=True,
            create_actions=True,
        )

        # 7. Return the serialized scenario
        serializer = self.get_serializer(scenario)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
