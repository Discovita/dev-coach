"""
Tests for apps/coach/eval/harness.py (the pure helpers).
"""

from unittest.mock import patch

from django.test import SimpleTestCase

from apps.coach.eval import harness
from apps.coach.eval.harness import load_targeted_checks


class TestLoadTargetedChecks(SimpleTestCase):
    """load_targeted_checks parses the per-phase file and merges --check extras."""

    def test_loads_checks_from_phase_file(self):
        """The shipped get_to_know_you file yields its non-comment lines."""
        checks = load_targeted_checks("get_to_know_you")
        self.assertTrue(checks, "expected the get_to_know_you checks file to load")
        # Comments and blank lines are skipped; bullets are stripped.
        self.assertTrue(all(c and not c.startswith("#") for c in checks))
        self.assertTrue(all(not c.startswith("- ") for c in checks))
        self.assertIn(
            "The coach never asks more than one question in a single message.",
            checks,
        )

    def test_unknown_phase_returns_only_extras(self):
        """A phase with no file falls back to just the command-line extras."""
        checks = load_targeted_checks("no_such_phase", extra=["one-off check"])
        self.assertEqual(checks, ["one-off check"])

    def test_unknown_phase_with_no_extras_is_empty(self):
        self.assertEqual(load_targeted_checks("no_such_phase"), [])

    def test_extras_are_appended_and_stripped(self):
        """--check extras append after file checks; blank/whitespace ones drop."""
        base = load_targeted_checks("get_to_know_you")
        merged = load_targeted_checks(
            "get_to_know_you", extra=["  extra one  ", "", "   "]
        )
        self.assertEqual(merged, base + ["extra one"])

    def test_parses_bullets_blanks_and_comments(self):
        """Bullet, comment, and blank-line handling on synthetic file contents."""
        sample = "# header\n\n- first check\n* second check\nthird check\n\n# tail\n"
        with patch.object(harness.Path, "exists", return_value=True), patch.object(
            harness.Path, "read_text", return_value=sample
        ):
            checks = load_targeted_checks("anything")
        self.assertEqual(checks, ["first check", "second check", "third check"])
