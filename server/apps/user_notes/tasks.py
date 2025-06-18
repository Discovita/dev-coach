from celery import shared_task
from apps.chat_messages.models import ChatMessage
from services.sentinel.sentinel import Sentinel
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


@shared_task
def extract_user_notes(chat_message_id):
    user_msg = ChatMessage.objects.get(id=chat_message_id)
    sentinel = Sentinel(user_msg.user)
    sentinel.extract_notes()
