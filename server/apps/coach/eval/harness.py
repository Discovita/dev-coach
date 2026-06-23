"""
Shared building blocks for the automated coach eval harness.

Keeps the reusable orchestration pieces — persona loading, the simulated
user-bot, and component-aware driving of the coach — in one place so the eval
management commands all share them.

The harness drives the REAL coach pipeline via `process_message`, so it exercises
whatever prompts are currently active in the database.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from django.contrib.auth import get_user_model
from pydantic import BaseModel, Field

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.coach.functions.public.process_message import process_message
from apps.coach_states.models import CoachState
from apps.coach_states.serializers.coach_state_serializer import CoachStateSerializer
from apps.prompts.models import Prompt
from apps.test_scenario.functions.admin.instantiate_test_scenario import (
    instantiate_test_scenario,
)
from apps.test_scenario.models import TestScenario
from enums.ai import AIModel
from enums.component_type import ComponentType
from enums.message_role import MessageRole
from enums.prompt_type import PromptType
from services.ai.utils.openai import structured_completion

User = get_user_model()

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

# Per-phase targeted-check files (one assertion per line) live here.
CHECKS_DIR = Path(__file__).resolve().parent / "checks"

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


def chat_history_transcript(user) -> Transcript:
    """Build a (role, text) transcript from a user's stored chat history.

    Maps coach/user ChatMessage rows in chronological order; skips blank-text
    cards (e.g. the welcome video card, whose text is ""). Used to give the
    user-bot conversational continuity — and the judge prior context — when an
    eval is seeded from a frozen scenario's real history rather than a cold start.
    """
    rows = ChatMessage.objects.filter(
        user=user, role__in=(MessageRole.USER, MessageRole.COACH)
    ).order_by("timestamp")
    out: Transcript = []
    for m in rows:
        text = (m.content or "").strip()
        if not text:
            continue
        out.append(("coach" if m.role == MessageRole.COACH else "user", text))
    return out


def load_phase_prompt_body(
    phase: str, version: Optional[int] = None
) -> Tuple[str, Optional[int]]:
    """Return (body, version) of the coach Prompt for `phase` — the SAME row the
    coach pipeline uses (see PromptManager.create_chat_prompt).

    With `version`, pin that exact version; otherwise the latest active. This raw
    body — the phase's coaching instructions, placeholders intact — IS the live
    rubric: the judge checks whether the coach followed it, so the rubric tracks
    the prompt automatically and never needs separate maintenance. The appended
    action/JSON mechanics, global system context, and recent messages are NOT part
    of `body` and are intentionally excluded from the rubric. Returns ("", None)
    if no matching prompt exists.
    """
    qs = Prompt.objects.filter(
        prompt_type=PromptType.COACH, coaching_phase=phase, is_active=True
    )
    if version is not None:
        qs = qs.filter(version=version)
    prompt = qs.order_by("-version").first()
    if not prompt:
        return "", None
    return prompt.body, prompt.version


def load_targeted_checks(
    phase: str, extra: Optional[List[str]] = None
) -> List[str]:
    """Load the per-phase targeted checks plus any `extra` (command-line) checks.

    Targeted checks are explicit, hand-authored pass/fail assertions ("phase X
    must do Y / must never do Z") — deliberately separate from the prompt-derived
    rubric. The per-phase file lives at apps/coach/eval/checks/<phase>.md: one
    check per line; blank lines and lines starting with '#' are ignored, and a
    single leading '-'/'*' bullet is stripped.
    """
    checks: List[str] = []
    path = CHECKS_DIR / f"{phase}.md"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s[0] in "-*":
                s = s[1:].strip()
            if s:
                checks.append(s)
    if extra:
        checks.extend(c.strip() for c in extra if c and c.strip())
    return checks


def save_eval_run(path: str, data: dict) -> None:
    """Persist an eval run artifact (the report plus its `user_turns`) as JSON.

    The artifact doubles as the replay source: `load_eval_run` reads it back and
    the eval re-runs the recorded user turns (see run_coach_eval_spike --replay),
    so the only thing that changes is the prompt/model under test.
    """
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_eval_run(path: str) -> dict:
    """Load an eval run artifact written by `save_eval_run`."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


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


# --- seeding ------------------------------------------------------------------
#
# Two ways to put a throwaway user into the state an eval starts from: a cold
# user freshly created at a phase, or a full hydration of a frozen TestScenario
# (real prior history). Both are idempotent and shared by the eval commands.


def seed_cold_user(email: str, phase: str) -> "User":
    """Create a fresh throwaway user at `phase` (deleting any prior one)."""
    User.objects.filter(email=email).delete()  # idempotent
    user = User.objects.create_user(email=email, password="Coach123!")
    coach_state = CoachState.objects.get(user=user)  # auto-created by signal
    coach_state.current_phase = phase
    coach_state.save(update_fields=["current_phase"])
    return user


def seed_scenario_user(name: str) -> Tuple["User", str, str]:
    """Hydrate a frozen TestScenario and return (user, email, start_phase).

    Full hydration (chat history, identities, coach state, notes, actions,
    breaks) so the eval resumes from real prior history. The start phase is
    whatever the scenario's coach state was frozen at. Raises
    TestScenario.DoesNotExist if no scenario has that exact name.
    """
    scenario = TestScenario.objects.get(name=name)
    result = instantiate_test_scenario(
        scenario,
        create_user=True,
        create_chat_messages=True,
        create_identities=True,
        create_coach_state=True,
        create_user_notes=True,
        create_actions=True,
        create_breaks=True,
    )
    user = result["user"]
    start_phase = CoachState.objects.get(user=user).current_phase
    return user, result["email"], start_phase


# --- driving one conversation -------------------------------------------------


@dataclass
class DriveResult:
    """The outcome of driving one eval conversation."""

    transcript: Transcript
    user_turns: List[str]
    actions: list
    final_coach_state: dict
    final_phase: str
    run_error: Optional[str] = None


def drive_eval(
    user,
    *,
    coach_model: AIModel,
    prompt_versions: Optional[dict],
    start_phase: str,
    max_turns: int,
    harness_client=None,
    persona: Optional[PersonaSpec] = None,
    prior: Optional[Transcript] = None,
    replay_turns: Optional[List[str]] = None,
    emit: Optional[Callable[[str, str], None]] = None,
) -> DriveResult:
    """Drive ONE eval conversation against the real coach pipeline.

    Supply either a `persona` (the user-bot generates each turn) or
    `replay_turns` (recorded turns replayed verbatim). Component gates
    (video/break) are clicked through dynamically and don't consume a turn. The
    loop stops on phase transition, on pipeline error, when the turn budget is
    hit, or when replay turns run out.

    `emit(kind, text)` receives live progress events for the caller to render —
    kinds: "gate", "client", "coach", "action", "info", "error". Defaults to a
    no-op. Returns a DriveResult; a pipeline failure is reported via
    `run_error` (not raised) so the caller can treat it as an error outcome
    rather than a coaching-quality result.
    """
    emit = emit or (lambda kind, text: None)
    prior = prior or []
    transcript: Transcript = []
    replay_idx = 0
    # Prior-history actions exist on a hydrated user; record their ids so only
    # actions taken DURING this run are reported.
    seen_action_ids = set(
        Action.objects.filter(user=user).values_list("id", flat=True)
    )
    actions: list = []
    run_error = None

    for _ in range(max_turns):
        comp = pending_component(user)
        if comp:
            acts = primary_button_actions(comp)
            emit("gate", f"{comp.get('component_type')} -> {[a.get('action') for a in acts]}")
            ok, data, err = process_message(
                user, None, acts, coach_model, prompt_versions
            )
        else:
            if replay_turns is not None:
                if replay_idx >= len(replay_turns):
                    emit("info", f"replay exhausted after {replay_idx} user turns")
                    break
                user_msg = replay_turns[replay_idx]
                replay_idx += 1
            else:
                user_msg = user_bot_reply(
                    harness_client, DEFAULT_USER_BOT_MODEL, persona, prior + transcript
                )
            transcript.append(("user", user_msg))
            emit("client", user_msg)
            ok, data, err = process_message(
                user, user_msg, None, coach_model, prompt_versions
            )

        if not ok:
            run_error = err
            emit("error", err)
            break

        coach_msg = data.get("message", "")
        if coach_msg:
            transcript.append(("coach", coach_msg))
            emit("coach", coach_msg)

        coach_state = CoachState.objects.get(user=user)
        new_actions = collect_new_actions(user, seen_action_ids)
        actions.extend(new_actions)
        if new_actions:
            emit("action", ", ".join(a["action"] for a in new_actions))

        if coach_state.current_phase != start_phase:
            emit("info", f"phase transitioned to: {coach_state.current_phase}")
            break

    final_coach_state = coach_state_snapshot(CoachState.objects.get(user=user))
    return DriveResult(
        transcript=transcript,
        user_turns=[t[1] for t in transcript if t[0] == "user"],
        actions=actions,
        final_coach_state=final_coach_state,
        final_phase=final_coach_state["current_phase"],
        run_error=run_error,
    )


# --- judging ------------------------------------------------------------------
#
# The rubric is DERIVED LIVE from the phase's own coach Prompt.body (the same
# version the coach ran): the judge is asked "did the coach follow these
# instructions?" and derives the criteria from the body itself, so it tracks the
# prompt automatically and needs no maintenance. Targeted checks layer explicit,
# hand-authored pass/fail assertions on top.

JUDGE_FRAMING = (
    "You are a strict but fair judge evaluating a COACH in an identity coaching "
    "conversation. Judge ONLY the coach's messages (role=coach).\n\n"
    "The standard is the coach's OWN phase instructions, shown below. Decide "
    "whether the coach actually FOLLOWED them in the transcript. Focus on "
    "behavioral and conversational adherence — IGNORE output formatting, JSON, "
    "and action/tool mechanics (those are enforced elsewhere and are not your "
    "concern). Placeholders like {curly_braces} in the instructions are filled "
    "with live data at runtime; judge the intent behind them, not the literal "
    "placeholder.\n\n"
    "Derive the key behavioral expectations from the instructions yourself, score "
    "the coach on each as a criterion, and give an overall pass/fail + 1-5 score."
)


class CriterionScore(BaseModel):
    name: str
    passed: bool
    note: str


class CheckResult(BaseModel):
    """Verdict on one explicit, hand-authored targeted check."""

    check: str = Field(description="The targeted check being evaluated (echoed).")
    passed: bool
    note: str


class JudgeVerdict(BaseModel):
    """LLM-as-judge verdict over the full transcript."""

    passed: bool = Field(description="Overall pass/fail for the coach.")
    score: int = Field(description="Overall quality score 1-5.")
    criteria: List[CriterionScore] = Field(
        description="Criteria derived from the phase instructions, each scored."
    )
    targeted_checks: List[CheckResult] = Field(
        description="One result per supplied targeted check; empty if none given."
    )
    reasoning: str


def judge_transcript(
    client,
    *,
    phase: str,
    rubric_body: str,
    transcript: Transcript,
    targeted_checks: Optional[List[str]] = None,
    context: Optional[Transcript] = None,
    judge_model: AIModel = DEFAULT_JUDGE_MODEL,
) -> JudgeVerdict:
    """Judge a transcript against the phase's derived rubric + targeted checks."""
    convo = render_transcript(transcript, you_label="CLIENT")
    context_block = ""
    if context:
        ctx = render_transcript(context, you_label="CLIENT")
        context_block = (
            "PRIOR CONVERSATION (context only — do NOT score these messages; "
            "they predate the phase under evaluation. Use them only to know "
            f"what the client already shared):\n\n{ctx}\n\n"
        )
    checks_block = ""
    if targeted_checks:
        numbered = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(targeted_checks))
        checks_block = (
            "TARGETED CHECKS — in addition to the rubric, evaluate each of these "
            "explicit requirements as a hard yes/no and return a verdict + note "
            "for each in `targeted_checks` (echo the check text "
            f"verbatim):\n{numbered}\n\n"
        )
    system = (
        f"{JUDGE_FRAMING}\n\n"
        f"--- BEGIN {phase} PHASE INSTRUCTIONS ---\n{rubric_body}\n"
        f"--- END {phase} PHASE INSTRUCTIONS ---\n\n"
        f"{checks_block}{context_block}"
        f"Transcript to evaluate:\n\n{convo}\n\n"
        "Return your structured verdict."
    )
    completion = structured_completion(
        client=client,
        messages=[{"role": "system", "content": system}],
        model=judge_model,
        response_format=JudgeVerdict,
        temperature=0.0,
    )
    return completion.choices[0].message.parsed
