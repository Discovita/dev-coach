---
sidebar_position: 4
---

# Running Evals

This is the step-by-step guide to running an automated coach eval. It assumes no
prior context — follow it top to bottom.

For the concepts behind what you're running, see the
[Overview](/docs/testing/eval-harness/overview).

## Prerequisites

1. **The local stack is up** (Postgres especially). Start it the usual way if it
   isn't running:

   ```bash
   COMPOSE_PROJECT_NAME=dev-coach-local \
     docker compose --profile local \
     -f docker/docker-compose.yml \
     -f docker/docker-compose.local.yml up --build
   ```

2. **The backend container has outbound internet.** The harness calls OpenAI. The
   container normally has egress; if it has lost it (see
   [Troubleshooting](#troubleshooting)), restart the stack or use the host path
   below.

3. **`OPENAI_API_KEY` is set** in `server/.env` — the same key the Coach uses.

4. **The phase you're testing has an active prompt in the local DB.** The harness
   reads whatever prompt is currently active (that's the point). If you've been
   running the Coach locally, prompts are already seeded.

## Run an eval (recommended: in the container)

The simplest invocation runs inside the backend container, which reaches the DB
directly:

```bash
docker exec dev-coach-local-backend-1 \
  python manage.py run_coach_eval_spike --persona casey --max-turns 10
```

The command seeds a throwaway user at `get_to_know_you`, drives the conversation
(CLIENT = user-bot, COACH = the Coach), clicks through any video/break gates, then
prints an **EVAL REPORT** and a final `PASS` / `FAIL`. The throwaway user is
deleted on exit unless you pass `--keep`.

### Running from the host instead

If the container has no outbound network, run from the host against the dockerized
DB's published port:

```bash
cd server \
  && set -a && . ./.env && set +a \
  && export LOCAL_DB_HOST=127.0.0.1 \
  && DJANGO_SETTINGS_MODULE=settings.local \
     ../.venv/bin/python manage.py run_coach_eval_spike --persona casey
```

- `set -a && . ./.env && set +a` loads DB creds + `OPENAI_API_KEY`.
- `export LOCAL_DB_HOST=127.0.0.1` overrides the in-container DB host with the
  host-published port.

## `run_coach_eval_spike` flags

| Flag | Default | Purpose |
| --- | --- | --- |
| `--persona NAME` | `casey` | Persona file to drive the user-bot (filename stem in `apps/coach/eval/personas/`). See [Personas](/docs/testing/eval-harness/personas). |
| `--max-turns N` | `20` | Cap on steps before the run stops. The run also stops early when the phase transitions. |
| `--coach-model NAME` | configured `DEFAULT_AI_MODEL` (e.g. `gpt-5.4`) | Override the **coach** model under test. Any id from `server/enums/ai.py`. |
| `--prompt-version N` | latest active | Pin the phase-under-test prompt to a specific version. This is how you run before/after — see [Prompt Version Pinning](/docs/testing/eval-harness/prompt-versioning). The derived rubric uses this same version's body. |
| `--from-scenario NAME` | off (cold-seed) | Hydrate a frozen [TestScenario](/docs/testing/eval-harness/scenario-chain) by exact name (real prior history) and pick the eval up from that scenario's phase, instead of cold-seeding a fresh user at `get_to_know_you`. |
| `--check ASSERTION` | none | Add a one-off [targeted check](#rubric--targeted-checks) (repeatable), evaluated on top of the per-phase checks file. |
| `--save-run PATH` | off | Write the run (recorded user turns + full report) to a JSON artifact for later [`--replay`](#replay-a-run) or inspection. |
| `--replay PATH` | off | [Replay](#replay-a-run) the user turns from a saved artifact instead of generating new ones with the user-bot. |
| `--keep` | off | Keep the throwaway test user instead of deleting it. |

## Seeding from a frozen scenario

By default the spike cold-seeds a fresh user at `get_to_know_you` with no history.
`--from-scenario` instead instantiates a named [TestScenario](/docs/testing/eval-harness/scenario-chain)
— full hydration (chat history, identities, coach state, notes, actions, breaks)
— so the eval resumes from **real prior history**, exactly like opening that
scenario in the admin Test Scenario tools.

```bash
docker exec dev-coach-local-backend-1 \
  python manage.py run_coach_eval_spike \
    --from-scenario "[Auto] Casey @ get_to_know_you"
```

What changes when you seed from a scenario:

- **Start phase is the scenario's phase** — read from the hydrated coach state,
  not hard-coded. The version pin (`--prompt-version`) applies to that phase.
- **Prior history feeds the user-bot** so it continues the conversation naturally,
  and is given to the judge as **context only** — prior coach turns are *not*
  scored (they predate the phase under test).
- **Only new actions are reported** — actions baked into the scenario are excluded
  from the action log so you see just what the Coach did during this run.
- The throwaway user (a fresh copy of the scenario's user) is still deleted on
  exit unless `--keep` is passed; your saved scenario is never mutated.

Build these scenarios with the [scenario builder](/docs/testing/eval-harness/scenario-chain).
If the name doesn't exist, the command prints the available scenario names.

## Rubric & targeted checks

The judge scores the coach against **two** standards, reported separately.

**1. The derived rubric (quality).** There is no hand-written rubric. The judge is
handed the phase's own coach `Prompt.body` — the *same version the coach ran* (so
`--prompt-version` pins both) — and asked *"did the coach follow these
instructions?"* It derives the salient behavioral criteria from the body itself
and scores each. This means:

- The rubric **tracks the prompt automatically** — edit the prompt (or pin a
  different version) and the standard moves with it. Nothing to maintain in
  lockstep, and it works for **any phase**.
- Only the phase **`Prompt.body`** is used — the appended action/JSON mechanics,
  global system context, and chat history are deliberately excluded, so the judge
  evaluates coaching behavior, not output plumbing.

**2. Targeted checks.** Explicit, hand-authored pass/fail assertions — the "this
phase must do X / must never do Y" cases you care about, including things the
prompt may not spell out. They come from two places, merged:

- A per-phase file at `apps/coach/eval/checks/<phase>.md` — one check per line;
  blank lines and `#` comments ignored, a leading `-`/`*` bullet stripped.
- Any `--check "…"` flags (repeatable) for one-off cases.

```bash
docker exec dev-coach-local-backend-1 \
  python manage.py run_coach_eval_spike \
    --check "The coach addresses the client by name at least once"
```

Each check gets its own `passed` + `note`. Checks are reported as their **own
outcome** (`CHECKS: n/m passed`) — never folded into the quality score — so a
failed assertion is visible even when overall quality passes.

## Replay a run

Every eval drives a *fresh* conversation, so two runs differ both by whatever you
changed **and** by user-bot randomness. Replay removes the second variable: it
records one run's exact user turns and feeds them back verbatim, so a re-run
differs only by the prompt/model.

```bash
# 1. Record a run (note --save-run):
docker exec dev-coach-local-backend-1 \
  python manage.py run_coach_eval_spike --prompt-version 10 --save-run /tmp/v10.json

# 2. Replay those same turns against a new version:
docker exec dev-coach-local-backend-1 \
  python manage.py run_coach_eval_spike --replay /tmp/v10.json --prompt-version 11
```

- The artifact is the **full report plus the recorded `user_turns`** (and the
  transcript + seed). It's written for both successful and errored runs.
- On replay, the artifact's **persona, scenario seed, coach model, and prompt
  version are used as defaults** — pass the flags to override. The common case is
  overriding `--prompt-version` to test a new version on identical turns.
- Component gates (videos/breaks) are still clicked through dynamically; only the
  typed user turns are replayed. If the recorded turns run out before the phase
  transitions, the run stops (`[replay exhausted after N user turns]`).
- The coach is still a live LLM, so its *replies* can vary run-to-run — replay
  fixes the **user** side, not coach sampling. For a rigorous read, replay a few
  times or lean on the targeted checks (which are deterministic assertions).

## Before / after comparison

A change is only meaningful relative to a baseline. Use replay so the prompt is
the only variable:

1. **Baseline** against the old version, recording the turns:
   ```bash
   docker exec dev-coach-local-backend-1 \
     python manage.py run_coach_eval_spike --prompt-version 10 --save-run /tmp/v10.json
   ```
2. **Create the new prompt version** (e.g. via the `dev-coach-docs` MCP server's
   `create_new_coach_prompt` tool — it auto-assigns the next version).
3. **Candidate** — replay the *same* turns against the new version:
   ```bash
   docker exec dev-coach-local-backend-1 \
     python manage.py run_coach_eval_spike --replay /tmp/v10.json --prompt-version 11
   ```
4. **Compare the two reports** — quality score + per-criterion reasoning, targeted
   checks, and progression. (An automated baseline↔candidate *diff* command is the
   [next roadmap item](/docs/testing/eval-harness/roadmap).)

The version pin is **phase-scoped** (details:
[Prompt Version Pinning](/docs/testing/eval-harness/prompt-versioning)).

## Reading the report

```json
{
  "scenario": "get_to_know_you_spike",
  "persona": "casey",
  "coach_model": "gpt-5.4",
  "prompt_version": 6,
  "turns": 10,
  "quality": {
    "passed": true,
    "score": 5,
    "rubric_source": { "phase": "get_to_know_you", "prompt_version": 6, "pinned": false },
    "criteria": [ { "name": "Single Question Per Response", "passed": true, "note": "..." } ],
    "reasoning": "..."
  },
  "progression": {
    "start_phase": "get_to_know_you",
    "final_phase": "get_to_know_you",
    "transitioned": false,
    "reached_goal_phase": false
  },
  "targeted_checks": [
    { "check": "The coach never asks more than one question in a single message.", "passed": true, "note": "..." },
    { "check": "The coach addresses the client by name at least once", "passed": false, "note": "..." }
  ],
  "actions": [
    {
      "action": "update_asked_questions",
      "params": { "asked_question": "background_upbringing" },
      "summary": "Added question 'background_upbringing' to asked questions list"
    }
  ],
  "final_coach_state": {
    "current_phase": "get_to_know_you",
    "identity_focus": "passions_and_talents",
    "who_you_are": [],
    "asked_questions": ["background_upbringing", "family_structure"],
    "shown_videos": [], "on_break": false, "current_identity": null
  }
}
```

The report keeps **quality**, **targeted checks**, and **progression** as
separate, independent outcomes — they are never combined into one verdict:

- `quality` — the LLM-judge verdict against the [derived rubric](#rubric--targeted-checks)
  (overall pass, 1–5 score, per-criterion results, reasoning). `rubric_source`
  records which phase + prompt version the standard came from, and whether it was
  pinned. This is the coaching-quality call.
- `progression` — phase movement: whether the coach transitioned and whether it
  reached a goal phase. **Reported independently of quality** — a 5/5 conversation
  that didn't transition within the turn budget is a *non-transition*, not a
  failure. (Some phases legitimately run long; raise `--max-turns` if needed.)
- `targeted_checks` — one `passed` + `note` per [targeted check](#rubric--targeted-checks)
  (omitted entirely when none are defined). A failed check stands on its own and
  is **not** folded into the quality score.
- `actions` — every action the coach took that run, from the
  [Action table](/docs/database/models/action): e.g. which get-to-know-you
  questions it recorded (`update_asked_questions`), identity creates, phase
  transitions. This shows what the coach *did*, not just what it said.
- `final_coach_state` — a snapshot mirroring the admin Coach State viewer (phase,
  identity focus, who-you-are, asked questions, shown videos, current identity).

The run also prints terminal summary lines — `QUALITY: PASS (5/5, …)`,
`CHECKS: n/m passed` (when checks are defined), and `PROGRESSION:
get_to_know_you -> …` — so the outcomes are never conflated.

Per-turn, the live output also shows a `↳ actions: …` line whenever the coach
takes actions, so you can watch the coach state evolve as the conversation runs.

## Building scenarios (the chain)

To create the per-phase starting states the evals seed from, use the scenario
builder. It drives a persona from the introduction phase and (with `--freeze`)
saves the end-state as a `TestScenario`:

```bash
# Dry run — drive the intro, save nothing:
docker exec dev-coach-local-backend-1 \
  python manage.py build_eval_scenario --persona casey

# Save it as a scenario:
docker exec dev-coach-local-backend-1 \
  python manage.py build_eval_scenario --freeze --name "[Auto] Casey @ get_to_know_you"
```

Full details and the chain workflow: [Scenario Chain](/docs/testing/eval-harness/scenario-chain).

## Running the unit tests

The harness change also touched the coach prompt-building path. Those unit tests
are mocked (no LLM, no internet):

```bash
docker exec dev-coach-local-backend-1 \
  sh -c 'DJANGO_SETTINGS_MODULE=settings.test python -m pytest \
    services/prompt_manager/tests/test_manager.py \
    apps/coach/tests/test_build_coach_prompt.py \
    apps/coach/tests/test_process_message.py -q'
```

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `openai.APIConnectionError` / `Connection refused` to `:443` from the container | The backend container has lost outbound network. | Restart the local stack, or run from the host (above). |
| `could not translate host name "db"` | Host process using the in-container DB host. | Include `export LOCAL_DB_HOST=127.0.0.1` (host path only). |
| `127.0.0.1:5432 ... Can't assign requested address` | DB container not running, or a network-restricted shell. | Start the stack; run from a normal shell or `docker exec`. |
| `No prompt found for state <phase>` | No active prompt for that phase (or a pinned `--prompt-version` that doesn't exist). | Seed/activate a prompt, or pick a version that exists. |
| `Persona '<id>' not found` | No matching file in `apps/coach/eval/personas/`. | Check the available list printed in the error; use a valid stem. |
| `OPENAI_API_KEY environment variable is required` | `.env` not loaded (host path). | Include `set -a && . ./.env && set +a`. |

## Related Documentation

- **[Overview](/docs/testing/eval-harness/overview)** — architecture and concepts
- **[Personas](/docs/testing/eval-harness/personas)** — the `--persona` files
- **[Scenario Chain](/docs/testing/eval-harness/scenario-chain)** — building starting states
- **[Prompt Version Pinning](/docs/testing/eval-harness/prompt-versioning)** — `--prompt-version`
- **[Roadmap](/docs/testing/eval-harness/roadmap)** — planned capabilities
