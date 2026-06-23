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
currently active (i.e. the ones you just edited).

By default it creates a throwaway `@testscenario.com` user seeded cold at the
get_to_know_you phase. Pass --from-scenario "<name>" to instead hydrate a frozen
TestScenario (real prior history, built via build_eval_scenario) and pick the
eval up from that scenario's phase. Either way the throwaway user is deleted on
exit unless --keep is passed.

Usage:
    python manage.py run_coach_eval_spike
    python manage.py run_coach_eval_spike --persona casey --max-turns 10 --keep
    python manage.py run_coach_eval_spike --coach-model gpt-4o --prompt-version 10
    python manage.py run_coach_eval_spike --from-scenario "[Auto] Casey @ start of get_to_know_you"
"""

import json
from typing import List, Optional, Tuple

from django.core.management.base import BaseCommand
from pydantic import BaseModel, Field

from apps.actions.models import Action
from apps.coach.eval.harness import (
    DEFAULT_JUDGE_MODEL,
    DEFAULT_USER_BOT_MODEL,
    Transcript,
    chat_history_transcript,
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
from apps.test_scenario.functions.admin.instantiate_test_scenario import (
    instantiate_test_scenario,
)
from apps.test_scenario.models import TestScenario
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
            "--from-scenario",
            type=str,
            default=None,
            metavar="NAME",
            help=(
                "Seed from a frozen TestScenario (by exact name) — real prior "
                "history — and pick the eval up from that scenario's phase, "
                "instead of cold-seeding a fresh user at get_to_know_you. Build "
                "scenarios with build_eval_scenario."
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

    def _seed_from_scenario(self, name: str) -> Tuple[User, str, str]:
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

    # --- judge ----------------------------------------------------------------
    def _judge(
        self,
        client,
        transcript: Transcript,
        context: Optional[Transcript] = None,
    ) -> JudgeVerdict:
        convo = render_transcript(transcript, you_label="CLIENT")
        context_block = ""
        if context:
            ctx = render_transcript(context, you_label="CLIENT")
            context_block = (
                "PRIOR CONVERSATION (context only — do NOT score these messages; "
                "they predate the phase under evaluation. Use them only to know "
                f"what the client already shared):\n\n{ctx}\n\n"
            )
        system = (
            f"{RUBRIC}\n\n{context_block}"
            f"Transcript to evaluate:\n\n{convo}\n\n"
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
        scenario_name = options["from_scenario"]

        # Seed cold (fresh user at get_to_know_you) or from a frozen scenario
        # (real prior history; phase = whatever it was frozen at). `prior` is the
        # scenario's chat history — given to the user-bot for continuity and to
        # the judge as context, but NOT itself scored.
        prior: Transcript = []
        if scenario_name:
            try:
                user, cleanup_email, start_phase = self._seed_from_scenario(scenario_name)
            except TestScenario.DoesNotExist:
                names = list(
                    TestScenario.objects.order_by("name").values_list("name", flat=True)
                )
                self.stderr.write(self.style.ERROR(
                    f"No TestScenario named '{scenario_name}'. Available:\n  "
                    + "\n  ".join(names or ["(none)"])
                ))
                return
            prior = chat_history_transcript(user)
            scenario_label = scenario_name
        else:
            user = self._seed_user()
            cleanup_email = SPIKE_EMAIL
            start_phase = START_PHASE.value
            scenario_label = "get_to_know_you_spike"

        # The rubric is hard-coded for get_to_know_you. Seeding from a different
        # phase still runs, but warn that quality scores aren't phase-matched yet
        # (phase-derived rubrics are the next roadmap item).
        if start_phase != START_PHASE.value:
            self.stdout.write(self.style.WARNING(
                f"NOTE: rubric is get_to_know_you-specific, but this scenario "
                f"starts at '{start_phase}'. Quality scores may not be meaningful; "
                f"progression still is."
            ))

        # Phase-scoped version pin: only applies while the user is in start_phase.
        prompt_version = options["prompt_version"]
        prompt_versions = (
            {start_phase: prompt_version} if prompt_version is not None else None
        )
        version_label = prompt_version if prompt_version is not None else "latest"

        self.stdout.write(self.style.HTTP_INFO(
            f"Persona: {persona.name} | coach: {coach_model.value} "
            f"| start: {start_phase} (v{version_label}) "
            f"| seed: {scenario_label} "
            f"| user-bot: {DEFAULT_USER_BOT_MODEL.value} | judge: {DEFAULT_JUDGE_MODEL.value}"
        ))

        transcript: Transcript = []
        # Prior-history actions exist on the hydrated user; record their ids so
        # collect_new_actions only reports what the coach does DURING this eval.
        seen_action_ids: set = set(
            Action.objects.filter(user=user).values_list("id", flat=True)
        )
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
                        harness_client, DEFAULT_USER_BOT_MODEL, persona, prior + transcript
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

                if coach_state.current_phase != start_phase:
                    transition_reached = coach_state.current_phase in GOAL_PHASES
                    self.stdout.write(self.style.HTTP_INFO(
                        f"\n[phase transitioned to: {coach_state.current_phase}]"
                    ))
                    break

            final_coach_state = coach_state_snapshot(CoachState.objects.get(user=user))
            final_phase = final_coach_state["current_phase"]

            base_report = {
                "scenario": scenario_label,
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

            verdict = self._judge(harness_client, transcript, context=prior)

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
                    "start_phase": start_phase,
                    "final_phase": final_phase,
                    "transitioned": final_phase != start_phase,
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
            if final_phase != start_phase:
                prog = f"{start_phase} -> {final_phase}"
            else:
                prog = f"did not transition (still {final_phase})"
            self.stdout.write(self.style.HTTP_INFO(f"PROGRESSION: {prog}"))
        finally:
            if not options["keep"]:
                User.objects.filter(email=cleanup_email).delete()
                self.stdout.write("\n(cleaned up throwaway user)")
            else:
                self.stdout.write(f"\n(kept throwaway user: {cleanup_email})")
