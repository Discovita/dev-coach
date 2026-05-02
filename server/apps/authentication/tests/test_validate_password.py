"""
Unit tests for validate_password utility.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.authentication.utils.password_validator import validate_password


class ValidatePasswordTests(TestCase):
    """Tests for the validate_password utility function."""

    def test_valid_password_passes(self):
        """Password meeting all requirements should not raise."""
        validate_password("StrongPass1!")

    def test_too_short_raises(self):
        """Password under 8 characters should raise ValidationError."""
        with self.assertRaises(ValidationError) as ctx:
            validate_password("Ab1!")
        self.assertIn("8 characters", str(ctx.exception))

    def test_exactly_min_length_passes(self):
        """Password of exactly 8 characters meeting all rules should pass."""
        validate_password("Abcde1f!")

    def test_missing_uppercase_raises(self):
        """Password without uppercase letter should raise ValidationError."""
        with self.assertRaises(ValidationError) as ctx:
            validate_password("alllower1!")
        self.assertIn("uppercase", str(ctx.exception))

    def test_missing_digit_raises(self):
        """Password without a digit should raise ValidationError."""
        with self.assertRaises(ValidationError) as ctx:
            validate_password("NoDigits!!")
        self.assertIn("number", str(ctx.exception))

    def test_missing_special_char_raises(self):
        """Password without a special character should raise ValidationError."""
        with self.assertRaises(ValidationError) as ctx:
            validate_password("NoSpecial1")
        self.assertIn("special", str(ctx.exception))

    def test_checks_are_ordered_length_first(self):
        """A 3-char password should fail on length, not missing chars."""
        with self.assertRaises(ValidationError) as ctx:
            validate_password("ab")
        self.assertIn("8 characters", str(ctx.exception))
