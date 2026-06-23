"""
run_coach_eval_diff

Baseline ↔ candidate diff for coach prompt changes — "did my edit help?".

Runs the SAME conversation against two prompt versions and reports the delta:

    seed user at a phase
        -> drive BASELINE (--baseline-version) with the user-bot, judge it
        -> RE-seed an identical user
        -> REPLAY the baseline's exact user turns against CANDIDATE
           (--candidate-version), judge it
        -> pairwise judge: show both coach transcripts (same client turns) and
           ask which performed better
        -> report the delta (quality score, targeted checks, progression,
           pairwise preference)

Replay holds the user side fixed, so the prompt version is the only thing that
differs between the two runs. Each run's quality rubric is still derived from its
OWN prompt body (a v11 run is judged against v11's instructions); the targeted
checks are constant across versions, so they give a clean apples-to-apples delta.
The pairwise judge compares the two transcripts directly (more reliable than
differencing two absolute scores).

Shares all the machinery (seeding, drive loop, judge) with run_coach_eval_spike
via apps/coach/eval/harness.py.

Usage:
    python manage.py run_coach_eval_diff --baseline-version 10 --candidate-version 11
    python manage.py run_coach_eval_diff --candidate-version 11   # baseline = latest
    python manage.py run_coach_eval_diff --from-scenario "[Auto] Casey @ get_to_know_you" \
        --baseline-version 10 --candidate-version 11 --out /tmp/diff.json
"""

import json
from typing import List, Optional

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from pydantic import BaseModel, Field

from apps.coach.eval.harness import (
    DEFAULT_JUDGE_MODEL,
    DEFAULT_USER_BOT_MODEL,
    Transcript,
    chat_history_transcript,
    drive_eval,
    judge_transcript,
    load_phase_prompt_body,
    load_persona,
    load_targeted_checks,
    render_transcript,
    save_eval_run,
    seed_cold_user,
    seed_scenario_user,
)
from apps.test_scenario.models import TestScenario
from enums.ai import AIModel
from enums.coaching_phase import CoachingPhase
from services.ai.ai_service_factory import AIServiceFactory
from services.ai.utils.openai import structured_completion

User = get_user_model()

DIFF_EMAIL = "coach-eval-diff@testscenario.com"
DEFAULT_START_PHASE = CoachingPhase.GET_TO_KNOW_YOU

# A/B are shown to the pairwise judge instead of baseline/candidate so it can't
# be biased toward "the newer one". We map back after.
_AB_TO_ROLE = {"A": "baseline", "B": "candidate", "tie": "tie"}


class PairwiseAspect(BaseModel):
    aspect: str
    winner: str = Field(description="'A', 'B', or 'tie'.")
    note: str


class PairwiseVerdict(BaseModel):
    """Direct comparison of two coach transcripts over identical client turns."""

    winner: str = Field(description="Overall better coach: 'A', 'B', or 'tie'.")
    aspects: List[PairwiseAspect] = Field(
        description="Per-aspect comparisons (e.g. warmth, focus, forward motion)."
    )
    reasoning: str


class Command(BaseCommand):
    help = "Diff two coach prompt versions over the same (replayed) conversation."

    def add_arguments(self, parser):
        parser.add_argument("--max-turns", type=int, default=20)
        parser.add_argument("--persona", type=str, default="casey")
        parser.add_argument(
            "--coach-model",
            type=str,
            default=None,
            help="Coach model for BOTH runs (the variable is the prompt, not the model).",
        )
        parser.add_argument(
            "--baseline-version",
            type=int,
            default=None,
            help="Baseline prompt version. Defaults to the latest active.",
        )
        parser.add_argument(
            "--candidate-version",
            type=int,
            default=None,
            help="Candidate prompt version. Defaults to the latest active.",
        )
        parser.add_argument(
            "--from-scenario",
            type=str,
            default=None,
            metavar="NAME",
            help="Seed both runs from a frozen TestScenario instead of cold-seeding.",
        )
        parser.add_argument(
            "--check",
            action="append",
            default=None,
            metavar="ASSERTION",
            help="Add a one-off targeted check (repeatable), on top of the phase file.",
        )
        parser.add_argument(
            "--out",
            type=str,
            default=None,
            metavar="PATH",
            help="Write the full diff report to PATH as JSON.",
        )
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Keep the throwaway test user instead of deleting it on exit.",
        )

    # --- seeding (fresh, identical state for each run) -------------------------
    def _seed(self, scenario_name):
        """Return (user, cleanup_email, start_phase, prior) for a fresh run."""
        if scenario_name:
            user, email, start_phase = seed_scenario_user(scenario_name)
            return user, email, start_phase, chat_history_transcript(user)
        user = seed_cold_user(DIFF_EMAIL, DEFAULT_START_PHASE.value)
        return user, DIFF_EMAIL, DEFAULT_START_PHASE.value, []

    def _make_emit(self, label):
        def emit(kind: str, text: str) -> None:
            if kind == "client":
                self.stdout.write(self.style.WARNING(f"[{label}] CLIENT: {text}"))
            elif kind == "coach":
                self.stdout.write(self.style.SUCCESS(f"[{label}] COACH: {text}"))
            elif kind == "error":
                self.stderr.write(self.style.ERROR(f"[{label}] failed: {text}"))
            # gate/action/info are suppressed in diff mode to keep output readable
        return emit

    def _pairwise(self, client, *, phase, reference_body, transcript_a, transcript_b):
        convo_a = render_transcript(transcript_a, you_label="CLIENT")
        convo_b = render_transcript(transcript_b, you_label="CLIENT")
        system = (
            "You are comparing two COACHES, A and B, who each responded to the "
            f"SAME client messages in the {phase} phase of identity coaching. The "
            "client's turns are identical in both transcripts; only the coach "
            "differs. Decide which coach served the client better. Judge coaching "
            "behavior and conversational quality — IGNORE output formatting/JSON.\n\n"
            "Reference — the intended behavior for this phase:\n"
            f"--- BEGIN INSTRUCTIONS ---\n{reference_body}\n--- END INSTRUCTIONS ---\n\n"
            f"=== COACH A ===\n{convo_a}\n\n=== COACH B ===\n{convo_b}\n\n"
            "Return winner ('A', 'B', or 'tie'), per-aspect comparisons, and your "
            "reasoning. Be willing to call a genuine 'tie'."
        )
        completion = structured_completion(
            client=client,
            messages=[{"role": "system", "content": system}],
            model=DEFAULT_JUDGE_MODEL,
            response_format=PairwiseVerdict,
            temperature=0.0,
        )
        return completion.choices[0].message.parsed

    def _run_side(self, *, label, version, user, start_phase, prior, coach_model,
                  max_turns, harness_client, targeted_checks, persona, replay_turns):
        """Drive (or replay) one side, judge it against its own prompt body, and
        return a dict describing the run, or None if its prompt is missing or the
        pipeline errored."""
        rubric_body, rubric_version = load_phase_prompt_body(start_phase, version)
        if not rubric_body:
            self.stderr.write(self.style.ERROR(
                f"No active coach prompt for phase '{start_phase}'"
                + (f" at version {version}" if version else "") + f" ({label})."
            ))
            return None
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n=== {label.upper()} (prompt v{rubric_version}) ==="
        ))
        prompt_versions = {start_phase: version} if version is not None else None
        run = drive_eval(
            user,
            coach_model=coach_model,
            prompt_versions=prompt_versions,
            start_phase=start_phase,
            max_turns=max_turns,
            harness_client=harness_client,
            persona=persona,
            prior=prior,
            replay_turns=replay_turns,
            emit=self._make_emit(label),
        )
        if run.run_error is not None:
            self.stderr.write(self.style.ERROR(
                f"{label} run failed: {run.run_error} — cannot diff."
            ))
            return None
        verdict = judge_transcript(
            harness_client,
            phase=start_phase,
            rubric_body=rubric_body,
            transcript=run.transcript,
            targeted_checks=targeted_checks,
            context=prior,
        )
        return {
            "prompt_version": rubric_version,
            "run": run,
            "verdict": verdict,
        }

    # --- orchestration --------------------------------------------------------
    def handle(self, *args, **options):
        coach_model = AIModel.get_or_default(options["coach_model"])
        persona = load_persona(options["persona"])
        harness_client = AIServiceFactory.create(DEFAULT_USER_BOT_MODEL).client
        scenario_name = options["from_scenario"]
        max_turns = options["max_turns"]
        baseline_version = options["baseline_version"]
        candidate_version = options["candidate_version"]

        if baseline_version == candidate_version:
            self.stdout.write(self.style.WARNING(
                "NOTE: baseline and candidate resolve to the same version "
                f"({baseline_version if baseline_version is not None else 'latest'}) "
                "— the diff will only reflect coach/user-bot nondeterminism."
            ))

        cleanup_emails = set()
        try:
            # --- Baseline: drive fresh with the user-bot ----------------------
            try:
                user, email, start_phase, prior = self._seed(scenario_name)
            except TestScenario.DoesNotExist:
                names = list(
                    TestScenario.objects.order_by("name").values_list("name", flat=True)
                )
                self.stderr.write(self.style.ERROR(
                    f"No TestScenario named '{scenario_name}'. Available:\n  "
                    + "\n  ".join(names or ["(none)"])
                ))
                return
            cleanup_emails.add(email)
            targeted_checks = load_targeted_checks(start_phase, options["check"])

            self.stdout.write(self.style.HTTP_INFO(
                f"Diff | persona: {persona.name} | coach: {coach_model.value} "
                f"| phase: {start_phase} | seed: {scenario_name or 'cold get_to_know_you'} "
                f"| baseline v{baseline_version or 'latest'} vs candidate "
                f"v{candidate_version or 'latest'} | checks: {len(targeted_checks)}"
            ))

            baseline = self._run_side(
                label="baseline", version=baseline_version, user=user,
                start_phase=start_phase, prior=prior, coach_model=coach_model,
                max_turns=max_turns, harness_client=harness_client,
                targeted_checks=targeted_checks, persona=persona, replay_turns=None,
            )
            if baseline is None:
                return
            user_turns = baseline["run"].user_turns

            # --- Candidate: re-seed identical, replay the same user turns ------
            user, email, start_phase, prior = self._seed(scenario_name)
            cleanup_emails.add(email)
            candidate = self._run_side(
                label="candidate", version=candidate_version, user=user,
                start_phase=start_phase, prior=prior, coach_model=coach_model,
                max_turns=max_turns, harness_client=harness_client,
                targeted_checks=targeted_checks, persona=None, replay_turns=user_turns,
            )
            if candidate is None:
                return

            # --- Pairwise comparison over the two transcripts -----------------
            candidate_body, _ = load_phase_prompt_body(start_phase, candidate_version)
            pairwise = self._pairwise(
                harness_client,
                phase=start_phase,
                reference_body=candidate_body,
                transcript_a=baseline["run"].transcript,
                transcript_b=candidate["run"].transcript,
            )

            self._report(
                start_phase=start_phase,
                scenario_name=scenario_name,
                persona=persona,
                coach_model=coach_model,
                user_turns=user_turns,
                targeted_checks=targeted_checks,
                baseline=baseline,
                candidate=candidate,
                pairwise=pairwise,
                out_path=options["out"],
            )
        finally:
            if not options["keep"]:
                for email in cleanup_emails:
                    User.objects.filter(email=email).delete()
                self.stdout.write("\n(cleaned up throwaway users)")
            else:
                self.stdout.write(f"\n(kept throwaway users: {sorted(cleanup_emails)})")

    # --- reporting ------------------------------------------------------------
    def _check_deltas(self, baseline_verdict, candidate_verdict):
        """Pair targeted-check results by check text; classify each change."""
        b = {c.check: c.passed for c in baseline_verdict.targeted_checks}
        out = []
        for c in candidate_verdict.targeted_checks:
            was = b.get(c.check)
            if was is None:
                change = "new"
            elif was == c.passed:
                change = "same"
            elif c.passed:
                change = "fixed"
            else:
                change = "regressed"
            out.append({
                "check": c.check,
                "baseline": was,
                "candidate": c.passed,
                "change": change,
            })
        return out

    def _report(self, *, start_phase, scenario_name, persona, coach_model,
                user_turns, targeted_checks, baseline, candidate, pairwise, out_path):
        bv, cv = baseline["verdict"], candidate["verdict"]
        b_phase = baseline["run"].final_phase
        c_phase = candidate["run"].final_phase
        check_deltas = self._check_deltas(bv, cv)
        winner_role = _AB_TO_ROLE.get(pairwise.winner.strip(), pairwise.winner)

        report = {
            "phase": start_phase,
            "scenario": scenario_name or "cold get_to_know_you",
            "persona": persona.persona_id,
            "coach_model": coach_model.value,
            "user_turns": user_turns,
            "baseline": {
                "prompt_version": baseline["prompt_version"],
                "quality": {"passed": bv.passed, "score": bv.score},
                "final_phase": b_phase,
                "transitioned": b_phase != start_phase,
            },
            "candidate": {
                "prompt_version": candidate["prompt_version"],
                "quality": {"passed": cv.passed, "score": cv.score},
                "final_phase": c_phase,
                "transitioned": c_phase != start_phase,
            },
            "deltas": {
                "quality_score": cv.score - bv.score,
                "targeted_checks": check_deltas,
            },
            "pairwise": {
                "winner": winner_role,
                "aspects": [
                    {"aspect": a.aspect, "winner": _AB_TO_ROLE.get(a.winner.strip(), a.winner), "note": a.note}
                    for a in pairwise.aspects
                ],
                "reasoning": pairwise.reasoning,
            },
        }

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.MIGRATE_HEADING("DIFF REPORT"))
        self.stdout.write(json.dumps(report, indent=2))
        self.stdout.write("=" * 70)
        if out_path:
            save_eval_run(out_path, report)
            self.stdout.write(self.style.SUCCESS(f"(wrote diff -> {out_path})"))

        # --- terminal summary ---
        bvers, cvers = baseline["prompt_version"], candidate["prompt_version"]
        self.stdout.write(self.style.HTTP_INFO(
            f"\nPROMPTS:  baseline v{bvers}  vs  candidate v{cvers}"
        ))
        delta = cv.score - bv.score
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "=")
        q_style = self.style.SUCCESS if delta > 0 else (
            self.style.ERROR if delta < 0 else self.style.HTTP_INFO)
        self.stdout.write(q_style(
            f"QUALITY:  v{bvers} {bv.score}/5  ->  v{cvers} {cv.score}/5  ({arrow} {delta:+d})"
        ))
        if targeted_checks:
            fixed = [d["check"] for d in check_deltas if d["change"] == "fixed"]
            regressed = [d["check"] for d in check_deltas if d["change"] == "regressed"]
            b_pass = sum(1 for d in check_deltas if d["baseline"])
            c_pass = sum(1 for d in check_deltas if d["candidate"])
            c_style = self.style.ERROR if regressed else self.style.SUCCESS
            self.stdout.write(c_style(
                f"CHECKS:   v{bvers} {b_pass}/{len(check_deltas)}  ->  "
                f"v{cvers} {c_pass}/{len(check_deltas)}  "
                f"(fixed {len(fixed)}, regressed {len(regressed)})"
            ))
            for d in check_deltas:
                if d["change"] in ("fixed", "regressed", "new"):
                    mark = {"fixed": "▲", "regressed": "▼", "new": "+"}[d["change"]]
                    self.stdout.write(self.style.HTTP_INFO(f"  {mark} {d['check']}"))
        self.stdout.write(self.style.HTTP_INFO(
            f"PROGRESS: v{bvers} {'transitioned' if b_phase != start_phase else 'no'}"
            f"  ->  v{cvers} {'transitioned' if c_phase != start_phase else 'no'}"
        ))
        p_style = self.style.SUCCESS if winner_role == "candidate" else (
            self.style.ERROR if winner_role == "baseline" else self.style.HTTP_INFO)
        self.stdout.write(p_style(f"PAIRWISE: {winner_role} preferred"))
