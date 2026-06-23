"""
build_eval_scenario

Build (or rebuild) an automated-test TestScenario by driving a persona through
the coach with the real pipeline, then freezing the resulting state.

This is how we recreate the per-phase scenario chain *attached to the automated
system*: start a persona at the introduction phase, let the user-bot click
through and converse until the coach transitions to the target phase, then freeze
that end-state as a named scenario. The frozen scenario becomes the starting
point for testing that phase — exactly like the hand-built "Casey - * Testing"
chain, but reproducible.

Run it once per phase boundary to extend the chain:
    introduction --> (freeze "start of get_to_know_you")
    get_to_know_you --> (freeze "start of identity_warm_up")
    ...

The conversation is driven component-aware: video and break gates are clicked
through by replaying their button actions (see apps/coach/eval/harness.py).

Freezing is OPT-IN. By default this is a dry run — it drives the conversation and
reports, but saves nothing, so your existing scenarios are never touched. Pass
--freeze to save the result, and --force to overwrite an existing name.

Usage:
    # Dry run — watch a persona go through the intro, save nothing:
    python manage.py build_eval_scenario --persona casey

    # Create the scenario (fails if the name already exists):
    python manage.py build_eval_scenario --freeze --name "[Auto] Casey @ get_to_know_you"

    # Replace an existing scenario:
    python manage.py build_eval_scenario --freeze --force --name "[Auto] Casey @ get_to_know_you"
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.chat_messages.utils import ensure_initial_message_exists
from apps.coach.eval.harness import (
    DEFAULT_USER_BOT_MODEL,
    Transcript,
    collect_new_actions,
    load_persona,
    pending_component,
    primary_button_actions,
    user_bot_reply,
)
from apps.coach.functions.public.process_message import process_message
from apps.coach_states.models import CoachState
from apps.test_scenario.functions.admin.freeze_user_session import (
    FreezeSessionError,
    freeze_user_session,
)
from apps.test_scenario.models import TestScenario
from enums.ai import AIModel
from enums.coaching_phase import CoachingPhase
from services.ai.ai_service_factory import AIServiceFactory

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Drive a persona through the coach (from the introduction phase by "
        "default) until it reaches a target phase. Dry run by default; pass "
        "--freeze to save the result as a named automated-test TestScenario."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--persona",
            type=str,
            default="casey",
            help="Persona id (filename stem in apps/coach/eval/personas/).",
        )
        parser.add_argument(
            "--name",
            type=str,
            default=None,
            help="Name for the frozen scenario. Defaults to a generated label.",
        )
        parser.add_argument(
            "--stop-phase",
            type=str,
            default=CoachingPhase.GET_TO_KNOW_YOU.value,
            help="Freeze once the coach transitions into this phase.",
        )
        parser.add_argument(
            "--coach-model",
            type=str,
            default=None,
            help="Override coach model. Defaults to the configured DEFAULT_AI_MODEL.",
        )
        parser.add_argument("--max-steps", type=int, default=40)
        parser.add_argument("--description", type=str, default="")
        parser.add_argument(
            "--freeze",
            action="store_true",
            help=(
                "Freeze the result as a TestScenario. WITHOUT this flag the run "
                "is a dry run: it drives the conversation and reports, but saves "
                "nothing (so it never touches your existing scenarios)."
            ),
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help=(
                "Allow --freeze to overwrite an existing scenario with the same "
                "--name. Without it, freezing onto an existing name is refused."
            ),
        )
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Keep the throwaway driving user instead of deleting it on exit.",
        )

    def handle(self, *args, **options):
        persona = load_persona(options["persona"])
        coach_model = AIModel.get_or_default(options["coach_model"])
        stop_phase = options["stop_phase"]
        max_steps = options["max_steps"]

        valid_phases = {p.value for p in CoachingPhase}
        if stop_phase not in valid_phases:
            self.stderr.write(self.style.ERROR(
                f"Unknown stop-phase '{stop_phase}'. Valid: {sorted(valid_phases)}"
            ))
            return

        name = options["name"] or f"[Auto] {persona.name} @ start of {stop_phase}"
        client = AIServiceFactory.create(DEFAULT_USER_BOT_MODEL).client

        # Persona name -> first/last for the frozen scenario's user.
        name_parts = persona.name.split()
        first_name = name_parts[0] if name_parts else persona.persona_id
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        email = f"eval-builder-{persona.persona_id}@testscenario.com"
        User.objects.filter(email=email).delete()  # idempotent
        user = User.objects.create_user(email=email, password="Coach123!")
        # New users start at INTRODUCTION (via signal). Seed the welcome video so
        # the first turn clicks through it.
        ensure_initial_message_exists(user)

        self.stdout.write(self.style.HTTP_INFO(
            f"Persona: {persona.name} | coach: {coach_model.value} "
            f"| start: introduction -> stop: {stop_phase} "
            f"| user-bot: {DEFAULT_USER_BOT_MODEL.value}"
        ))

        transcript: Transcript = []
        seen_action_ids: set = set()
        reached = False

        try:
            for step in range(max_steps):
                comp = pending_component(user)
                if comp:
                    actions = primary_button_actions(comp)
                    self.stdout.write(self.style.HTTP_INFO(
                        f"[click-through: {comp.get('component_type')} "
                        f"-> {[a.get('action') for a in actions]}]"
                    ))
                    ok, data, err = process_message(user, None, actions, coach_model)
                else:
                    user_msg = user_bot_reply(
                        client, DEFAULT_USER_BOT_MODEL, persona, transcript
                    )
                    transcript.append(("user", user_msg))
                    self.stdout.write(self.style.WARNING(f"\nCLIENT: {user_msg}"))
                    ok, data, err = process_message(user, user_msg, None, coach_model)

                if not ok:
                    self.stderr.write(self.style.ERROR(f"process_message failed: {err}"))
                    break

                coach_msg = data.get("message", "")
                if coach_msg:
                    transcript.append(("coach", coach_msg))
                    self.stdout.write(self.style.SUCCESS(f"COACH: {coach_msg}"))

                acts = collect_new_actions(user, seen_action_ids)
                if acts:
                    self.stdout.write(self.style.HTTP_INFO(
                        "  ↳ actions: " + ", ".join(a["action"] for a in acts)
                    ))

                current_phase = CoachState.objects.get(user=user).current_phase
                if current_phase == stop_phase:
                    reached = True
                    self.stdout.write(self.style.HTTP_INFO(
                        f"\n[reached stop phase '{stop_phase}' after {step + 1} steps]"
                    ))
                    break

            if not reached:
                final = CoachState.objects.get(user=user).current_phase
                self.stderr.write(self.style.ERROR(
                    f"Did not reach '{stop_phase}' within {max_steps} steps "
                    f"(stuck at '{final}'). Nothing frozen."
                ))
                return

            # Freezing is opt-in: without --freeze this is a dry run that saves
            # nothing, so existing scenarios are never touched.
            if not options["freeze"]:
                self.stdout.write(self.style.SUCCESS(
                    f"\nDry run complete — reached '{stop_phase}'. Nothing was saved.\n"
                    f"To save this as a scenario, re-run with: "
                    f"--freeze --name \"{name}\""
                ))
                return

            # --freeze given. Guard against clobbering an existing scenario.
            if TestScenario.objects.filter(name=name).exists():
                if not options["force"]:
                    self.stderr.write(self.style.ERROR(
                        f"A scenario named '{name}' already exists — refusing to "
                        f"overwrite it. Pass --force to replace it, or choose a "
                        f"different --name."
                    ))
                    return
                TestScenario.objects.filter(name=name).delete()
                self.stdout.write(self.style.WARNING(f"(--force: replacing '{name}')"))

            try:
                scenario = freeze_user_session(
                    user_id=str(user.id),
                    name=name,
                    description=(
                        options["description"]
                        or f"[Automated] {persona.name} at the start of {stop_phase}. "
                        "Generated by build_eval_scenario."
                    ),
                    first_name=first_name,
                    last_name=last_name,
                    created_by=None,
                )
            except FreezeSessionError as e:
                self.stderr.write(self.style.ERROR(f"Freeze failed: {e.detail}"))
                return

            t = scenario.template or {}
            self.stdout.write(self.style.SUCCESS(
                f"\nFroze scenario '{scenario.name}' (id={scenario.id}) at "
                f"phase '{stop_phase}': {len(t.get('chat_messages') or [])} messages, "
                f"{len(t.get('identities') or [])} identities, "
                f"{len(t.get('user_notes') or [])} notes."
            ))
        finally:
            if not options["keep"]:
                User.objects.filter(email=email).delete()
                self.stdout.write("(cleaned up throwaway driving user)")
            else:
                self.stdout.write(f"(kept throwaway driving user: {email})")
