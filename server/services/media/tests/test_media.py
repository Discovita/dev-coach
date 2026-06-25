"""
Tests for the media generation layer (services/media/).

Covers the provider enums, the standard error type, the Veo video provider and
Gemini TTS provider (with the google-genai client mocked), and the factory.
No network calls are made.
"""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from enums.media import AudioProvider, VideoProvider
from services.media.base import MediaGenerationError, MediaResult
from services.media.factory import MediaProviderFactory
from services.media.gemini_tts_provider import GeminiTTSProvider
from services.media.veo_video_provider import VeoVideoProvider

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestProviderEnums(SimpleTestCase):
    def test_video_provider_from_string(self):
        self.assertEqual(VideoProvider.from_string("veo"), VideoProvider.GOOGLE_VEO)
        self.assertEqual(
            VideoProvider.from_string("GOOGLE_VEO"), VideoProvider.GOOGLE_VEO
        )

    def test_video_provider_from_string_unknown(self):
        with self.assertRaises(ValueError):
            VideoProvider.from_string("runway")

    def test_audio_provider_from_string(self):
        self.assertEqual(AudioProvider.from_string("gemini"), AudioProvider.GEMINI_TTS)
        self.assertEqual(AudioProvider.from_string("TTS"), AudioProvider.GEMINI_TTS)

    def test_audio_provider_from_string_unknown(self):
        with self.assertRaises(ValueError):
            AudioProvider.from_string("elevenlabs")


# ---------------------------------------------------------------------------
# MediaGenerationError
# ---------------------------------------------------------------------------


class TestMediaGenerationError(SimpleTestCase):
    def test_from_exception_rate_limited(self):
        err = MediaGenerationError.from_exception(Exception("429 quota exceeded"))
        self.assertEqual(err.error_code, MediaGenerationError.RATE_LIMITED)

    def test_from_exception_overloaded(self):
        err = MediaGenerationError.from_exception(Exception("503 UNAVAILABLE"))
        self.assertEqual(err.error_code, MediaGenerationError.MODEL_OVERLOADED)

    def test_from_exception_safety(self):
        err = MediaGenerationError.from_exception(
            Exception("request blocked by safety")
        )
        self.assertEqual(err.error_code, MediaGenerationError.SAFETY_BLOCK)

    def test_from_exception_unknown(self):
        err = MediaGenerationError.from_exception(Exception("something odd"))
        self.assertEqual(err.error_code, MediaGenerationError.UNKNOWN)

    def test_from_exception_passthrough(self):
        original = MediaGenerationError("boom", MediaGenerationError.TIMEOUT)
        self.assertIs(MediaGenerationError.from_exception(original), original)


# ---------------------------------------------------------------------------
# VeoVideoProvider
# ---------------------------------------------------------------------------


def _make_veo_provider(**kwargs):
    provider = VeoVideoProvider(api_key="test-key", **kwargs)
    provider.client = MagicMock()
    return provider


def _mock_done_operation(video_bytes=b"VIDEOBYTES", mime_type="video/mp4"):
    video = MagicMock()
    video.video_bytes = video_bytes
    video.mime_type = mime_type
    generated = MagicMock()
    generated.video = video
    op = MagicMock()
    op.done = True
    op.error = None
    op.response.generated_videos = [generated]
    return op


class TestVeoVideoProvider(SimpleTestCase):
    def test_provider_name(self):
        self.assertEqual(_make_veo_provider().provider_name(), VideoProvider.GOOGLE_VEO)

    def test_generate_success(self):
        provider = _make_veo_provider()
        provider.client.models.generate_videos.return_value = _mock_done_operation()

        result = provider.generate(prompt="serene portrait", first_frame=b"img")

        self.assertIsInstance(result, MediaResult)
        self.assertEqual(result.data, b"VIDEOBYTES")
        self.assertEqual(result.mime_type, "video/mp4")
        self.assertEqual(result.provider, VideoProvider.GOOGLE_VEO.value)
        self.assertEqual(result.width, 1920)
        self.assertEqual(result.height, 1080)
        self.assertEqual(result.duration_seconds, 8.0)
        provider.client.files.download.assert_called_once()

    def test_generate_forces_8s_at_1080p(self):
        provider = _make_veo_provider()
        provider.client.models.generate_videos.return_value = _mock_done_operation()

        provider.generate(
            prompt="p", first_frame=b"img", resolution="1080p", duration_seconds=4
        )

        config = provider.client.models.generate_videos.call_args.kwargs["config"]
        self.assertEqual(config.duration_seconds, 8)

    def test_generate_allows_4s_at_720p(self):
        provider = _make_veo_provider()
        provider.client.models.generate_videos.return_value = _mock_done_operation()

        provider.generate(
            prompt="p", first_frame=b"img", resolution="720p", duration_seconds=4
        )

        config = provider.client.models.generate_videos.call_args.kwargs["config"]
        self.assertEqual(config.duration_seconds, 4)

    def test_generate_timeout(self):
        provider = _make_veo_provider(poll_interval=0, timeout=0)
        op = MagicMock()
        op.done = False
        provider.client.models.generate_videos.return_value = op

        with self.assertRaises(MediaGenerationError) as ctx:
            provider.generate(prompt="p", first_frame=b"img")
        self.assertEqual(ctx.exception.error_code, MediaGenerationError.TIMEOUT)

    def test_generate_operation_error(self):
        provider = _make_veo_provider()
        op = MagicMock()
        op.done = True
        op.error = "safety violation"
        provider.client.models.generate_videos.return_value = op

        with self.assertRaises(MediaGenerationError):
            provider.generate(prompt="p", first_frame=b"img")

    def test_generate_empty_response(self):
        provider = _make_veo_provider()
        op = MagicMock()
        op.done = True
        op.error = None
        op.response.generated_videos = []
        provider.client.models.generate_videos.return_value = op

        with self.assertRaises(MediaGenerationError) as ctx:
            provider.generate(prompt="p", first_frame=b"img")
        self.assertEqual(ctx.exception.error_code, MediaGenerationError.EMPTY_RESPONSE)

    def test_generate_wraps_submit_exception(self):
        provider = _make_veo_provider()
        provider.client.models.generate_videos.side_effect = Exception("429 quota")

        with self.assertRaises(MediaGenerationError) as ctx:
            provider.generate(prompt="p", first_frame=b"img")
        self.assertEqual(ctx.exception.error_code, MediaGenerationError.RATE_LIMITED)


# ---------------------------------------------------------------------------
# GeminiTTSProvider
# ---------------------------------------------------------------------------


def _make_tts_provider(**kwargs):
    provider = GeminiTTSProvider(api_key="test-key", **kwargs)
    provider.client = MagicMock()
    return provider


def _mock_tts_response(pcm=b"\x00\x01" * 12000):
    part = MagicMock()
    part.inline_data.data = pcm
    response = MagicMock()
    response.candidates = [MagicMock()]
    response.candidates[0].content.parts = [part]
    return response


class TestGeminiTTSProvider(SimpleTestCase):
    def test_provider_name(self):
        self.assertEqual(_make_tts_provider().provider_name(), AudioProvider.GEMINI_TTS)

    def test_generate_success_wraps_wav(self):
        provider = _make_tts_provider()
        provider.client.models.generate_content.return_value = _mock_tts_response()

        result = provider.generate(script="I am calm. I am focused.")

        self.assertIsInstance(result, MediaResult)
        self.assertEqual(result.mime_type, "audio/wav")
        self.assertEqual(result.provider, AudioProvider.GEMINI_TTS.value)
        # WAV container magic bytes.
        self.assertTrue(result.data.startswith(b"RIFF"))
        self.assertIn(b"WAVE", result.data[:12])
        self.assertGreater(result.duration_seconds, 0)

    def test_generate_no_audio_raises(self):
        provider = _make_tts_provider()
        response = MagicMock()
        response.candidates = []
        provider.client.models.generate_content.return_value = response

        with self.assertRaises(MediaGenerationError) as ctx:
            provider.generate(script="hello")
        self.assertEqual(ctx.exception.error_code, MediaGenerationError.EMPTY_RESPONSE)

    def test_generate_wraps_api_exception(self):
        provider = _make_tts_provider()
        provider.client.models.generate_content.side_effect = Exception(
            "503 overloaded"
        )

        with self.assertRaises(MediaGenerationError) as ctx:
            provider.generate(script="hello")
        self.assertEqual(
            ctx.exception.error_code, MediaGenerationError.MODEL_OVERLOADED
        )


# ---------------------------------------------------------------------------
# MediaProviderFactory
# ---------------------------------------------------------------------------


class TestMediaProviderFactory(SimpleTestCase):
    def test_create_video_provider_default(self):
        provider = MediaProviderFactory.create_video_provider(api_key="test-key")
        self.assertIsInstance(provider, VeoVideoProvider)

    def test_create_video_provider_by_string(self):
        provider = MediaProviderFactory.create_video_provider("veo", api_key="test-key")
        self.assertIsInstance(provider, VeoVideoProvider)

    def test_create_video_provider_by_enum(self):
        provider = MediaProviderFactory.create_video_provider(
            VideoProvider.GOOGLE_VEO, api_key="test-key"
        )
        self.assertIsInstance(provider, VeoVideoProvider)

    def test_create_audio_provider_default(self):
        provider = MediaProviderFactory.create_audio_provider(api_key="test-key")
        self.assertIsInstance(provider, GeminiTTSProvider)

    def test_create_audio_provider_by_string(self):
        provider = MediaProviderFactory.create_audio_provider(
            "gemini", api_key="test-key"
        )
        self.assertIsInstance(provider, GeminiTTSProvider)
