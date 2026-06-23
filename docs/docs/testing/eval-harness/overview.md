---
sidebar_position: 1
---

# Overview

The **Automated Eval Harness** lets you test coach prompt changes without manually
chatting with the Coach. It simulates a full conversation against the real coach
pipeline, then judges the result — so a prompt edit can be verified for its
intended effect automatically.

> **Why this exists:** Manual testing of prompt changes (open the app, role-play a
> client through a phase, eyeball the responses) was consuming the majority of
> development time. The harness automates the "role-play and evaluate" loop.

This page enumerates the architecture. Then:

- [Personas](/docs/testing/eval-harness/personas) — who the simulated user is.
- [Scenario Chain](/docs/testing/eval-harness/scenario-chain) — how starting states
  are built per phase.
- [Running Evals](/docs/testing/eval-harness/running-evals) — how to actually run it.

## The loop

A single eval run is four stages:

```
  ┌──────────────────────────────────────────────────────────────┐
  │ 1. SEED      user at a target coaching phase (fresh, or from   │
  │              a frozen TestScenario with real prior history)    │
  └──────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌──────────────────────────────────────────────────────────────┐
  │ 2. DRIVE     user-bot (LLM + persona file) writes the client's │
  │              reply ──► process_message() ──► coach reply        │
  │              (real prompt assembly from DB + real coach model)  │
  │              component gates (videos/breaks) are clicked        │
  │              through automatically; repeat until phase          │
  │              transition OR max turns                            │
  └──────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌──────────────────────────────────────────────────────────────┐
  │ 3. JUDGE     deterministic checks (final phase, actions) +      │
  │              LLM-as-judge rubric over the full transcript       │
  └──────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌──────────────────────────────────────────────────────────────┐
  │ 4. REPORT    transcript + verdict JSON (pass/fail + reasoning)  │
  └──────────────────────────────────────────────────────────────┘
```

The critical property: stage 2 calls the **same `process_message` code path the
real API uses** (`server/apps/coach/functions/public/process_message.py`). It is
not mocked. The prompts come from the database and the coach model is the
configured default — so the harness validates the *actual* prompts you just
edited, end to end.

## Components

The reusable pieces live in `server/apps/coach/eval/harness.py`; the management
commands wire them together.

| Component | What it is | Where |
| --- | --- | --- |
| **Persona** | A swappable Markdown file describing who the simulated client is. Its body becomes the user-bot's system prompt. | `server/apps/coach/eval/personas/*.md` |
| **User-bot** | An LLM driven by the persona + the running transcript; returns the client's next message. Cheap model. | `harness.user_bot_reply` |
| **Component driver** | Clicks through gating UI components (session videos, breaks) by replaying their button actions — no per-component hardcoding. | `harness.pending_component`, `primary_button_actions` |
| **Coach** | The real pipeline: `process_message` → `build_coach_prompt` → `PromptManager` → coach LLM → action handler. | [Prompt Manager](/docs/core-systems/prompt-manager/overview), [Action Handler](/docs/core-systems/action-handler/overview) |
| **Drive loop** | Seeds a user, drives (or replays) the conversation, records turns + actions + state. Shared by both commands. | `harness.drive_eval` |
| **Judge** | An LLM-as-judge scoring the transcript against the phase's derived rubric + targeted checks. Stronger model. | `harness.judge_transcript` |
| **Diff** | Drives a baseline version, replays the same turns against a candidate, and reports the delta + a pairwise comparison. | `run_coach_eval_diff` command |
| **Scenario builder** | Drives a persona from the intro phase and (optionally) freezes the end-state as a per-phase starting scenario. | `build_eval_scenario` command |

### Models used by the harness

These are the models the *harness* uses — separate from the coach model under test.

- **User-bot:** `gpt-5.4-mini` (cheap; realistic enough to drive a conversation).
- **Judge:** `gpt-4o` (stronger; more reliable verdicts).
- **Coach:** the configured `DEFAULT_AI_MODEL` (currently `gpt-5.4`), overridable per run.

All are OpenAI; keys come from `OPENAI_API_KEY` (already in the environment — it is
how the Coach itself runs). Model ids live in `server/enums/ai.py`. Defaults for the
harness are `DEFAULT_USER_BOT_MODEL` / `DEFAULT_JUDGE_MODEL` in `harness.py`.

## Component-aware driving

Several coaching phases gate the conversation behind UI components the client must
click through: the welcome video, per-session intro/outro videos, and breaks. The
harness handles these **generically** — when the latest coach message carries a
gating component, it replays that component's primary-button actions (e.g.
`acknowledge_session_video`, `end_break`) verbatim as `request_component_actions`,
instead of having the user-bot type text.

Only genuine gates are treated this way (`GATE_COMPONENT_TYPES` = `session_video`,
`session_break`). Other components like `intro_canned_response` are reply
*shortcuts*, not gates, so the user-bot just types a normal message when it sees
them.

## The judge has two layers

1. **Deterministic checks** — read straight from the DB / response. Cheap, exact,
   and immune to LLM flakiness. Examples: did `current_phase` advance to an
   expected phase? Was a disallowed action emitted? These catch most regressions.
2. **LLM-as-judge rubric** — for qualitative behavior the deterministic layer
   cannot see. The rubric is **derived live from the phase's own coach
   `Prompt.body`** (the same version the coach ran): the judge is asked "did the
   coach follow these instructions?" and derives the criteria from the body
   itself, so it tracks the prompt automatically and needs no maintenance. On top
   of that, hand-authored **targeted checks** (per-phase files + `--check` flags)
   assert specific "must do X / must never do Y" behaviors. See
   [Running Evals → Rubric & targeted checks](/docs/testing/eval-harness/running-evals#rubric--targeted-checks).

These are reported as **separate, independent outcomes** — `quality` (the judge's
verdict against the derived rubric), `targeted_checks` (explicit assertions), and
`progression` (phase movement) — never AND-ed into a single pass/fail. A 5/5
conversation that simply didn't transition within the turn budget is a
*non-transition*, not a failure; conflating them hides the real signal.

Because LLM output is non-deterministic, a single run is one sample. Rigorous
suites run each scenario several times and report a pass *rate*.

## Observability: state + action log

To see what the coach is actually *doing* (not just what it says), the harness
captures, after every turn:

- **Coach state snapshot** — the same fields the admin Coach State viewer shows,
  via `CoachStateSerializer` (phase, identity focus, who-you-are, asked questions,
  shown videos, current identity). Surfaced as `final_coach_state` in the report.
- **Action log** — the [Action](/docs/database/models/action) rows the coach wrote
  that turn (e.g. `update_asked_questions`, `transition_phase`), with their params
  and result summaries. Surfaced as `actions` in the report and a `↳ actions:` line
  in the live output.

This makes a run legible: you can see *which* get-to-know-you questions the coach
recorded, when it created an identity, or exactly when it transitioned — the
structural truth behind the conversation text.

## Before / after is the point

You can only tell whether a prompt change helped by comparing **before** (old
prompt) and **after** (new prompt) on the same scenario. The harness supports this
via [phase-scoped prompt-version pinning](/docs/testing/eval-harness/prompt-versioning):
run the baseline pinned to the old version, run the candidate pinned to the new
version, and diff the outcomes.

### Transcript vs. judgment (the caching model)

A run splits into two halves with very different costs and cache behavior:

- **Transcript** — what the Coach actually did. Depends only on
  `(phase, prompt_version, model, scenario/persona, user turns)`. Expensive (many
  coach LLM calls). **Cacheable** as a baseline.
- **Judgment** — a rubric + targeted checks applied to a transcript. Cheap (no
  coach calls). Changes every time requirements change.

Key insight: **cache the transcript, key it on the transcript-determining inputs
only — never on the rubric.** When a new requirement appears ("phase X does Y and
I hate it"), re-judge the *same cached baseline transcript* against the new check.
This is why "requirements change every run" does *not* make baselines useless.

## Personas and starting state

Two things are needed to test a mid-conversation phase, and they are separate:

- **Persona** — *who* the client is and *how* they answer. A phase-independent
  Markdown character file. One persona per person; swap files to test a different
  client or run contrarian cases. See [Personas](/docs/testing/eval-harness/personas).
- **Starting state** — the accumulated history/identities the phase's prompt
  assumes. Built per phase by driving a persona forward and freezing the result.
  See [Scenario Chain](/docs/testing/eval-harness/scenario-chain).

The persona is phase-independent; when phases change you re-freeze the scenario
snapshots, the persona stays the same.

## Where it runs

The harness needs **two** things at once: the local database **and** outbound
access to the OpenAI API.

- Running inside the **backend container** (`docker exec dev-coach-local-backend-1`)
  is the normal path — it reaches the DB directly and, when the stack has working
  outbound internet, reaches OpenAI too.
- If the container has lost outbound network (it can, e.g. a long-running/degraded
  stack), restart the stack, or run from the **host** against the dockerized DB's
  published port (`127.0.0.1:5432`).

Both invocations are in [Running Evals](/docs/testing/eval-harness/running-evals).

## Relationship to the Test Scenario system

The harness reuses the [Test Scenario system](/docs/testing/overview): the scenario
builder freezes a driven conversation into a `TestScenario` via the same
`freeze_user_session` path the admin UI uses, and evals can seed from those frozen
scenarios.

## Current status

- **Built:** the full loop (seed → drive → judge → report); persona files +
  loading; component-aware driving; phase-scoped prompt-version pinning; the
  `build_eval_scenario` chain builder (dry-run by default, opt-in freeze); seeding
  the eval directly from a frozen scenario (`--from-scenario`); rubrics derived
  live from the phase `Prompt.body` + per-phase targeted checks; replay mode
  (`--save-run` / `--replay`) to re-run the exact user turns against a new prompt;
  baseline↔candidate diffing (`run_coach_eval_diff`) with a pairwise judge; a
  `run_coach_eval` MCP tool (over `POST /api/v1/eval/run`) so evals run without
  shelling into Django.
- **Planned:** transcript caching, an MCP diff tool, and suites / k-run pass
  rates. See the [Roadmap](/docs/testing/eval-harness/roadmap).

## Related Documentation

- **[Personas](/docs/testing/eval-harness/personas)** — the simulated user
- **[Scenario Chain](/docs/testing/eval-harness/scenario-chain)** — per-phase starting states
- **[Running Evals](/docs/testing/eval-harness/running-evals)** — how to run
- **[Prompt Version Pinning](/docs/testing/eval-harness/prompt-versioning)** — before/after
- **[Roadmap](/docs/testing/eval-harness/roadmap)** — built vs planned
- **[Test Scenario System](/docs/testing/overview)** — seeding user state
