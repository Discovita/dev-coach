---
sidebar_position: 6
---

# Roadmap

The eval harness is being built in phases. This page tracks what exists today
versus what is planned, so the docs stay honest about the system's maturity.
Update it as phases land.

## Built ✅

The core loop and the scenario-building tooling are in place.

- **End-to-end loop** — seed → drive → judge → report against the real coach
  pipeline. Command: `run_coach_eval_spike`.
- **Personas as swappable files** — `--persona`, loaded from
  `apps/coach/eval/personas/`. First persona: `casey`, extracted from the
  hand-built `Casey - * Testing` scenarios. See
  [Personas](/docs/testing/eval-harness/personas).
- **Component-aware driving** — clicks through `session_video` / `session_break`
  gates by replaying their button actions; ignores non-gating components.
- **Scenario chain builder** — `build_eval_scenario` drives a persona from the
  introduction phase to a target phase and (opt-in) freezes the result as a
  `TestScenario`. Dry-run by default; `--freeze` / `--force` to save/replace. See
  [Scenario Chain](/docs/testing/eval-harness/scenario-chain).
- **Phase-scoped prompt-version pinning** — `--prompt-version`, threaded through
  `process_message` → `build_coach_prompt` → `PromptManager`. See
  [Prompt Version Pinning](/docs/testing/eval-harness/prompt-versioning).
- **Shared harness module** — `apps/coach/eval/harness.py` holds persona loading,
  the user-bot, and the component driver, shared by both commands.
- **Observability** — per-turn coach-state snapshots (mirroring the admin Coach
  State viewer) and the coach's action log, surfaced inline and in the report.
  Quality and progression are reported as separate outcomes (not AND-ed).
- **Seed evals from a frozen scenario** — `--from-scenario "<name>"` hydrates a
  built starting state (real prior history) and picks the eval up from that
  scenario's phase instead of fresh-seeding. Prior history feeds the user-bot for
  continuity and the judge as context (not scored); only new actions are reported.
  See [Running Evals → Seeding from a frozen scenario](/docs/testing/eval-harness/running-evals#seeding-from-a-frozen-scenario).
- **Rubric derived from `Prompt.body`** — the rubric IS the phase's own coach
  prompt body (the same version the coach runs); the judge is asked "did the coach
  follow these instructions?", so it tracks the prompt automatically and works for
  any phase with nothing to hand-maintain. Plus per-phase **targeted checks**
  (explicit pass/fail assertions in `apps/coach/eval/checks/<phase>.md`, plus
  `--check` flags) reported as their own outcome. See
  [Running Evals → Rubric & targeted checks](/docs/testing/eval-harness/running-evals#rubric--targeted-checks).
- **Replay mode** — `--save-run PATH` records a run's exact user turns (+ report)
  to a JSON artifact; `--replay PATH` re-runs those turns instead of the user-bot,
  so the prompt/model is the only variable. The artifact's persona/scenario/
  coach-model/version are replay defaults; override with the flags (typically a new
  `--prompt-version`). See
  [Running Evals → Replay](/docs/testing/eval-harness/running-evals#replay-a-run).
- **Baseline ↔ candidate diff** — `run_coach_eval_diff` drives a baseline with the
  user-bot, replays the *same* user turns against a candidate, and reports the
  delta: per-side quality score, targeted-check changes (fixed/regressed),
  progression, and a **pairwise** judge that compares the two transcripts directly.
  The variable can be the prompt version, the coach model (`--baseline-model` /
  `--candidate-model`), or both. See
  [Running Evals → Diffing two runs](/docs/testing/eval-harness/running-evals#diffing-two-runs).
- **`run_coach_eval` MCP tool** — the `dev-coach-docs` MCP server exposes a
  `run_coach_eval` tool that POSTs to a new `POST /api/v1/eval/run` backend
  endpoint, so the edit-prompt → eval → iterate loop runs without shelling into
  Django. (Single-eval; a diff tool can follow.) See
  [Running Evals → From the MCP server](/docs/testing/eval-harness/running-evals#from-the-mcp-server).

## Planned

- **Transcript caching** — persist baseline transcripts keyed on
  `(phase, prompt_version, model, scenario, user_turns)` — *not* on the rubric — so
  a baseline is generated once and re-judged cheaply when requirements change. See
  the caching model in the
  [Overview](/docs/testing/eval-harness/overview#transcript-vs-judgment-the-caching-model).
- **`run_coach_eval_diff` MCP tool** — expose the baseline↔candidate diff over MCP too.
- **Suites & k-run pass rates** — multiple scenarios per phase, and repeated runs to
  handle LLM non-determinism instead of single-sample pass/fail.

## Known constraints

- **OpenAI egress** — the harness needs the DB and outbound OpenAI access at once.
  Run it in the backend container when it has egress, or from the host otherwise.
  See [Running Evals → Where it runs](/docs/testing/eval-harness/running-evals#running-from-the-host-instead).
- **LLM non-determinism** — a single run is one sample; rigorous comparison needs
  multiple runs or replay mode.
- **Chain build cost** — `build_eval_scenario` drives from the introduction each
  run, so later links take longer to build.

## Related Documentation

- **[Overview](/docs/testing/eval-harness/overview)** — architecture
- **[Personas](/docs/testing/eval-harness/personas)** — the simulated user
- **[Scenario Chain](/docs/testing/eval-harness/scenario-chain)** — starting states
- **[Running Evals](/docs/testing/eval-harness/running-evals)** — how to run today
- **[Prompt Version Pinning](/docs/testing/eval-harness/prompt-versioning)** — before/after
