"""
Tests for chat history serialization utilities.
"""

from django.test import TestCase
from unittest.mock import MagicMock

from services.image_generation.utils.chat_history_serializer import (
    serialize_chat_history,
    deserialize_chat_history,
)


class ChatHistorySerializerTests(TestCase):
    """Tests for chat history serialization utilities."""

    def test_serialize_chat_history(self):
        """Test that Content objects are serialized to JSON dicts."""
        # Create mock Content objects
        mock_content1 = MagicMock()
        mock_content1.to_json_dict.return_value = {
            "role": "user",
            "parts": [{"text": "Generate an image"}]
        }
        
        mock_content2 = MagicMock()
        mock_content2.to_json_dict.return_value = {
            "role": "model",
            "parts": [
                {"text": "I'll generate that"},
                {"inline_data": {"mime_type": "image/png", "data": "base64data"}}
            ]
        }
        
        history = [mock_content1, mock_content2]
        result = serialize_chat_history(history)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["role"], "user")
        self.assertEqual(result[1]["role"], "model")
        # Verify to_json_dict was called
        mock_content1.to_json_dict.assert_called_once()
        mock_content2.to_json_dict.assert_called_once()

    def test_deserialize_chat_history(self):
        """Test that JSON dicts are deserialized back to Content objects."""
        from google.genai.types import Content
        import base64
        
        # Create valid base64 data
        test_image_bytes = b"fake image data"
        base64_data = base64.b64encode(test_image_bytes).decode('utf-8')
        
        history_data = [
            {
                "role": "user",
                "parts": [{"text": "Generate an image"}]
            },
            {
                "role": "model",
                "parts": [
                    {"text": "I'll generate that"},
                    {"inline_data": {"mime_type": "image/png", "data": base64_data}}
                ]
            }
        ]
        
        result = deserialize_chat_history(history_data)
        
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Content)
        self.assertIsInstance(result[1], Content)
        self.assertEqual(result[0].role, "user")
        self.assertEqual(result[1].role, "model")

    def test_serialization_round_trip(self):
        """Test that serialize → deserialize preserves data."""
        from google.genai.types import Content
        import base64
        
        # Create valid base64 data
        test_image_bytes = b"fake image data"
        base64_data = base64.b64encode(test_image_bytes).decode('utf-8')
        
        # Create actual Content objects
        content1 = Content.model_validate({
            "role": "user",
            "parts": [{"text": "Generate an image"}]
        })
        content2 = Content.model_validate({
            "role": "model",
            "parts": [
                {"text": "I'll generate that"},
                {"inline_data": {"mime_type": "image/png", "data": base64_data}}
            ]
        })
        
        original_history = [content1, content2]
        
        # Serialize
        serialized = serialize_chat_history(original_history)
        
        # Deserialize
        deserialized = deserialize_chat_history(serialized)
        
        # Verify round trip
        self.assertEqual(len(deserialized), len(original_history))
        self.assertEqual(deserialized[0].role, original_history[0].role)
        self.assertEqual(deserialized[1].role, original_history[1].role)
        # Verify parts are preserved
        self.assertEqual(len(deserialized[0].parts), len(original_history[0].parts))
        self.assertEqual(len(deserialized[1].parts), len(original_history[1].parts))

    def test_serialize_empty_history(self):
        """Test serializing empty history."""
        result = serialize_chat_history([])
        self.assertEqual(result, [])

    def test_deserialize_empty_history(self):
        """Test deserializing empty history."""
        result = deserialize_chat_history([])
        self.assertEqual(result, [])

    def test_serialize_dict_history(self):
        """Test that dicts are passed through without modification."""
        # When get_history() returns dicts (e.g., from mocks or already serialized)
        dict_history = [
            {"role": "user", "parts": [{"text": "test"}]},
            {"role": "model", "parts": [{"text": "response"}]}
        ]
        
        result = serialize_chat_history(dict_history)
        
        # Should return the dicts as-is
        self.assertEqual(result, dict_history)
        self.assertEqual(len(result), 2)
