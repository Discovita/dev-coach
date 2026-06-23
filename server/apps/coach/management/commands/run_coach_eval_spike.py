"""
run_coach_eval_spike

Phase-0 spike for the automated prompt-testing harness.

Proves the full loop end-to-end against the REAL coach pipeline (real prompt
assembly from the DB + real coach LLM):

    seed user at a phase
        -> user-bot (LLM persona) drives the conversation
        -> coach responds via process_message (the same code path the API uses)
        -> judge returns a verdict against the phase's own prompt + targeted checks

The persona is loaded from a markdown file (see apps/coach/eval/personas/), and
the loop is component-aware — it clicks through any video/break gates by
replaying their button actions. Shared pieces live in apps/coach/eval/harness.py.

The rubric is DERIVED LIVE from the phase's coach Prompt.body — the judge is
asked "did the coach follow these instructions?" — so it tracks the prompt
automatically and works for any phase, with nothing to hand-maintain. On top of
that, per-phase targeted checks (explicit pass/fail assertions in
apps/coach/eval/checks/<phase>.md, plus any --check flags) are evaluated and
reported separately.

Runs against the LIVE local database so it exercises whatever prompts are
currently active (i.e. the ones you just edited).

By default it creates a throwaway `@testscenario.com` user seeded cold at the
get_to_know_you phase. Pass --from-scenario "<name>" to instead hydrate a frozen
TestScenario (real prior history, built via build_eval_scenario) and pick the
eval up from that scenario's phase. Either way the throwaway user is deleted on
exit unless --keep is passed.

Replay: --save-run PATH writes the run (user turns + report) to a JSON artifact;
--replay PATH re-runs those exact user turns instead of generating new ones with
the user-bot. Combined with a different --prompt-version, replay removes user-bot
variance so the prompt is the only thing that changed — the basis for a fair
before/after. The artifact's persona/scenario/coach-model/version are used as
defaults on replay; pass the flags to override (e.g. a new --prompt-version).

Usage:
    python manage.py run_coach_eval_spike
    python manage.py run_coach_eval_spike --persona casey --max-turns 10 --keep
    python manage.py run_coach_eval_spike --coach-model gpt-4o --prompt-version 10
    python manage.py run_coach_eval_spike --from-scenario "[Auto] Casey @ start of get_to_know_you"
    python manage.py run_coach_eval_spike --check "Never asks more than one question per message"
    python manage.py run_coach_eval_spike --prompt-version 11 --save-run /tmp/v11.json
    python manage.py run_coach_eval_spike --replay /tmp/v11.json --prompt-version 12
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
    load_eval_run,
    load_persona,
    load_phase_prompt_body,
    load_targeted_checks,
    pending_component,
    primary_button_actions,
    render_transcript,
    save_eval_run,
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

# How to judge — the WHAT (the criteria) is derived live from the phase's own
# Prompt.body at runtime; this only frames HOW to apply it.
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
                "Pin the phase-under-test prompt to a specific version (for "
                "before/after comparisons). Defaults to the latest active. The "
                "derived rubric uses this same version's body."
            ),
        )
        parser.add_argument(
            "--check",
            action="append",
            default=None,
            metavar="ASSERTION",
            help=(
                "Add a one-off targeted check (repeatable), evaluated in addition "
                "to the per-phase checks file (apps/coach/eval/checks/<phase>.md)."
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
            "--save-run",
            type=str,
            default=None,
            metavar="PATH",
            help=(
                "Write the run (recorded user turns + full report) to a JSON "
                "artifact at PATH, for later --replay or inspection."
            ),
        )
        parser.add_argument(
            "--replay",
            type=str,
            default=None,
            metavar="PATH",
            help=(
                "Replay the user turns from a saved-run artifact instead of "
                "generating new ones with the user-bot. Persona / scenario / "
                "coach-model / prompt-version default from the artifact; pass the "
                "flags to override (e.g. --prompt-version to test a new version)."
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
        *,
        phase: str,
        rubric_body: str,
        transcript: Transcript,
        targeted_checks: Optional[List[str]] = None,
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
        checks_block = ""
        if targeted_checks:
            numbered = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(targeted_checks))
            checks_block = (
                "TARGETED CHECKS — in addition to the rubric, evaluate each of "
                "these explicit requirements as a hard yes/no and return a verdict "
                "+ note for each in `targeted_checks` (echo the check text "
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
            model=DEFAULT_JUDGE_MODEL,
            response_format=JudgeVerdict,
            temperature=0.0,
        )
        return completion.choices[0].message.parsed

    # --- orchestration --------------------------------------------------------
    def handle(self, *args, **options):
        # Replay: load the saved run's user turns and let its recorded
        # persona / scenario / coach-model / version stand in as defaults, so the
        # only thing that changes is whatever you override on the CLI (typically
        # --prompt-version). Explicit flags always win.
        replay_turns = None
        if options["replay"]:
            artifact = load_eval_run(options["replay"])
            replay_turns = artifact.get("user_turns") or []
            for key in ("coach_model", "prompt_version"):
                if options[key] is None and artifact.get(key) is not None:
                    options[key] = artifact[key]
            if options["from_scenario"] is None and artifact.get("scenario_seed"):
                options["from_scenario"] = artifact["scenario_seed"]
            if artifact.get("persona"):
                options["persona"] = artifact["persona"]
            self.stdout.write(self.style.HTTP_INFO(
                f"[replay: {len(replay_turns)} user turns from {options['replay']}]"
            ))

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

        # Phase-scoped version pin: only applies while the user is in start_phase.
        prompt_version = options["prompt_version"]
        prompt_versions = (
            {start_phase: prompt_version} if prompt_version is not None else None
        )

        # The rubric IS the phase's own prompt body (the same version the coach
        # runs), so it tracks the prompt automatically and works for any phase.
        # Targeted checks layer explicit assertions on top.
        rubric_body, rubric_version = load_phase_prompt_body(start_phase, prompt_version)
        if not rubric_body:
            self.stderr.write(self.style.ERROR(
                f"No active coach prompt for phase '{start_phase}'"
                + (f" at version {prompt_version}" if prompt_version else "")
                + " — cannot derive a rubric. Aborting."
            ))
            if not options["keep"]:
                User.objects.filter(email=cleanup_email).delete()
            return
        targeted_checks = load_targeted_checks(start_phase, options["check"])
        version_label = rubric_version if rubric_version is not None else "?"

        self.stdout.write(self.style.HTTP_INFO(
            f"Persona: {persona.name} | coach: {coach_model.value} "
            f"| start: {start_phase} (prompt v{version_label}) "
            f"| seed: {scenario_label} | targeted-checks: {len(targeted_checks)} "
            f"| user-bot: {DEFAULT_USER_BOT_MODEL.value} | judge: {DEFAULT_JUDGE_MODEL.value}"
        ))

        transcript: Transcript = []
        replay_idx = 0
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
                    if replay_turns is not None:
                        # Replay the recorded user turns verbatim (no user-bot),
                        # so the only variable vs the saved run is the prompt/model.
                        if replay_idx >= len(replay_turns):
                            self.stdout.write(self.style.HTTP_INFO(
                                f"\n[replay exhausted after {replay_idx} user turns]"
                            ))
                            break
                        user_msg = replay_turns[replay_idx]
                        replay_idx += 1
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
                if options["save_run"]:
                    # The report plus the recorded user turns + seed IS the replay
                    # artifact: --replay reads these back to re-run the same turns.
                    save_eval_run(options["save_run"], {
                        **report,
                        "scenario_seed": scenario_name,
                        "user_turns": [t[1] for t in transcript if t[0] == "user"],
                        "transcript": [{"role": r, "text": t} for r, t in transcript],
                    })
                    self.stdout.write(self.style.SUCCESS(
                        f"(saved run -> {options['save_run']})"
                    ))

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

            verdict = self._judge(
                harness_client,
                phase=start_phase,
                rubric_body=rubric_body,
                transcript=transcript,
                targeted_checks=targeted_checks,
                context=prior,
            )

            # Quality (rubric), targeted checks, and progression are reported as
            # SEPARATE outcomes, never AND-ed together. A high-quality conversation
            # that simply didn't transition within the turn budget is NOT a
            # failure — it's a non-transition, which is its own signal.
            report = {
                **base_report,
                "status": "ok",
                "quality": {
                    "passed": verdict.passed,
                    "score": verdict.score,
                    "rubric_source": {
                        "phase": start_phase,
                        "prompt_version": rubric_version,
                        "pinned": prompt_version is not None,
                    },
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
            }
            if targeted_checks:
                report["targeted_checks"] = [c.model_dump() for c in verdict.targeted_checks]
            _emit(report)

            # Independent outcomes — quality is the judge's call against the
            # phase prompt; targeted checks are explicit assertions; progression
            # is informational (phase movement within the turn budget).
            q_style = self.style.SUCCESS if verdict.passed else self.style.ERROR
            self.stdout.write(q_style(
                f"QUALITY:     {'PASS' if verdict.passed else 'FAIL'}  "
                f"(judge score {verdict.score}/5, vs {start_phase} prompt v{version_label})"
            ))
            if targeted_checks:
                passed = sum(1 for c in verdict.targeted_checks if c.passed)
                total = len(verdict.targeted_checks)
                c_style = self.style.SUCCESS if passed == total else self.style.ERROR
                self.stdout.write(c_style(
                    f"CHECKS:      {passed}/{total} passed"
                ))
                for c in verdict.targeted_checks:
                    mark = "✓" if c.passed else "✗"
                    self.stdout.write(self.style.HTTP_INFO(f"  {mark} {c.check}"))
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
