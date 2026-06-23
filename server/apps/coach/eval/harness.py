"""
Shared building blocks for the automated coach eval harness.

Keeps the reusable orchestration pieces — persona loading, the simulated
user-bot, and component-aware driving of the coach — in one place so the eval
management commands all share them.

The harness drives the REAL coach pipeline via `process_message`, so it exercises
whatever prompts are currently active in the database.
"""

from pathlib import Path
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.coach_states.serializers.coach_state_serializer import CoachStateSerializer
from enums.ai import AIModel
from enums.component_type import ComponentType
from enums.message_role import MessageRole
from services.ai.utils.openai import structured_completion

# Component types that genuinely GATE the conversation — the client must click a
# button (which carries a real action) to proceed. Other components (e.g.
# intro_canned_response) are optional reply shortcuts, not gates, so the user-bot
# should just type a normal message instead of replaying their button actions.
GATE_COMPONENT_TYPES = {
    ComponentType.SESSION_VIDEO.value,
    ComponentType.SESSION_BREAK.value,
}

# Persona markdown files live alongside this module.
PERSONA_DIR = Path(__file__).resolve().parent / "personas"

# Models for the harness itself (NOT the coach under test). The user-bot is
# cheap; the judge is the stronger model. The coach uses its configured default.
DEFAULT_USER_BOT_MODEL = AIModel.GPT_5_4_MINI
DEFAULT_JUDGE_MODEL = AIModel.GPT_4O

# A conversational transcript: (role, text) pairs where role is "coach" or "user".
Transcript = List[Tuple[str, str]]


class PersonaSpec(BaseModel):
    """A loaded persona: metadata + the markdown body used to prompt the user-bot."""

    persona_id: str
    name: str
    system_prompt: str


class UserBotReply(BaseModel):
    """The simulated client's next chat message."""

    reply: str = Field(description="The client's next chat message, first person, concise.")


def load_persona(persona_id: str) -> PersonaSpec:
    """Load a persona markdown file by id (filename stem) from PERSONA_DIR.

    Strips leading YAML frontmatter; the markdown body becomes the user-bot's
    system prompt. The frontmatter `name:` is used for display.
    """
    path = PERSONA_DIR / f"{persona_id}.md"
    if not path.exists():
        available = sorted(p.stem for p in PERSONA_DIR.glob("*.md"))
        raise FileNotFoundError(
            f"Persona '{persona_id}' not found at {path}. Available: {available}"
        )
    text = path.read_text(encoding="utf-8")
    name = persona_id
    body = text
    if text.lstrip().startswith("---"):
        stripped = text.lstrip()
        end = stripped.find("\n---", 3)
        if end != -1:
            frontmatter = stripped[3:end]
            body = stripped[end + 4 :].lstrip("\n")
            for line in frontmatter.splitlines():
                if line.strip().lower().startswith("name:"):
                    name = line.split(":", 1)[1].strip()
                    break
    return PersonaSpec(persona_id=persona_id, name=name, system_prompt=body.strip())


def render_transcript(transcript: Transcript, you_label: str = "YOU") -> str:
    """Render a transcript as plain text for prompting the user-bot or judge."""
    lines = []
    for role, text in transcript:
        who = "COACH" if role == "coach" else you_label
        lines.append(f"{who}: {text}")
    return "\n".join(lines)


def user_bot_reply(client, model: AIModel, persona: PersonaSpec, transcript: Transcript) -> str:
    """Generate the simulated client's next message, in persona, given the
    conversation so far."""
    convo = render_transcript(transcript) or (
        "(The conversation is just beginning. Send a natural opening message.)"
    )
    system = (
        f"{persona.system_prompt}\n\n"
        f"--- Conversation so far ---\n{convo}\n\n"
        "Write your next chat message as the client."
    )
    completion = structured_completion(
        client=client,
        messages=[{"role": "system", "content": system}],
        model=model,
        response_format=UserBotReply,
        temperature=0.8,
    )
    return completion.choices[0].message.parsed.reply.strip()


# --- component-aware driving --------------------------------------------------
#
# Several coaching phases gate the conversation behind UI components the client
# must click through: the welcome video, per-session intro/outro videos, and
# breaks. The harness drives these generically by replaying the component's
# primary-button actions (e.g. `acknowledge_session_video`, `end_break`) verbatim
# as `request_component_actions` — no per-component hardcoding required.


def _is_actionable_component(cfg) -> bool:
    return (
        bool(cfg)
        and cfg.get("component_type") in GATE_COMPONENT_TYPES
        and bool(cfg.get("buttons"))
        and not cfg.get("closed")
    )


def pending_component(user) -> Optional[dict]:
    """Return the latest coach message's component_config if it is a gating
    component (session video / break) the client must click through, else None.
    Non-gating components like canned-response shortcuts return None so the
    user-bot replies with normal text."""
    msg = (
        ChatMessage.objects.filter(user=user, role=MessageRole.COACH)
        .order_by("-timestamp")
        .first()
    )
    cfg = getattr(msg, "component_config", None) if msg else None
    return cfg if _is_actionable_component(cfg) else None


def primary_button_actions(cfg: dict) -> list:
    """The actions on a component's first button — replayed verbatim to click
    through the gate (acknowledge a video, end a break)."""
    buttons = cfg.get("buttons") or []
    if not buttons:
        return []
    return buttons[0].get("actions") or []


# --- observability: coach state + action log ----------------------------------
#
# To see what the coach is actually *doing* (not just what it says), the harness
# snapshots the CoachState after every turn (the same fields the admin Coach State
# viewer shows) and pulls the Action rows the coach wrote that turn.

# Fields mirrored from CoachStateSerializer (current_identity is reduced to a name).
COACH_STATE_FIELDS = (
    "current_phase",
    "identity_focus",
    "skipped_identity_categories",
    "who_you_are",
    "who_you_want_to_be",
    "asked_questions",
    "shown_videos",
    "on_break",
)


def coach_state_snapshot(coach_state) -> dict:
    """A compact, JSON-serializable snapshot of the coach state — the same fields
    the admin Coach State viewer shows, with current_identity reduced to its name."""
    data = CoachStateSerializer(coach_state).data
    snap = {f: data.get(f) for f in COACH_STATE_FIELDS}
    current_identity = data.get("current_identity")
    snap["current_identity"] = (
        current_identity.get("name") if isinstance(current_identity, dict) else None
    )
    return snap


def collect_new_actions(user, seen_ids: set) -> list:
    """Return the Action rows for this user not already in seen_ids (i.e. the
    actions the coach took on the latest turn), recording their ids into seen_ids.

    Each item: {action, params, summary} — action_type, the JSON params, and the
    handler's natural-language result_summary."""
    rows = list(
        Action.objects.filter(user=user)
        .exclude(id__in=seen_ids)
        .order_by("timestamp")
    )
    out = []
    for a in rows:
        seen_ids.add(a.id)
        out.append(
            {"action": a.action_type, "params": a.parameters, "summary": a.result_summary}
        )
    return out
