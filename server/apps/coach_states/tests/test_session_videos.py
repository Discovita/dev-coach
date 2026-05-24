"""
Tests for the SESSION_VIDEOS registry and the `get_video` helper.

The registry is the source of truth for video display data. The set of
keys must stay in sync with the intro/outro keys in the SESSIONS map
(enums/coaching_phase.py).
"""

import pytest

from apps.coach_states.constants import SESSION_VIDEOS, get_video
from enums.coaching_phase import SESSIONS


# ---------------------------------------------------------------------------
# Registry coverage vs SESSIONS map
# ---------------------------------------------------------------------------


class TestSessionVideosCoverage:
    """SESSION_VIDEOS keys must match the intro/outro keys in SESSIONS."""

    def test_session_videos_has_intro_entry_for_every_session(self):
        """Every session with a non-None intro has a matching registry entry."""
        for meta in SESSIONS.values():
            intro = meta["intro"]
            if intro is not None:
                assert intro in SESSION_VIDEOS, (
                    f"Missing SESSION_VIDEOS entry for intro key {intro!r}"
                )

    def test_session_videos_has_outro_entry_only_for_sessions_with_outro(self):
        """Sessions with an outro have a registry entry; sessions without don't."""
        expected_outro_keys = {
            meta["outro"] for meta in SESSIONS.values() if meta["outro"] is not None
        }
        actual_outro_keys = {
            key for key in SESSION_VIDEOS.keys() if key.endswith("_outro")
        }
        assert expected_outro_keys == actual_outro_keys

    def test_session_videos_keys_match_sessions_intro_outro_union(self):
        """Registry has exactly the union of intro + outro keys from SESSIONS."""
        expected = set()
        for meta in SESSIONS.values():
            if meta["intro"] is not None:
                expected.add(meta["intro"])
            if meta["outro"] is not None:
                expected.add(meta["outro"])
        assert set(SESSION_VIDEOS.keys()) == expected

    def test_total_video_count_is_twelve(self):
        """Sanity check on the documented 12-video set."""
        assert len(SESSION_VIDEOS) == 12


# ---------------------------------------------------------------------------
# Registry entry shape
# ---------------------------------------------------------------------------


class TestSessionVideoEntryShape:
    def test_every_entry_has_name_and_url_keys(self):
        for key, entry in SESSION_VIDEOS.items():
            assert "name" in entry, f"{key} is missing 'name'"
            assert "url" in entry, f"{key} is missing 'url'"

    def test_every_entry_name_is_non_empty_string(self):
        for key, entry in SESSION_VIDEOS.items():
            assert isinstance(entry["name"], str)
            assert entry["name"].strip(), f"{key} has empty name"

    def test_urls_are_strings(self):
        """URLs are strings (may be empty until PR 20 populates them)."""
        for key, entry in SESSION_VIDEOS.items():
            assert isinstance(entry["url"], str)


# ---------------------------------------------------------------------------
# get_video helper
# ---------------------------------------------------------------------------


class TestGetVideo:
    def test_get_video_returns_dict_with_name_and_url(self):
        entry = get_video("welcome_session_intro")
        assert "name" in entry
        assert "url" in entry

    def test_get_video_raises_keyerror_on_unknown_key(self):
        with pytest.raises(KeyError):
            get_video("not_a_real_video_key")

    def test_get_video_returns_same_object_as_registry(self):
        """The helper is a direct lookup — no copy, no transform."""
        assert get_video("brainstorming_session_intro") is SESSION_VIDEOS[
            "brainstorming_session_intro"
        ]
