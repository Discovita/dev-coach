"""
Request serializer for the coach eval endpoint (POST /api/v1/eval/run).

See: apps/coach/serializers/__init__.py
"""

from rest_framework import serializers


class EvalRunSerializer(serializers.Serializer):
    """Validates the inputs for one automated coach eval run.

    Mirrors run_coach_eval_spike's flags: drive a persona against a phase (cold or
    from a frozen scenario), optionally pin a prompt version, layer extra targeted
    checks, and cap the turn budget.
    """

    persona = serializers.CharField(required=False, default="casey")
    from_scenario = serializers.CharField(
        required=False, allow_null=True, default=None,
        help_text="Exact TestScenario name to hydrate; omit to cold-seed get_to_know_you.",
    )
    coach_model = serializers.CharField(
        required=False, allow_null=True, default=None,
        help_text="Coach model id; defaults to the configured DEFAULT_AI_MODEL.",
    )
    prompt_version = serializers.IntegerField(
        required=False, allow_null=True, default=None, min_value=1,
        help_text="Pin the phase prompt (and derived rubric) to this version.",
    )
    checks = serializers.ListField(
        child=serializers.CharField(), required=False, default=list,
        help_text="One-off targeted checks, on top of the per-phase checks file.",
    )
    max_turns = serializers.IntegerField(
        required=False, default=20, min_value=1, max_value=40,
        help_text="Cap on conversation turns before the run stops.",
    )
