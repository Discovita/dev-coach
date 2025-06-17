from celery import shared_task
from apps.chat_messages.models import ChatMessage
from apps.user_notes.models import UserNote
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


@shared_task
def extract_user_notes(chat_message_id):
    # 1. Get the triggering user message
    user_msg = ChatMessage.objects.get(id=chat_message_id)
    user = user_msg.user

    # 2. Get the previous COACH message (if any)
    prev_coach_msg = (
        ChatMessage.objects
        .filter(user=user, role='COACH', timestamp__lt=user_msg.timestamp)
        .order_by('-timestamp')
        .first()
    )

    # 3. Get all current notes for the user
    notes = list(UserNote.objects.filter(user=user).order_by('created_at'))

    # 4. Call the LLM (stub for now)
    # llm_response = call_llm(user_msg, prev_coach_msg, notes)
    log.info(f"LLM would see: user_msg={user_msg.content}, prev_coach_msg={prev_coach_msg.content if prev_coach_msg else None}, notes={[n.note for n in notes]}")

    # 5. Parse and update notes (stub for now)
    # ... (to be implemented)
