from enums.coaching_phase import CoachingPhase
from enums.context_keys import ContextKey
from enums.action_type import ActionType
from enums.prompt_type import PromptType
from enums.appearance import (
    Gender,
    SkinTone,
    HairColor,
    EyeColor,
    Height,
    Build,
    AgeRange,
)
from enums.appearance.build import BUILDS_MALE, BUILDS_FEMALE, BUILDS_NEUTRAL
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
        Returns all enum values for coach_state, allowed_actions, context_keys, prompt_types, and appearance options.
        """
        coaching_phases = [{"value": c.value, "label": c.label} for c in CoachingPhase]
        allowed_actions = [{"value": a.value, "label": a.label} for a in ActionType]
        context_keys = [{"value": k.value, "label": k.label} for k in ContextKey]
        prompt_types = [{"value": p.value, "label": p.label} for p in PromptType]
        
        # Appearance enums
        genders = [{"value": g.value, "label": g.label} for g in Gender]
        skin_tones = [{"value": s.value, "label": s.label} for s in SkinTone]
        hair_colors = [{"value": h.value, "label": h.label} for h in HairColor]
        eye_colors = [{"value": e.value, "label": e.label} for e in EyeColor]
        heights = [{"value": h.value, "label": h.label} for h in Height]
        age_ranges = [{"value": a.value, "label": a.label} for a in AgeRange]
        
        # Build enums - grouped by gender for frontend filtering
        builds_male = [{"value": b.value, "label": b.label} for b in BUILDS_MALE]
        builds_female = [{"value": b.value, "label": b.label} for b in BUILDS_FEMALE]
        builds_neutral = [{"value": b.value, "label": b.label} for b in BUILDS_NEUTRAL]
        
        return Response(
            {
                "coaching_phases": coaching_phases,
                "allowed_actions": allowed_actions,
                "context_keys": context_keys,
                "prompt_types": prompt_types,
                "appearance": {
                    "genders": genders,
                    "skin_tones": skin_tones,
                    "hair_colors": hair_colors,
                    "eye_colors": eye_colors,
                    "heights": heights,
                    "builds_male": builds_male,
                    "builds_female": builds_female,
                    "builds_neutral": builds_neutral,
                    "age_ranges": age_ranges,
                },
            }
        )
