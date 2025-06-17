from .utils import get_all_user_notes, get_previous_coach_message
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

class Sentinel:
    """
    Service for extracting and updating user notes based on chat messages.
    """

    def __init__(self, user):
        self.user = user

    def extract_notes(self, user_msg):
        prev_coach_msg = get_previous_coach_message(self.user, user_msg)
        notes = get_all_user_notes(self.user)
        # Call your LLM here (stub for now)
        # llm_response = call_llm(user_msg, prev_coach_msg, notes)
        log.info(
            f"LLM would see: user_msg={user_msg.content}, prev_coach_msg={prev_coach_msg.content if prev_coach_msg else None}, notes={[n.note for n in notes]}"
        )
        # Parse and update notes (stub for now)
        # ...
