"""
Tests for the SESSIONS map + helpers in `enums/coaching_phase.py`.

Pure data + functions — no Django ORM access, no DB hits, no fixtures.
"""

import pytest

from enums.coaching_phase import (
    SESSIONS,
    CoachingPhase,
    is_first_phase_of_session,
    is_last_phase_of_session,
    session_of,
)

# Every CoachingPhase value EXCEPT SYSTEM_CONTEXT should appear in SESSIONS.
# SYSTEM_CONTEXT is a meta-phase, not a real coaching phase.
_REAL_PHASES = [p for p in CoachingPhase if p != CoachingPhase.SYSTEM_CONTEXT]


# ---------------------------------------------------------------------------
# SESSIONS map structure
# ---------------------------------------------------------------------------


class TestSessionsMapCoverage:
    """Every real CoachingPhase appears in exactly one session."""

    def test_sessions_map_covers_every_coaching_phase_exactly_once(self):
        seen: list[CoachingPhase] = []
        for meta in SESSIONS.values():
            seen.extend(meta["phases"])
        assert sorted(seen, key=lambda p: p.value) == sorted(
            _REAL_PHASES, key=lambda p: p.value
        )
        # No duplicates across sessions
        assert len(seen) == len(set(seen)), "A phase appears in more than one session"

    def test_sessions_map_excludes_system_context(self):
        for meta in SESSIONS.values():
            assert CoachingPhase.SYSTEM_CONTEXT not in meta["phases"]


# ---------------------------------------------------------------------------
# session_of
# ---------------------------------------------------------------------------


# Build (phase, expected_session_key) pairs from the SESSIONS map so the
# parametrization stays in sync with whatever the map says.
_PHASE_TO_SESSION = [
    (phase, session_key)
    for session_key, meta in SESSIONS.items()
    for phase in meta["phases"]
]


class TestSessionOf:
    @pytest.mark.parametrize("phase,expected_session", _PHASE_TO_SESSION)
    def test_session_of_returns_correct_session(self, phase, expected_session):
        assert session_of(phase) == expected_session

    def test_session_of_raises_for_unknown_phase(self):
        # SYSTEM_CONTEXT is a valid CoachingPhase but is intentionally not in
        # any session — session_of should raise.
        with pytest.raises(ValueError):
            session_of(CoachingPhase.SYSTEM_CONTEXT)


# ---------------------------------------------------------------------------
# is_first_phase_of_session
# ---------------------------------------------------------------------------


_FIRST_PHASES = [meta["phases"][0] for meta in SESSIONS.values()]
_NON_FIRST_PHASES = [
    phase
    for meta in SESSIONS.values()
    for phase in meta["phases"][1:]
]


class TestIsFirstPhaseOfSession:
    @pytest.mark.parametrize("phase", _FIRST_PHASES)
    def test_is_first_phase_of_session_true_for_first_phase(self, phase):
        assert is_first_phase_of_session(phase) is True

    @pytest.mark.parametrize("phase", _NON_FIRST_PHASES)
    def test_is_first_phase_of_session_false_for_non_first_phases(self, phase):
        assert is_first_phase_of_session(phase) is False

    def test_is_first_phase_of_session_false_for_system_context(self):
        assert is_first_phase_of_session(CoachingPhase.SYSTEM_CONTEXT) is False


# ---------------------------------------------------------------------------
# is_last_phase_of_session
# ---------------------------------------------------------------------------


_LAST_PHASES = [meta["phases"][-1] for meta in SESSIONS.values()]
_NON_LAST_PHASES = [
    phase
    for meta in SESSIONS.values()
    for phase in meta["phases"][:-1]
]


class TestIsLastPhaseOfSession:
    @pytest.mark.parametrize("phase", _LAST_PHASES)
    def test_is_last_phase_of_session_true_for_last_phase(self, phase):
        assert is_last_phase_of_session(phase) is True

    @pytest.mark.parametrize("phase", _NON_LAST_PHASES)
    def test_is_last_phase_of_session_false_for_non_last_phases(self, phase):
        assert is_last_phase_of_session(phase) is False

    def test_is_last_phase_of_session_false_for_system_context(self):
        assert is_last_phase_of_session(CoachingPhase.SYSTEM_CONTEXT) is False


# ---------------------------------------------------------------------------
# Asymmetric sessions sanity (intro-only by design)
# ---------------------------------------------------------------------------


class TestAsymmetricSessions:
    def test_welcome_session_outro_is_none(self):
        assert SESSIONS["welcome_session"]["outro"] is None

    def test_visualization_session_outro_is_none(self):
        assert SESSIONS["visualization_session"]["outro"] is None


# ---------------------------------------------------------------------------
# Naming convention guard
# ---------------------------------------------------------------------------


class TestSessionKeyNaming:
    def test_session_keys_all_end_with_underscore_session_suffix(self):
        for session_key in SESSIONS.keys():
            assert session_key.endswith("_session"), (
                f"Session key {session_key!r} must end with '_session'"
            )

    def test_intro_keys_match_session_key_prefix(self):
        for session_key, meta in SESSIONS.items():
            if meta["intro"] is not None:
                assert meta["intro"] == f"{session_key}_intro"

    def test_outro_keys_match_session_key_prefix(self):
        for session_key, meta in SESSIONS.items():
            if meta["outro"] is not None:
                assert meta["outro"] == f"{session_key}_outro"
