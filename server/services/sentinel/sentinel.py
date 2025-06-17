from enums.ai import AIModel

from services.logger import configure_logging
from services.prompt_manager.manager import PromptManager

log = configure_logging(__name__, log_level="INFO")


class Sentinel:
    """
    Service for extracting and updating user notes based on chat messages.
    """

    def __init__(self, user):
        self.user = user
        self.prompt_manager = PromptManager()
        self.model = AIModel.GPT_4O_MINI

    def extract_notes(self):
        # Use the PromptManager to build the sentinel prompt
        prompt, response_format = self.prompt_manager.create_sentinel_prompt(self.user, self.model)
        log.info(f"Sentinel LLM prompt:\n{prompt}")
        log.info(f"Sentinel response format: {response_format}")
        # Call your LLM here (stub for now)
        # llm_response = call_llm(prompt, response_format)
        # log.info(f"LLM response: {llm_response}")
        # Parse and update notes (stub for now)
        # ...
