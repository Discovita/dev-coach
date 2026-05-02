"""
Utility functions for the test_scenario app.

Exports:
    # Template validation utilities
    validate_scenario_template: Validates a scenario template against the template serializers.

    # Template assembly utilities
    build_scenario_template: Assembles a full template dict from a user's DB state.
    build_user_template_section: Builds the user section dict for a scenario template.

    # Template gather utilities
    gather_coach_state_section: Gathers CoachState into a template section dict.
    gather_identities_section: Gathers Identities into a template section list.
    gather_chat_messages_section: Gathers ChatMessages into a template section list and mapping.
    gather_user_notes_section: Gathers UserNotes into a template section list.
    gather_actions_section: Gathers Actions into a template section list.

    # Scenario creation utilities
    create_scenario_user: Creates a fresh test user from a template.
    create_scenario_identities: Creates Identity objects from a template.
    create_scenario_coach_state: Applies CoachState data from a template.
    create_scenario_chat_messages: Creates ChatMessage objects from a template.
    create_scenario_user_notes: Creates UserNote objects from a template.
    create_scenario_actions: Creates Action objects from a template.
    resolve_scenario_coach_message: Resolves the coach message to link to an action.

    # Image key utilities
    extract_s3_key_from_url: Extracts the S3 object key from a full URL.
    build_image_dest_key: Builds a UUID-based destination S3 key for an image.

    # Image transfer utilities
    duplicate_s3_image: Copies an existing S3 image to a new UUID-based key.
    copy_image_from_url: Copies an image from a URL (S3 or external) to S3.
    copy_image_within_s3: Server-side S3 copy within the same bucket.
    download_and_upload_image: Downloads an external image and uploads via storage.

    # Image deletion utilities
    delete_identity_image: Deletes the S3 image for a single identity entry.
    delete_removed_identity_images: Deletes images removed between template versions.

    # Image processing utilities
    process_identity_images: Handles image upload/deletion for identity images.
"""

# Template validation utilities
from apps.test_scenario.utils.validate_scenario_template import (
    validate_scenario_template,
)

# Template assembly utilities
from apps.test_scenario.utils.build_scenario_template import build_scenario_template
from apps.test_scenario.utils.build_user_template_section import (
    build_user_template_section,
)

# Template gather utilities
from apps.test_scenario.utils.gather_actions_section import gather_actions_section
from apps.test_scenario.utils.gather_chat_messages_section import (
    gather_chat_messages_section,
)
from apps.test_scenario.utils.gather_coach_state_section import (
    gather_coach_state_section,
)
from apps.test_scenario.utils.gather_identities_section import gather_identities_section
from apps.test_scenario.utils.gather_user_notes_section import gather_user_notes_section

# Scenario creation utilities
from apps.test_scenario.utils.create_scenario_actions import create_scenario_actions
from apps.test_scenario.utils.create_scenario_chat_messages import (
    create_scenario_chat_messages,
)
from apps.test_scenario.utils.create_scenario_coach_state import (
    create_scenario_coach_state,
)
from apps.test_scenario.utils.create_scenario_identities import (
    create_scenario_identities,
)
from apps.test_scenario.utils.create_scenario_user import create_scenario_user
from apps.test_scenario.utils.create_scenario_user_notes import (
    create_scenario_user_notes,
)
from apps.test_scenario.utils.resolve_scenario_coach_message import (
    resolve_scenario_coach_message,
)

# Image key utilities
from apps.test_scenario.utils.build_image_dest_key import build_image_dest_key
from apps.test_scenario.utils.extract_s3_key import extract_s3_key_from_url

# Image transfer utilities
from apps.test_scenario.utils.copy_image_from_url import copy_image_from_url
from apps.test_scenario.utils.copy_image_within_s3 import copy_image_within_s3
from apps.test_scenario.utils.download_and_upload_image import download_and_upload_image
from apps.test_scenario.utils.duplicate_s3_image import duplicate_s3_image

# Image deletion utilities
from apps.test_scenario.utils.delete_identity_image import delete_identity_image
from apps.test_scenario.utils.delete_removed_identity_images import (
    delete_removed_identity_images,
)

# Image processing utilities
from apps.test_scenario.utils.process_identity_images import process_identity_images

__all__ = [
    # Template validation utilities
    "validate_scenario_template",
    # Template assembly utilities
    "build_scenario_template",
    "build_user_template_section",
    # Template gather utilities
    "gather_coach_state_section",
    "gather_identities_section",
    "gather_chat_messages_section",
    "gather_user_notes_section",
    "gather_actions_section",
    # Scenario creation utilities
    "create_scenario_user",
    "create_scenario_identities",
    "create_scenario_coach_state",
    "create_scenario_chat_messages",
    "create_scenario_user_notes",
    "create_scenario_actions",
    "resolve_scenario_coach_message",
    # Image key utilities
    "extract_s3_key_from_url",
    "build_image_dest_key",
    # Image transfer utilities
    "duplicate_s3_image",
    "copy_image_from_url",
    "copy_image_within_s3",
    "download_and_upload_image",
    # Image deletion utilities
    "delete_identity_image",
    "delete_removed_identity_images",
    # Image processing utilities
    "process_identity_images",
]
