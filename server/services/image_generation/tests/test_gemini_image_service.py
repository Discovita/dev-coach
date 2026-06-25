"""
Tests for GeminiImageService error classification and transient-retry behavior.

Covers the fix for intermittent Gemini ``404 NOT_FOUND`` ("Requested entity was
not found") failures: transient errors are retried with backoff, and whatever
reaches the user is always a short, human-readable message (never raw provider
JSON).
"""

from unittest.mock import MagicMock, patch

from PIL import Image

from django.test import TestCase

from services.image_generation.gemini_image_service import (
    GeminiImageService,
    ImageGenerationError,
    _call_with_retries,
    is_transient_error,
)


class FakeClientError(Exception):
    """Stand-in for google.genai ClientError with a ``.code`` attribute."""

    def __init__(self, code: int, message: str):
        self.code = code
        super().__init__(message)


# The raw 404 the preview image model intermittently returns.
RAW_404 = (
    "404 NOT_FOUND. {'error': {'code': 404, "
    "'message': 'Requested entity was not found.', 'status': 'NOT_FOUND'}}"
)


class IsTransientErrorTests(TestCase):
    def test_404_is_transient(self):
        self.assertTrue(is_transient_error(FakeClientError(404, RAW_404)))

    def test_5xx_is_transient(self):
        for code in (500, 502, 503, 504):
            self.assertTrue(is_transient_error(FakeClientError(code, f"{code} ERR")))

    def test_connection_and_ssl_are_transient(self):
        self.assertTrue(is_transient_error(Exception("Connection reset by peer")))
        self.assertTrue(
            is_transient_error(Exception("SSL connection has been closed unexpectedly"))
        )

    def test_rate_limit_is_not_transient(self):
        self.assertFalse(is_transient_error(FakeClientError(429, "429 RESOURCE")))

    def test_safety_is_not_transient(self):
        self.assertFalse(is_transient_error(Exception("blocked by safety filters")))


class FromExceptionTests(TestCase):
    def test_404_maps_to_overloaded_and_hides_raw(self):
        err = ImageGenerationError.from_exception(FakeClientError(404, RAW_404))
        self.assertEqual(err.error_code, ImageGenerationError.MODEL_OVERLOADED)
        self.assertIn("overloaded", err.message.lower())
        # The raw provider error must never leak into the user-facing message.
        self.assertNotIn("404", err.message)
        self.assertNotIn("NOT_FOUND", err.message)
        # ...but it is preserved in details for logging/debugging.
        self.assertEqual(err.details, RAW_404)

    def test_429_maps_to_rate_limited(self):
        err = ImageGenerationError.from_exception(FakeClientError(429, "429 RESOURCE"))
        self.assertEqual(err.error_code, ImageGenerationError.RATE_LIMITED)

    def test_safety_maps_to_safety_block(self):
        err = ImageGenerationError.from_exception(Exception("blocked by safety"))
        self.assertEqual(err.error_code, ImageGenerationError.SAFETY_BLOCK)

    def test_unknown_is_generic_and_hides_raw(self):
        raw = "weird boom 0xdeadbeef"
        err = ImageGenerationError.from_exception(Exception(raw))
        self.assertEqual(err.error_code, ImageGenerationError.UNKNOWN)
        self.assertNotIn("0xdeadbeef", err.message)
        self.assertEqual(err.details, raw)


class CallWithRetriesTests(TestCase):
    @patch("services.image_generation.gemini_image_service.time.sleep")
    def test_retries_transient_then_succeeds(self, _sleep):
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise FakeClientError(503, "503 UNAVAILABLE")
            return "ok"

        self.assertEqual(_call_with_retries(flaky, "x"), "ok")
        self.assertEqual(calls["n"], 3)

    @patch("services.image_generation.gemini_image_service.time.sleep")
    def test_gives_up_after_max_attempts(self, _sleep):
        calls = {"n": 0}

        def always():
            calls["n"] += 1
            raise FakeClientError(404, RAW_404)

        with self.assertRaises(FakeClientError):
            _call_with_retries(always, "x")
        self.assertEqual(calls["n"], 3)  # MAX_GENERATION_ATTEMPTS

    @patch("services.image_generation.gemini_image_service.time.sleep")
    def test_does_not_retry_non_transient(self, _sleep):
        calls = {"n": 0}

        def safety():
            calls["n"] += 1
            raise Exception("blocked by safety")

        with self.assertRaises(Exception):
            _call_with_retries(safety, "x")
        self.assertEqual(calls["n"], 1)


class SendChatMessageRetryTests(TestCase):
    def _image_response(self):
        resp = MagicMock()
        part = MagicMock()
        part.thought = False
        part.text = None
        part.inline_data = MagicMock()
        part.as_image.return_value = Image.new("RGB", (8, 8), "red")
        resp.parts = [part]
        return resp

    @patch("services.image_generation.gemini_image_service.time.sleep")
    @patch("services.image_generation.gemini_image_service.genai.Client")
    def test_send_chat_message_recovers_after_transient_404(self, _client, _sleep):
        service = GeminiImageService(api_key="test")
        chat = MagicMock()
        chat.send_message.side_effect = [
            FakeClientError(404, RAW_404),
            FakeClientError(404, RAW_404),
            self._image_response(),
        ]

        image, _resp = service.send_chat_message(chat, "make it warmer")

        self.assertIsNotNone(image)
        self.assertEqual(chat.send_message.call_count, 3)

    @patch("services.image_generation.gemini_image_service.time.sleep")
    @patch("services.image_generation.gemini_image_service.genai.Client")
    def test_persistent_404_raises_friendly_overloaded(self, _client, _sleep):
        service = GeminiImageService(api_key="test")
        chat = MagicMock()
        chat.send_message.side_effect = FakeClientError(404, RAW_404)

        with self.assertRaises(ImageGenerationError) as cm:
            service.send_chat_message(chat, "make it warmer")

        self.assertEqual(cm.exception.error_code, ImageGenerationError.MODEL_OVERLOADED)
        self.assertNotIn("404", cm.exception.message)
        self.assertEqual(chat.send_message.call_count, 3)
