"""
Static registry of session videos.

Each entry maps a `video_key` (matching the intro/outro keys in the SESSIONS
map next to the CoachingPhase enum) to display data — `name` (human-readable
label) and `s3_key` (bucket-relative path; resolved against the current
env's S3 bucket by `get_video_url`).

The set of videos is small and fixed. Promotion to a DB model is intentional
future work only if non-developers need to edit the registry — see the
Procedures memory tagged `dev-coach` for the rationale.

Adding a video later means three edits:
1. Upload the file to S3 (via `scripts/upload_session_videos.py`).
2. Edit the relevant session in `SESSIONS` (in `enums/coaching_phase.py`).
3. Edit / add the entry here in `SESSION_VIDEOS`.

URL shape note (PR 20): we store the bucket-relative `s3_key` and resolve
the full URL at request time via `get_video_url(video_key)` so the same
registry serves the staging and production buckets without per-env duplication.
"""

from typing import TypedDict

from django.conf import settings


class SessionVideo(TypedDict):
    name: str
    s3_key: str


SESSION_VIDEOS: dict[str, SessionVideo] = {
    # welcome_session — intro only
    "welcome_session_intro": {
        "name": "Welcome",
        "s3_key": "session-videos/01-welcome-session-intro.mov",
    },
    # get_to_know_session
    "get_to_know_session_intro": {
        "name": "Get to Know You Intro",
        "s3_key": "session-videos/02-get-to-know-session-intro.mov",
    },
    "get_to_know_session_outro": {
        "name": "Get to Know You Outro",
        "s3_key": "session-videos/03-get-to-know-session-outro.mov",
    },
    # brainstorming_session
    "brainstorming_session_intro": {
        "name": "Brainstorming Intro",
        "s3_key": "session-videos/04-brainstorming-session-intro.mov",
    },
    "brainstorming_session_outro": {
        "name": "Brainstorming Outro",
        "s3_key": "session-videos/05-brainstorming-session-outro.mov",
    },
    # refinement_session
    "refinement_session_intro": {
        "name": "Refinement Intro",
        "s3_key": "session-videos/06-refinement-session-intro.mov",
    },
    "refinement_session_outro": {
        "name": "Refinement Outro",
        "s3_key": "session-videos/07-refinement-session-outro.mov",
    },
    # commitment_session
    "commitment_session_intro": {
        "name": "Commitment Intro",
        "s3_key": "session-videos/08-commitment-session-intro.mov",
    },
    "commitment_session_outro": {
        "name": "Commitment Outro",
        "s3_key": "session-videos/09-commitment-session-outro.mov",
    },
    # i_am_session
    "i_am_session_intro": {
        "name": "I Am Statement Intro",
        "s3_key": "session-videos/10-i-am-session-intro.mov",
    },
    "i_am_session_outro": {
        "name": "I Am Statement Outro",
        "s3_key": "session-videos/11-i-am-session-outro.mov",
    },
    # visualization_session — intro only
    "visualization_session_intro": {
        "name": "Visualization",
        "s3_key": "session-videos/12-visualization-session-intro.mov",
    },
}


def get_video(video_key: str) -> SessionVideo:
    """
    Return the registry entry for `video_key`.

    Raises KeyError if the key is not in the registry — callers (action
    handlers, frontend card builders) should validate ahead of time.
    """
    return SESSION_VIDEOS[video_key]


def get_video_url(video_key: str) -> str:
    """
    Resolve the full S3 URL for a session video against the current env's bucket.

    Joins `settings.AWS_STORAGE_BUCKET_NAME` (set per-env in
    `settings/{local,staging,production,previews}.py`) with the registry's
    `s3_key` and the standard S3 virtual-hosted-style domain. The same
    registry serves every environment.

    Raises KeyError if the key is missing from the registry.
    """
    entry = SESSION_VIDEOS[video_key]
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    return f"https://{bucket}.s3.amazonaws.com/{entry['s3_key']}"
