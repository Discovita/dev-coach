"""
CoreViewSet — utility endpoints for the frontend (enums, config, etc.).
"""

from rest_framework import decorators, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from enums.action_type import ActionType
from enums.appearance import (
    AgeRange,
    EyeColor,
    Gender,
    HairColor,
    Height,
    SkinTone,
)
from enums.appearance.build import BUILDS_FEMALE, BUILDS_MALE, BUILDS_NEUTRAL
from enums.coaching_phase import CoachingPhase
from enums.context_keys import ContextKey
from enums.prompt_type import PromptType


class CoreViewSet(viewsets.GenericViewSet):
    """
    Utility endpoints for the frontend.

    Endpoints (trailing_slash=False router):
    - GET /api/v1/core/enums → enums()
    """

    permission_classes = [IsAuthenticated]

    # TODO: Remove certain ActionTypes enums that are not needed for the frontend.
    @decorators.action(detail=False, methods=["get"], url_path="enums")
    def enums(self, request: Request) -> Response:
        """
        GET /api/v1/core/enums

        Returns all enum values for coaching phases, allowed actions,
        context keys, prompt types, and appearance options. Used for
        populating dropdowns/selects in the frontend prompt management UI.
        """
        coaching_phases = [{"value": c.value, "label": c.label} for c in CoachingPhase]
        allowed_actions = [{"value": a.value, "label": a.label} for a in ActionType]
        context_keys = [{"value": k.value, "label": k.label} for k in ContextKey]
        prompt_types = [{"value": p.value, "label": p.label} for p in PromptType]

        genders = [{"value": g.value, "label": g.label} for g in Gender]
        skin_tones = [{"value": s.value, "label": s.label} for s in SkinTone]
        hair_colors = [{"value": h.value, "label": h.label} for h in HairColor]
        eye_colors = [{"value": e.value, "label": e.label} for e in EyeColor]
        heights = [{"value": h.value, "label": h.label} for h in Height]
        age_ranges = [{"value": a.value, "label": a.label} for a in AgeRange]

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
