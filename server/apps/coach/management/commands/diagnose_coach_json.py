"""
diagnose_coach_json

Reproduce and capture the intermittent malformed-JSON failure from the coach LLM.

The coach uses structured outputs via `client.beta.chat.completions.parse(...)`,
which parses the model's content into a Pydantic model and RAISES on bad JSON —
so the raw model output is discarded and we never see what actually came back.

This command replicates the exact coach generation call:
  - builds the real coach prompt for a seeded user at a phase (via build_coach_prompt),
  - derives the SAME json_schema response_format the SDK's .parse() would use,
  - but calls the raw `client.chat.completions.create(...)` so we keep
    `message.content` verbatim,
  - then attempts the same Pydantic validation ourselves and, on failure, dumps
    the exact raw bytes.

Run it many times to catch the intermittent failure and see precisely what the
model appended.

Usage:
    python manage.py diagnose_coach_json --iterations 30
    python manage.py diagnose_coach_json --phase get_to_know_you --message "yeah, sounds good — i'm Casey."
"""

import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from openai.lib._parsing._completions import type_to_response_format_param
from pydantic import ValidationError

from apps.chat_messages.utils import add_chat_message
from apps.coach.utils import build_coach_prompt
from apps.coach_states.models import CoachState
from enums.ai import AIModel
from enums.message_role import MessageRole
from services.ai.ai_service_factory import AIServiceFactory

User = get_user_model()

DIAG_EMAIL = "coach-json-diag@testscenario.com"


class Command(BaseCommand):
    help = "Reproduce the coach malformed-JSON failure and capture the raw output."

    def add_arguments(self, parser):
        parser.add_argument("--iterations", type=int, default=30)
        parser.add_argument("--phase", type=str, default="get_to_know_you")
        parser.add_argument("--coach-model", type=str, default=None)
        parser.add_argument(
            "--message",
            type=str,
            default="Sounds good! I'm Casey — go ahead and ask me whatever you'd like.",
            help="The latest user message to seed into the prompt's recent history.",
        )
        parser.add_argument(
            "--dump-all",
            action="store_true",
            help="Dump the raw content for successful calls too (not just failures).",
        )

    def _seed(self, phase: str, message: str) -> User:
        User.objects.filter(email=DIAG_EMAIL).delete()
        user = User.objects.create_user(email=DIAG_EMAIL, password="Coach123!")
        cs = CoachState.objects.get(user=user)
        cs.current_phase = phase
        # Mark the welcome video acknowledged so the prompt reflects an
        # in-progress conversation (no video gate).
        cs.shown_videos = ["welcome_session_intro"]
        cs.save(update_fields=["current_phase", "shown_videos"])
        # A minimal recent history so build_coach_prompt produces a realistic
        # mid-conversation prompt.
        add_chat_message(
            user,
            "Before we get into the Identity work, I'd love to get to know you "
            "better. Sound good?",
            MessageRole.COACH,
        )
        add_chat_message(user, message, MessageRole.USER)
        return user

    def handle(self, *args, **options):
        iterations = options["iterations"]
        model = AIModel.get_or_default(options["coach_model"])
        user = self._seed(options["phase"], options["message"])

        coach_prompt, response_format = build_coach_prompt(user, model)
        rf_param = type_to_response_format_param(response_format)
        client = AIServiceFactory.create(model).client

        # Mirror structured_completion's params for this model.
        token_param = AIModel.get_token_param_name(model)
        params = {
            "model": model.value,
            "messages": [{"role": "system", "content": coach_prompt}],
            "response_format": rf_param,
            token_param: AIModel.get_default_token_limit(model),
        }
        if "gpt-5" in model.value:
            params["reasoning_effort"] = "low"

        self.stdout.write(self.style.HTTP_INFO(
            f"Model: {model.value} | phase: {options['phase']} | "
            f"iterations: {iterations} | response_format: {response_format.__name__}"
        ))

        malformed = 0
        finish_reasons = {}
        try:
            for i in range(iterations):
                completion = client.chat.completions.create(**params)
                choice = completion.choices[0]
                raw = choice.message.content or ""
                finish = choice.finish_reason
                finish_reasons[finish] = finish_reasons.get(finish, 0) + 1

                try:
                    response_format.model_validate_json(raw)
                    ok = True
                    err = None
                except (ValidationError, json.JSONDecodeError) as e:
                    ok = False
                    err = str(e).splitlines()[0]
                    malformed += 1

                # Flag whether the model emitted an action (the more complex,
                # nested response shape that the original failure exhibited).
                has_action = any(
                    f'"{a}"' in raw
                    for a in ("update_asked_questions", "transition_phase")
                )
                tag = "OK  " if ok else "BAD "
                self.stdout.write(
                    f"[{i:02d}] {tag} finish={finish} len={len(raw)} "
                    f"action={'Y' if has_action else 'n'}"
                    + ("" if ok else f"  err={err}")
                )
                if not ok or options["dump_all"]:
                    self.stdout.write(self.style.WARNING("---- RAW CONTENT ----"))
                    self.stdout.write(raw)
                    self.stdout.write(self.style.WARNING("---- repr(last 300) ----"))
                    self.stdout.write(repr(raw[-300:]))
                    self.stdout.write(self.style.WARNING("---- END ----"))

            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(
                f"malformed: {malformed}/{iterations}  |  finish_reasons: {finish_reasons}"
            )
        finally:
            User.objects.filter(email=DIAG_EMAIL).delete()
