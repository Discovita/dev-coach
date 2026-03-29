from typing import Any, Dict, List, Optional, Tuple

from apps.users.models import User
from enums.ai import AIModel

from .functions import process_message as process_message_func


class CoachService:
    """
    Service facade for coach-related operations.

    This service handles the business logic for processing coach messages,
    separating it from the HTTP request/response handling in viewsets.
    """

    @staticmethod
    def process_message(
        user: User,
        message: str,
        request_component_actions: Optional[List],
        model: AIModel,
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Process a message for a user and generate a coach response.

        Args:
            user: The User object to process the message for
            message: The user's message to the coach
            request_component_actions: Optional list of component actions to apply
            model: The AI model to use for generation

        Returns:
            Tuple of (success: bool, response_data: Dict, error_message: str)
        """
        return process_message_func(user, message, request_component_actions, model)
