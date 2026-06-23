"""
Tests for the pure delta + version-resolution logic in run_coach_eval_diff.
"""

from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from apps.coach.eval.harness import CheckResult
from apps.coach.management.commands import run_coach_eval_diff
from apps.coach.management.commands.run_coach_eval_diff import Command


def _verdict(checks):
    """A stand-in JudgeVerdict carrying just the targeted_checks the delta uses."""
    return SimpleNamespace(
        targeted_checks=[CheckResult(check=c, passed=p, note="") for c, p in checks]
    )


class TestCheckDeltas(SimpleTestCase):
    """_check_deltas pairs targeted checks by text and classifies each change."""

    def setUp(self):
        self.cmd = Command()

    def test_classifies_fixed_regressed_same(self):
        baseline = _verdict([("one q", True), ("no facts", False), ("builds", True)])
        candidate = _verdict([("one q", True), ("no facts", True), ("builds", False)])
        deltas = {d["check"]: d for d in self.cmd._check_deltas(baseline, candidate)}
        self.assertEqual(deltas["one q"]["change"], "same")
        self.assertEqual(deltas["no facts"]["change"], "fixed")
        self.assertEqual(deltas["builds"]["change"], "regressed")

    def test_check_only_in_candidate_is_new(self):
        baseline = _verdict([("a", True)])
        candidate = _verdict([("a", True), ("b", True)])
        deltas = {d["check"]: d for d in self.cmd._check_deltas(baseline, candidate)}
        self.assertEqual(deltas["b"]["change"], "new")
        self.assertIsNone(deltas["b"]["baseline"])

    def test_iterates_candidate_checks(self):
        """The delta is driven by the candidate's checks (what we're judging now)."""
        baseline = _verdict([("a", True), ("dropped", True)])
        candidate = _verdict([("a", False)])
        rows = self.cmd._check_deltas(baseline, candidate)
        self.assertEqual([r["check"] for r in rows], ["a"])
        self.assertEqual(rows[0]["change"], "regressed")


class TestResolveVersions(SimpleTestCase):
    """Candidate defaults to latest; baseline to the version right before it."""

    def setUp(self):
        self.cmd = Command()

    def _resolve(self, active, baseline, candidate):
        with patch.object(
            run_coach_eval_diff, "active_prompt_versions", return_value=active
        ):
            return self.cmd._resolve_versions("get_to_know_you", baseline, candidate)

    def test_defaults_to_previous_vs_latest(self):
        self.assertEqual(self._resolve([6, 5, 4], None, None), (5, 6))

    def test_explicit_baseline_keeps_latest_candidate(self):
        self.assertEqual(self._resolve([6, 5, 4], 4, None), (4, 6))

    def test_explicit_candidate_takes_version_below_it(self):
        self.assertEqual(self._resolve([6, 5, 4], None, 5), (4, 5))

    def test_both_explicit(self):
        self.assertEqual(self._resolve([6, 5, 4], 4, 6), (4, 6))

    def test_single_version_has_no_baseline(self):
        self.assertIsNone(self._resolve([6], None, None))

    def test_missing_candidate_version_errors(self):
        self.assertIsNone(self._resolve([6, 5], None, 9))

    def test_missing_baseline_version_errors(self):
        self.assertIsNone(self._resolve([6, 5], 3, 6))

    def test_no_active_prompts_errors(self):
        self.assertIsNone(self._resolve([], None, None))
