"""
ImageChatResponse Serializer

Documents the response shape for image chat endpoints.
"""

from rest_framework import serializers


class ImageChatResponseSerializer(serializers.Serializer):
    """
    Response format for start-image-chat and continue-image-chat endpoints.
    """

    image_base64 = serializers.CharField(
        help_text="Base64 encoded PNG image"
    )

    identity_id = serializers.UUIDField(
        help_text="UUID of the identity the image was generated for"
    )

    identity_name = serializers.CharField(
        help_text="Name of the identity"
    )
