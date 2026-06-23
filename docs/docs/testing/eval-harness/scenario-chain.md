---
sidebar_position: 3
---

# Scenario Chain

To test a coaching phase, you need a user in the right **starting state** for that
phase. Most phases assume the accumulated state of the phases before them
(identities created, questions answered, `who_you_are` populated). You can't drop a
blank user into `identity_refinement` — the prompt has nothing to refine.

The `build_eval_scenario` command produces those starting states by driving a
[persona](/docs/testing/eval-harness/personas) forward through the Coach and
freezing the end-state as a `TestScenario`. Run it per phase boundary and you
rebuild the whole per-phase chain — the same idea as the hand-built
`Casey - * Testing` scenarios, but reproducible and attached to the automated
system.

## Why rebuild the chain

The hand-built scenarios still have valid *persona content*, but their action /
break / video plumbing has drifted as the system changed, so they can't be replayed
cleanly against the current pipeline. Regenerating them with the harness produces
scenarios that match today's flow.

## How it works

```
fresh user @ introduction
      │  drive persona (component-aware: clicks through the welcome video)
      ▼
coach transitions to get_to_know_you   ──(--freeze)──►  "[Auto] … @ get_to_know_you"
      │  (re-run with --stop-phase identity_warm_up)
      ▼
… and so on, one link per phase boundary
```

- Starts a **fresh user at `introduction`** (new users default to that phase) and
  seeds the welcome video.
- Drives the persona turn by turn, **clicking through gating components**
  (videos, breaks) by replaying their button actions — see
  [component-aware driving](/docs/testing/eval-harness/overview#component-aware-driving).
- Stops when the Coach transitions into `--stop-phase`.
- With `--freeze`, captures the end-state as a `TestScenario` via the same
  `freeze_user_session` path the admin UI uses.

## Freezing is opt-in

By default the command is a **dry run**: it drives the conversation and reports,
but saves nothing — so your existing scenarios are never touched.

| Invocation | Effect |
| --- | --- |
| `build_eval_scenario --persona casey` | Dry run. Drives the intro, reports, saves nothing. |
| `... --freeze --name "X"` | Saves the result as scenario "X". **Refuses if "X" already exists.** |
| `... --freeze --force --name "X"` | Replaces the existing "X". |

The two-step guard (`--freeze`, then `--force` to overwrite) is intentional: it
makes destroying or replacing a scenario a deliberate act, never a side effect of
running a test.

> Evals themselves **never freeze.** Freezing only happens here, with `--freeze`.
> Testing a phase loads a frozen scenario read-only.

## Flags

| Flag | Default | Purpose |
| --- | --- | --- |
| `--persona NAME` | `casey` | Persona file driving the user-bot. |
| `--stop-phase NAME` | `get_to_know_you` | Freeze once the Coach transitions into this phase. |
| `--name NAME` | generated label | Name for the frozen scenario. |
| `--freeze` | off | Actually save the result (otherwise dry run). |
| `--force` | off | Allow `--freeze` to overwrite an existing name. |
| `--coach-model NAME` | configured default | Override the coach model. |
| `--max-steps N` | `40` | Safety cap on driving steps. |
| `--description TEXT` | generated | Scenario description. |
| `--keep` | off | Keep the throwaway driving user. |

## Building the chain

Run once per boundary, freezing each link:

```bash
# Start of get_to_know_you
docker exec dev-coach-local-backend-1 \
  python manage.py build_eval_scenario --stop-phase get_to_know_you \
    --freeze --name "[Auto] Casey @ get_to_know_you"

# Start of identity_warm_up
docker exec dev-coach-local-backend-1 \
  python manage.py build_eval_scenario --stop-phase identity_warm_up \
    --freeze --name "[Auto] Casey @ identity_warm_up"
```

Each run currently drives from the introduction all the way to `--stop-phase`, so
later links take longer to build (the persona must converse through every prior
phase). Coaching-phase values are listed in `server/enums/coaching_phase.py`.

## The frozen scenario

A frozen scenario is a standard `TestScenario` (see
[Test Scenario System](/docs/testing/overview)) — its template holds the user,
coach state (at `--stop-phase`), identities, chat history, notes, actions, and
breaks. It shows up in the admin scenario list alongside hand-built ones, and can
be reset/instantiated like any other. The `[Auto]` name prefix marks it as
harness-generated.

## Related Documentation

- **[Personas](/docs/testing/eval-harness/personas)** — who is driven through
- **[Overview](/docs/testing/eval-harness/overview)** — component-aware driving
- **[Running Evals](/docs/testing/eval-harness/running-evals)** — running the commands
- **[Test Scenario System](/docs/testing/overview)** — what a frozen scenario is
