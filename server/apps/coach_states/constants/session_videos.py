"""
Static registry of session videos.

Each entry maps a `video_key` (matching the intro/outro keys in the SESSIONS
map next to the CoachingPhase enum) to display data — `name` (human-readable
label) and `url` (where the player streams from; populated in PR 20).

The set of videos is small and fixed. Promotion to a DB model is intentional
future work only if non-developers need to edit the registry — see the
Procedures memory tagged `dev-coach` for the rationale.

Adding a video later means three edits:
1. Upload the file to S3.
2. Edit the relevant session in `SESSIONS` (in `enums/coaching_phase.py`).
3. Edit / add the entry here in `SESSION_VIDEOS`.
"""

from typing import TypedDict


class SessionVideo(TypedDict):
    name: str
    url: str


SESSION_VIDEOS: dict[str, SessionVideo] = {
    # welcome_session — intro only
    "welcome_session_intro": {
        "name": "Welcome",
        "url": "",
    },
    # get_to_know_session
    "get_to_know_session_intro": {
        "name": "Get to Know You Intro",
        "url": "",
    },
    "get_to_know_session_outro": {
        "name": "Get to Know You Outro",
        "url": "",
    },
    # brainstorming_session
    "brainstorming_session_intro": {
        "name": "Brainstorming Intro",
        "url": "",
    },
    "brainstorming_session_outro": {
        "name": "Brainstorming Outro",
        "url": "",
    },
    # refinement_session
    "refinement_session_intro": {
        "name": "Refinement Intro",
        "url": "",
    },
    "refinement_session_outro": {
        "name": "Refinement Outro",
        "url": "",
    },
    # commitment_session
    "commitment_session_intro": {
        "name": "Commitment Intro",
        "url": "",
    },
    "commitment_session_outro": {
        "name": "Commitment Outro",
        "url": "",
    },
    # i_am_session
    "i_am_session_intro": {
        "name": "I Am Statement Intro",
        "url": "",
    },
    "i_am_session_outro": {
        "name": "I Am Statement Outro",
        "url": "",
    },
    # visualization_session — intro only
    "visualization_session_intro": {
        "name": "Visualization",
        "url": "",
    },
}


def get_video(video_key: str) -> SessionVideo:
    """
    Return the registry entry for `video_key`.

    Raises KeyError if the key is not in the registry — callers (action
    handlers, frontend card builders) should validate ahead of time.
    """
    return SESSION_VIDEOS[video_key]
