"""
HTTP endpoint for the automated coach eval harness.

Exposes run_phase_eval (the same loop as run_coach_eval_spike) over the API so it
can be driven from the dev-coach-docs MCP server's `run_coach_eval` tool — no
shelling into the Django container required.

See: apps/coach/views/__init__.py
"""

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from apps.coach.eval.harness import EvalError, run_phase_eval
from apps.coach.serializers import EvalRunSerializer
from apps.test_scenario.models import TestScenario
from enums.ai import AIModel
from permissions import IsAdminUser
from services.logger import configure_logging

log = configure_logging(__name__)


def _eval_harness_enabled() -> bool:
    """On locally/dev (DEBUG) by default; off in production. Override with the
    EVAL_HARNESS_ENABLED env var (true/false) in any environment."""
    flag = settings.EVAL_HARNESS_ENABLED
    if flag is None:
        return bool(settings.DEBUG)
    return str(flag).lower() == "true"


class EvalViewSet(viewsets.ViewSet):
    """Run one automated coach eval and return its report.

    POST /api/v1/eval/run — drives a persona against a phase (cold or from a
    frozen scenario), judges it against the phase's derived rubric + targeted
    checks, and returns the report JSON. Synchronous: the call runs the real coach
    pipeline (several minutes of LLM calls) before responding.
    """

    permission_classes = [HasAPIKey | IsAdminUser]

    @action(detail=False, methods=["post"], url_path="run")
    def run(self, request):
        if not _eval_harness_enabled():
            return Response(
                {"detail": "The eval harness is disabled in this environment."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EvalRunSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        coach_model = AIModel.get_or_default(data["coach_model"])

        try:
            report = run_phase_eval(
                persona_id=data["persona"],
                scenario_name=data["from_scenario"],
                coach_model=coach_model,
                prompt_version=data["prompt_version"],
                checks=data["checks"],
                max_turns=data["max_turns"],
            )
        except TestScenario.DoesNotExist:
            names = list(
                TestScenario.objects.order_by("name").values_list("name", flat=True)
            )
            return Response(
                {"detail": f"No TestScenario named '{data['from_scenario']}'.",
                 "available": names},
                status=status.HTTP_404_NOT_FOUND,
            )
        except FileNotFoundError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except EvalError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(report, status=status.HTTP_200_OK)
