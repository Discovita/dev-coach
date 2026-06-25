"""
create_meditation_for_user — build a pending meditation and its empty segments.

A segment is created for every identity that has BOTH a saved image and an
i_am_statement, ordered by identity order. Each segment is seeded with the
current editable video prompt (from the VIDEO_GENERATION prompt template) and
audio script (the identity's I Am statement). No parts are generated here.
"""

from apps.identities.models import Identity
from apps.meditations.models import Meditation, MeditationSegment
from apps.users.models import User
from services.logger import configure_logging
from services.prompt_manager.manager import PromptManager

log = configure_logging(__name__, log_level="INFO")


def get_eligible_identities(user: User):
    """Identities with both a saved image and an i_am_statement, in order."""
    return list(
        Identity.objects.filter(user=user)
        .exclude(image="")
        .exclude(image__isnull=True)
        .exclude(i_am_statement__isnull=True)
        .exclude(i_am_statement="")
        .order_by("order", "created_at")
    )


def create_meditation_for_user(user: User) -> Meditation:
    """
    Create a pending Meditation for *user* with one empty segment per eligible
    identity. Returns the created Meditation.
    """
    identities = get_eligible_identities(user)
    log.info(
        f"Creating meditation for {user.email} with {len(identities)} eligible identities"
    )

    meditation = Meditation.objects.create(user=user)
    prompt_manager = PromptManager()

    for index, identity in enumerate(identities):
        MeditationSegment.objects.create(
            meditation=meditation,
            identity=identity,
            order=index,
            current_video_prompt=prompt_manager.create_video_generation_prompt(
                identity
            ),
            current_audio_script=identity.i_am_statement or "",
        )

    return meditation
