from enums.ai import AIModel

from apps.coach_states.models import CoachState
from apps.users.models import User
from apps.chat_messages.models import ChatMessage
from services.ai.ai_service_factory import AIServiceFactory
from services.logger import configure_logging
from services.prompt_manager.manager import PromptManager
from models.SentinelChatResponse import SentinelChatResponse
from services.action_handler.handler import apply_coach_actions

log = configure_logging(__name__, log_level="INFO")


class Sentinel:
    """
    Service for extracting and updating user notes based on chat messages.
    """

    def __init__(self, user: User):
        self.user = user
        self.prompt_manager = PromptManager()
        self.model = AIModel.GPT_4O
        try:
            self.coach_state = CoachState.objects.get(user=user)
        except CoachState.DoesNotExist:
            log.error(f"User Coach State Not Found: {user.id}")

    def extract_notes(self, chat_message: ChatMessage):
        """
        Extract user notes from a chat message using the sentinel AI service.
        
        Args:
            chat_message: The ChatMessage to analyze for user notes
        """
        ai_service = AIServiceFactory.create(self.model)
        # Use the PromptManager to build the sentinel prompt
        sentinel_prompt, response_format = self.prompt_manager.create_sentinel_prompt(
            self.user, self.model
        )
        log.debug(f"Sentinel LLM prompt:\n{sentinel_prompt}")
        log.debug(f"Sentinel response format: {response_format}")
        response: SentinelChatResponse = ai_service.call_sentinel(
            sentinel_prompt, response_format, self.model
        )
        apply_coach_actions(self.coach_state, response, chat_message)
        log.debug(f"Sentinel Response: {response}")
