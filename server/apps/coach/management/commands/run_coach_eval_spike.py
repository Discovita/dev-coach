"""
run_coach_eval_spike

Phase-0 spike for the automated prompt-testing harness.

Proves the full loop end-to-end against the REAL coach pipeline (real prompt
assembly from the DB + real coach LLM):

    seed user at a phase
        -> user-bot (LLM persona) drives the conversation
        -> coach responds via process_message (the same code path the API uses)
        -> judge (deterministic checks + LLM rubric) returns a verdict

The persona is loaded from a markdown file (see apps/coach/eval/personas/), and
the loop is component-aware — it clicks through any video/break gates by
replaying their button actions. Shared pieces live in apps/coach/eval/harness.py.

Runs against the LIVE local database so it exercises whatever prompts are
currently active (i.e. the ones you just edited). It creates a throwaway
`@testscenario.com` user and deletes it on exit unless --keep is passed.

Usage:
    python manage.py run_coach_eval_spike
    python manage.py run_coach_eval_spike --persona casey --max-turns 10 --keep
    python manage.py run_coach_eval_spike --coach-model gpt-4o --prompt-version 10
"""

import json
from typing import List

from django.core.management.base import BaseCommand
from pydantic import BaseModel, Field

from apps.coach.eval.harness import (
    DEFAULT_JUDGE_MODEL,
    DEFAULT_USER_BOT_MODEL,
    Transcript,
    coach_state_snapshot,
    collect_new_actions,
    load_persona,
    pending_component,
    primary_button_actions,
    render_transcript,
    user_bot_reply,
)
from apps.coach.functions.public.process_message import process_message
from apps.coach_states.models import CoachState
from django.contrib.auth import get_user_model
from enums.ai import AIModel
from enums.coaching_phase import CoachingPhase
from services.ai.ai_service_factory import AIServiceFactory
from services.ai.utils.openai import structured_completion

User = get_user_model()

SPIKE_EMAIL = "coach-eval-spike@testscenario.com"

# --- The single spike scenario -------------------------------------------------
START_PHASE = CoachingPhase.GET_TO_KNOW_YOU
# Goal: the get_to_know_you phase should end by transitioning the user onward.
GOAL_PHASES = {
    CoachingPhase.IDENTITY_WARMUP.value,
    CoachingPhase.IDENTITY_BRAINSTORMING.value,
}

RUBRIC = (
    "You are evaluating the COACH's performance in a 'get to know you' phase of "
    "an identity coaching conversation. Judge ONLY the coach's messages "
    "(role=coach). Criteria:\n"
    "1. Warmth & rapport: the coach is warm, encouraging, and conversational.\n"
    "2. One thing at a time: the coach does not interrogate with multiple "
    "stacked questions in a single message.\n"
    "3. Curiosity & follow-up: the coach builds on what the client said rather "
    "than asking generic, disconnected questions.\n"
    "4. Stays on task: the coach is genuinely getting to know the client (their "
    "life, values, aspirations) and does not derail or hallucinate facts the "
    "client never said.\n"
    "5. Forward motion: by the end the coach is moving the client toward the "
    "next step rather than looping endlessly.\n"
    "Pass only if the coach is clearly competent across these. Be a strict but "
    "fair judge."
)


class CriterionScore(BaseModel):
    name: str
    passed: bool
    note: str


class JudgeVerdict(BaseModel):
    """LLM-as-judge verdict over the full transcript."""

    passed: bool = Field(description="Overall pass/fail for the coach.")
    score: int = Field(description="Overall quality score 1-5.")
    criteria: List[CriterionScore]
    reasoning: str


class Command(BaseCommand):
    help = "Phase-0 spike: drive a simulated conversation with the coach and judge it."

    def add_arguments(self, parser):
        parser.add_argument("--max-turns", type=int, default=20)
        parser.add_argument(
            "--persona",
            type=str,
            default="casey",
            help="Persona id (filename stem in apps/coach/eval/personas/).",
        )
        parser.add_argument(
            "--coach-model",
            type=str,
            default=None,
            help="Override coach model. Defaults to the configured DEFAULT_AI_MODEL.",
        )
        parser.add_argument(
            "--prompt-version",
            type=int,
            default=None,
            help=(
                f"Pin the {START_PHASE.value} prompt to a specific version "
                "(for before/after comparisons). Defaults to the latest active."
            ),
        )
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Keep the throwaway test user instead of deleting it on exit.",
        )

    # --- seed -----------------------------------------------------------------
    def _seed_user(self) -> User:
        User.objects.filter(email=SPIKE_EMAIL).delete()  # idempotent
        user = User.objects.create_user(email=SPIKE_EMAIL, password="Coach123!")
        coach_state = CoachState.objects.get(user=user)  # auto-created by signal
        coach_state.current_phase = START_PHASE.value
        coach_state.save(update_fields=["current_phase"])
        return user

    # --- judge ----------------------------------------------------------------
    def _judge(self, client, transcript: Transcript) -> JudgeVerdict:
        convo = render_transcript(transcript, you_label="CLIENT")
        system = (
            f"{RUBRIC}\n\nHere is the full transcript:\n\n{convo}\n\n"
            "Return your structured verdict."
        )
        completion = structured_completion(
            client=client,
            messages=[{"role": "system", "content": system}],
            model=DEFAULT_JUDGE_MODEL,
            response_format=JudgeVerdict,
            temperature=0.0,
        )
        return completion.choices[0].message.parsed

    # --- orchestration --------------------------------------------------------
    def handle(self, *args, **options):
        max_turns = options["max_turns"]
        coach_model = AIModel.get_or_default(options["coach_model"])
        persona = load_persona(options["persona"])
        harness_client = AIServiceFactory.create(DEFAULT_USER_BOT_MODEL).client

        # Phase-scoped version pin: only applies while the user is in START_PHASE.
        prompt_version = options["prompt_version"]
        prompt_versions = (
            {START_PHASE.value: prompt_version} if prompt_version is not None else None
        )
        version_label = prompt_version if prompt_version is not None else "latest"

        self.stdout.write(self.style.HTTP_INFO(
            f"Persona: {persona.name} | coach: {coach_model.value} "
            f"| {START_PHASE.value} prompt: v{version_label} "
            f"| user-bot: {DEFAULT_USER_BOT_MODEL.value} | judge: {DEFAULT_JUDGE_MODEL.value}"
        ))

        user = self._seed_user()
        transcript: Transcript = []
        seen_action_ids: set = set()
        all_actions: list = []
        transition_reached = False
        run_error = None

        try:
            for _ in range(max_turns):
                # Click through any gating component (video/break) before talking.
                comp = pending_component(user)
                if comp:
                    actions = primary_button_actions(comp)
                    self.stdout.write(self.style.HTTP_INFO(
                        f"[click-through: {comp.get('component_type')} "
                        f"-> {[a.get('action') for a in actions]}]"
                    ))
                    ok, data, err = process_message(
                        user, None, actions, coach_model, prompt_versions
                    )
                else:
                    user_msg = user_bot_reply(
                        harness_client, DEFAULT_USER_BOT_MODEL, persona, transcript
                    )
                    transcript.append(("user", user_msg))
                    self.stdout.write(self.style.WARNING(f"\nCLIENT: {user_msg}"))
                    ok, data, err = process_message(
                        user, user_msg, None, coach_model, prompt_versions
                    )

                if not ok:
                    run_error = err
                    self.stderr.write(self.style.ERROR(f"process_message failed: {err}"))
                    break

                coach_msg = data.get("message", "")
                if coach_msg:
                    transcript.append(("coach", coach_msg))
                    self.stdout.write(self.style.SUCCESS(f"COACH: {coach_msg}"))

                # Observability: what did the coach actually DO this turn?
                coach_state = CoachState.objects.get(user=user)
                acts = collect_new_actions(user, seen_action_ids)
                all_actions.extend(acts)
                if acts:
                    self.stdout.write(self.style.HTTP_INFO(
                        "  ↳ actions: " + ", ".join(a["action"] for a in acts)
                    ))

                if coach_state.current_phase != START_PHASE.value:
                    transition_reached = coach_state.current_phase in GOAL_PHASES
                    self.stdout.write(self.style.HTTP_INFO(
                        f"\n[phase transitioned to: {coach_state.current_phase}]"
                    ))
                    break

            final_coach_state = coach_state_snapshot(CoachState.objects.get(user=user))
            final_phase = final_coach_state["current_phase"]

            base_report = {
                "scenario": "get_to_know_you_spike",
                "persona": persona.persona_id,
                "coach_model": coach_model.value,
                "prompt_version": version_label,
                "turns": len([t for t in transcript if t[0] == "user"]),
            }

            def _emit(report: dict) -> None:
                self.stdout.write("\n" + "=" * 70)
                self.stdout.write(self.style.MIGRATE_HEADING("EVAL REPORT"))
                self.stdout.write(json.dumps(report, indent=2))
                self.stdout.write("=" * 70)

            # A pipeline failure (e.g. the coach returning malformed JSON) is an
            # ERROR, not a coaching-quality result. Skip the judge so an infra
            # hiccup never gets laundered into a fake low score.
            if run_error is not None:
                _emit({
                    **base_report,
                    "status": "error",
                    "error": run_error,
                    "actions": all_actions,
                    "final_coach_state": final_coach_state,
                })
                self.stdout.write(self.style.ERROR(
                    "RESULT: ERROR — pipeline failure; judge skipped"
                ))
                return

            verdict = self._judge(harness_client, transcript)

            # Quality (LLM rubric) and progression (phase movement) are reported
            # SEPARATELY and never AND-ed together. A high-quality conversation
            # that simply didn't transition within the turn budget is NOT a
            # failure — it's a non-transition, which is its own signal.
            _emit({
                **base_report,
                "status": "ok",
                "quality": {
                    "passed": verdict.passed,
                    "score": verdict.score,
                    "criteria": [c.model_dump() for c in verdict.criteria],
                    "reasoning": verdict.reasoning,
                },
                "progression": {
                    "start_phase": START_PHASE.value,
                    "final_phase": final_phase,
                    "transitioned": final_phase != START_PHASE.value,
                    "reached_goal_phase": transition_reached,
                },
                "actions": all_actions,
                "final_coach_state": final_coach_state,
            })

            # Two independent outcomes — quality is the judge's call; progression
            # is informational (phase movement within the turn budget).
            q_style = self.style.SUCCESS if verdict.passed else self.style.ERROR
            self.stdout.write(q_style(
                f"QUALITY:     {'PASS' if verdict.passed else 'FAIL'}  "
                f"(judge score {verdict.score}/5)"
            ))
            if final_phase != START_PHASE.value:
                prog = f"{START_PHASE.value} -> {final_phase}"
            else:
                prog = f"did not transition (still {final_phase})"
            self.stdout.write(self.style.HTTP_INFO(f"PROGRESSION: {prog}"))
        finally:
            if not options["keep"]:
                User.objects.filter(email=SPIKE_EMAIL).delete()
                self.stdout.write("\n(cleaned up throwaway user)")
            else:
                self.stdout.write(f"\n(kept throwaway user: {SPIKE_EMAIL})")
