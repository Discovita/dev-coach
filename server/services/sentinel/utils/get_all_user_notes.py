from apps.user_notes.models import UserNote
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def get_all_user_notes(user: User) -> list[UserNote]:
    """
    For a given user, retrieve all associated UserNotes
    """
    user_notes = list(UserNote.objects.filter(user=user).order_by("created_at"))
    return user_notes
