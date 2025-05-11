from enums.coaching_state import CoachingState
from enums.context_keys import ContextKey
from enums.action_type import ActionType
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

    @decorators.action(detail=False, methods=["get"], url_path="enums")
    def enums(self, request, *args, **kwargs):
        """
        GET /api/enums
        Returns all enum values for coach_state, allowed_actions, and context_keys.
        """
        coach_states = [{"value": c.value, "label": c.label} for c in CoachingState]
        allowed_actions = [{"value": a.value, "label": a.label} for a in ActionType]
        context_keys = [{"value": k.value, "label": k.label} for k in ContextKey]
        return Response(
            {
                "coach_states": coach_states,
                "allowed_actions": allowed_actions,
                "context_keys": context_keys,
            }
        )
