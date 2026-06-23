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

## Planned

- **Seed evals from a frozen scenario** — `--from-scenario "<name>"` on the eval so
  it picks a phase up from a built starting state (real prior history) instead of
  fresh-seeding. This is the next step.
- **Rubric derived from `Prompt.body`** ("did the Coach do what this prompt
  instructs?") plus a per-run list of **targeted checks** — the
  "phase X does Y and I hate it" cases.
- **Baseline ↔ candidate diff** — run two prompt versions and report the delta
  (deterministic outcome + per-criterion rubric scores).
- **Replay mode** — reuse a baseline run's exact user turns against the candidate
  prompt, so the only variable is the prompt (removes user-bot variance).
- **Transcript caching** — persist baseline transcripts keyed on
  `(phase, prompt_version, model, scenario, user_turns)` — *not* on the rubric — so
  a baseline is generated once and re-judged cheaply when requirements change. See
  the caching model in the
  [Overview](/docs/testing/eval-harness/overview#transcript-vs-judgment-the-caching-model).
- **`run_coach_eval` MCP tool** — on the `dev-coach-docs` MCP server, so the
  edit-prompt → eval → iterate loop runs without manual command invocation.
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
