from rest_framework import viewsets, status, decorators, mixins, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import TestScenario
from .serializers import TestScenarioSerializer
from .validation import validate_scenario_template
from .services import instantiate_test_scenario


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

    def perform_create(self, serializer):
        template = self.request.data.get("template")
        errors = validate_scenario_template(template)
        if errors:
            raise serializers.ValidationError({"template": errors})
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
        )

    def perform_update(self, serializer):
        template = self.request.data.get("template")
        errors = validate_scenario_template(template)
        if errors:
            raise serializers.ValidationError({"template": errors})
        instance = serializer.save()
        # Re-instantiate scenario with all supported sections
        instantiate_test_scenario(
            instance,
            create_user=True,
            create_coach_state=True,
            create_identities=True,
            create_chat_messages=True,
            create_user_notes=True,
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
        2. Gather all user state: User, CoachState, Identities, ChatMessages, UserNotes
        3. Build a scenario template dict as per canonical schema (strict: only required/optional fields)
        4. Validate the template using validate_scenario_template
        5. Create and save the new TestScenario
        6. Return the serialized scenario or error
        """
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
        first_name = user.first_name or "Test"
        last_name = user.last_name or "User"
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
            if identity.affirmation:
                identity_dict["affirmation"] = identity.affirmation
            if identity.visualization:
                identity_dict["visualization"] = identity.visualization
            if identity.notes:
                identity_dict["notes"] = identity.notes
            identities_section.append(identity_dict)

        # --- ChatMessages section (only fields in TemplateChatMessageSerializer) ---
        from apps.chat_messages.models import ChatMessage
        chat_messages_qs = ChatMessage.objects.filter(user=user).order_by("timestamp")
        chat_messages_section = []
        for msg in chat_messages_qs:
            msg_dict = {
                "role": msg.role,
                "content": msg.content,
            }
            if msg.timestamp:
                msg_dict["timestamp"] = msg.timestamp.isoformat()
            chat_messages_section.append(msg_dict)

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
        )

        # 7. Return the serialized scenario
        serializer = self.get_serializer(scenario)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
