from typing import List, Optional, TypedDict

from django.db import models


class CoachingPhase(models.TextChoices):
    """
    Enum for the possible coaching state in the coaching system.
    """

    # This was added so that we could control the content of the system_context sent to the LLM via the web interface. SYSTEM_CONTEXT is not a phase in the coaching process, but a context that is always sent to the LLM.
    SYSTEM_CONTEXT = "system_context", "System Context"
    INTRODUCTION = "introduction", "Introduction"
    GET_TO_KNOW_YOU = "get_to_know_you", "Get to Know You"
    IDENTITY_WARMUP = "identity_warm_up", "Identity Warm-Up"
    IDENTITY_BRAINSTORMING = "identity_brainstorming", "Identity Brainstorming"
    BRAINSTORMING_REVIEW = "brainstorming_review", "Brainstorming Review"
    IDENTITY_REFINEMENT = "identity_refinement", "Identity Refinement"
    ANYTHING_MISSING = "anything_missing", "Anything Missing"
    IDENTITY_COMMITMENT = "identity_commitment", "Identity Commitment"
    I_AM_STATEMENT = "i_am_statement", "I Am Statement"
    IDENTITY_VISUALIZATION = "identity_visualization", "Identity Visualization"

    @classmethod
    def from_string(cls, value: str) -> "CoachingPhase":
        """
        Convert a string to an CoachingState enum value, accepting flexible input.
        """
        normalized = value.lower().replace(" ", "_").replace("-", "_")
        for member in cls:
            if member.name.lower() == normalized or member.value.lower() == normalized:
                return member
        valid_types = ", ".join([t.name for t in cls])
        raise ValueError(
            f"Unknown identity category: {value}. Valid categories: {valid_types}"
        )

    def __str__(self) -> str:
        """
        Get a human-readable string representation of the identity category.
        """
        return self.label


# ---------------------------------------------------------------------------
# Coaching sessions
# ---------------------------------------------------------------------------
# A "session" groups one or more consecutive CoachingPhases that belong
# together for the purpose of intro/outro video boundaries and breaks. The
# SESSIONS map is the source of truth for which phases form which session
# and which video keys are attached to each side.
#
# - The session key is the dict key (suffixed `_session` so callers never
#   confuse it with a CoachingPhase value).
# - `phases` is the ordered list of CoachingPhase members in this session.
# - `intro` / `outro` are video keys; `None` means no video on that side.
#
# SYSTEM_CONTEXT is intentionally absent — it is a meta-phase used only to
# control system context for the LLM, not a real coaching phase.


class SessionMeta(TypedDict):
    phases: List[CoachingPhase]
    intro: Optional[str]
    outro: Optional[str]


SESSIONS: dict[str, SessionMeta] = {
    "welcome_session": {
        "phases": [CoachingPhase.INTRODUCTION],
        "intro": "welcome_session_intro",
        "outro": None,
    },
    "get_to_know_session": {
        "phases": [CoachingPhase.GET_TO_KNOW_YOU, CoachingPhase.IDENTITY_WARMUP],
        # No intro video: the coach introduces this phase itself. (The
        # Introduction-phase transition is the lead-in to get-to-know.)
        "intro": None,
        "outro": "get_to_know_session_outro",
    },
    "brainstorming_session": {
        "phases": [
            CoachingPhase.IDENTITY_BRAINSTORMING,
            CoachingPhase.BRAINSTORMING_REVIEW,
        ],
        "intro": "brainstorming_session_intro",
        "outro": "brainstorming_session_outro",
    },
    "refinement_session": {
        "phases": [
            CoachingPhase.IDENTITY_REFINEMENT,
            CoachingPhase.ANYTHING_MISSING,
        ],
        "intro": "refinement_session_intro",
        "outro": "refinement_session_outro",
    },
    "commitment_session": {
        "phases": [CoachingPhase.IDENTITY_COMMITMENT],
        "intro": "commitment_session_intro",
        "outro": "commitment_session_outro",
    },
    "i_am_session": {
        "phases": [CoachingPhase.I_AM_STATEMENT],
        "intro": "i_am_session_intro",
        "outro": "i_am_session_outro",
    },
    "visualization_session": {
        "phases": [CoachingPhase.IDENTITY_VISUALIZATION],
        "intro": "visualization_session_intro",
        "outro": None,
    },
}


def session_of(phase: CoachingPhase) -> str:
    """
    Return the session key that contains `phase`.

    Raises ValueError if `phase` does not belong to any session (e.g.,
    SYSTEM_CONTEXT, which is a meta-phase, not a coaching phase).
    """
    for session_key, meta in SESSIONS.items():
        if phase in meta["phases"]:
            return session_key
    raise ValueError(
        f"Phase {phase!r} does not belong to any session in SESSIONS."
    )


def is_first_phase_of_session(phase: CoachingPhase) -> bool:
    """
    True iff `phase` is the first phase listed in its session.

    The intro-video trigger boundary. Returns False for phases not in any
    session (e.g., SYSTEM_CONTEXT).
    """
    for meta in SESSIONS.values():
        if meta["phases"] and meta["phases"][0] == phase:
            return True
    return False


def is_last_phase_of_session(phase: CoachingPhase) -> bool:
    """
    True iff `phase` is the last phase listed in its session.

    The outro-video / break trigger boundary. Returns False for phases not
    in any session (e.g., SYSTEM_CONTEXT).
    """
    for meta in SESSIONS.values():
        if meta["phases"] and meta["phases"][-1] == phase:
            return True
    return False
