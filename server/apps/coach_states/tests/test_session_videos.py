"""
Tests for the SESSION_VIDEOS registry and the `get_video` / `get_video_url`
helpers.

The registry is the source of truth for video display data. The set of
keys must stay in sync with the intro/outro keys in the SESSIONS map
(enums/coaching_phase.py). After PR 20, each entry stores an `s3_key`
(bucket-relative path); `get_video_url` joins it with the current env's
S3 bucket at request time so the same registry serves every environment.
"""

import pytest
from django.test import override_settings

from apps.coach_states.constants import SESSION_VIDEOS, get_video
from apps.coach_states.constants.session_videos import get_video_url
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

    def test_total_video_count_is_eleven(self):
        """Sanity check on the video set: 12 originals minus the removed
        get-to-know intro (the coach introduces that phase itself)."""
        assert len(SESSION_VIDEOS) == 11


# ---------------------------------------------------------------------------
# Registry entry shape (PR 20 — `s3_key` replaces `url`)
# ---------------------------------------------------------------------------


class TestSessionVideoEntryShape:
    def test_every_entry_has_name_and_s3_key_keys(self):
        for key, entry in SESSION_VIDEOS.items():
            assert "name" in entry, f"{key} is missing 'name'"
            assert "s3_key" in entry, f"{key} is missing 's3_key'"

    def test_every_entry_name_is_non_empty_string(self):
        for key, entry in SESSION_VIDEOS.items():
            assert isinstance(entry["name"], str)
            assert entry["name"].strip(), f"{key} has empty name"

    def test_every_s3_key_is_under_media_session_videos_prefix(self):
        """All S3 keys live under the `media/session-videos/` prefix.

        The `media/` parent prefix is the existing public-read scope on
        the dev-coach buckets (matches user-image storage). Putting session
        videos there avoids a bucket-policy change.
        """
        for key, entry in SESSION_VIDEOS.items():
            assert isinstance(entry["s3_key"], str)
            assert entry["s3_key"].startswith("media/session-videos/"), (
                f"{key} s3_key does not start with 'media/session-videos/': "
                f"{entry['s3_key']!r}"
            )

    def test_every_s3_key_ends_with_mov(self):
        for key, entry in SESSION_VIDEOS.items():
            assert entry["s3_key"].endswith(".mov"), (
                f"{key} s3_key does not end with .mov: {entry['s3_key']!r}"
            )

    def test_s3_keys_are_unique(self):
        """Two videos should never share the same S3 path."""
        s3_keys = [entry["s3_key"] for entry in SESSION_VIDEOS.values()]
        assert len(s3_keys) == len(set(s3_keys))


# ---------------------------------------------------------------------------
# get_video helper
# ---------------------------------------------------------------------------


class TestGetVideo:
    def test_get_video_returns_dict_with_name_and_s3_key(self):
        entry = get_video("welcome_session_intro")
        assert "name" in entry
        assert "s3_key" in entry

    def test_get_video_raises_keyerror_on_unknown_key(self):
        with pytest.raises(KeyError):
            get_video("not_a_real_video_key")

    def test_get_video_returns_same_object_as_registry(self):
        """The helper is a direct lookup — no copy, no transform."""
        assert get_video("brainstorming_session_intro") is SESSION_VIDEOS[
            "brainstorming_session_intro"
        ]


# ---------------------------------------------------------------------------
# get_video_url helper (PR 20)
# ---------------------------------------------------------------------------


class TestGetVideoUrl:
    @override_settings(AWS_STORAGE_BUCKET_NAME="test-bucket-foo")
    def test_resolves_to_full_https_url_using_current_bucket(self):
        url = get_video_url("welcome_session_intro")
        assert url == (
            "https://test-bucket-foo.s3.amazonaws.com/"
            "media/session-videos/01-welcome-session-intro.mov"
        )

    @override_settings(AWS_STORAGE_BUCKET_NAME="prod-bucket")
    def test_changes_with_bucket_setting(self):
        """Same registry key → different URL when bucket changes."""
        url = get_video_url("brainstorming_session_intro")
        assert url.startswith("https://prod-bucket.s3.amazonaws.com/")
        assert url.endswith("04-brainstorming-session-intro.mov")

    def test_raises_keyerror_for_unknown_video_key(self):
        with pytest.raises(KeyError):
            get_video_url("not_a_real_video_key")

    def test_resolves_every_registry_key(self):
        """Sanity: every registered key produces a non-empty URL."""
        for video_key in SESSION_VIDEOS:
            url = get_video_url(video_key)
            assert url.startswith("https://")
            assert url.endswith(".mov")
