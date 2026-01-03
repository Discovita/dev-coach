from enums.coaching_phase import CoachingPhase
from enums.context_keys import ContextKey
from enums.action_type import ActionType
from enums.prompt_type import PromptType
from rest_framework.response import Response
from rest_framework import decorators, viewsets


# CoreView: Class-based view for core utility endpoints
#
# Step-by-step for enums endpoint:
# 1. Handle GET requests to /api/enums.
# 2. Collect all possible values for each enum (coach_state, allowed_actions, context_keys).
# 3. Return them in a single JSON response for use in frontend dropdowns/selects.
# 4. Each enum is returned as a list of objects with 'value' and 'label' for display and value use.
class CoreViewSet(viewsets.GenericViewSet):
    """
    CoreView provides utility endpoints for the frontend, such as enums for dropdowns.
    Used for populating dropdowns/selects in the frontend prompt management UI.
    """

    # TODO: Remove certain ActionTypes enums that are not needed for the frontend.
    @decorators.action(detail=False, methods=["get"], url_path="enums")
    def enums(self, request, *args, **kwargs):
        """
        GET /api/enums
        Returns all enum values for coach_state, allowed_actions, context_keys, and prompt_types.
        """
        coaching_phases = [{"value": c.value, "label": c.label} for c in CoachingPhase]
        allowed_actions = [{"value": a.value, "label": a.label} for a in ActionType]
        context_keys = [{"value": k.value, "label": k.label} for k in ContextKey]
        prompt_types = [{"value": p.value, "label": p.label} for p in PromptType]
        return Response(
            {
                "coaching_phases": coaching_phases,
                "allowed_actions": allowed_actions,
                "context_keys": context_keys,
                "prompt_types": prompt_types,
            }
        )
