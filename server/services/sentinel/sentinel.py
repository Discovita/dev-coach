from enums.ai import AIModel

from services.ai.ai_service_factory import AIServiceFactory
from services.logger import configure_logging
from services.prompt_manager.manager import PromptManager
from models.SentinelChatResponse import SentinelChatResponse


log = configure_logging(__name__, log_level="DEBUG")


class Sentinel:
    """
    Service for extracting and updating user notes based on chat messages.
    """

    def __init__(self, user):
        self.user = user
        self.prompt_manager = PromptManager()
        self.model = AIModel.GPT_4O_MINI

    def extract_notes(self):
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
        log.critical(response)
