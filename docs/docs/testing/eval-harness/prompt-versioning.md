---
sidebar_position: 5
---

# Prompt Version Pinning

Every coaching phase can have many `Prompt` versions in the database. Normally the
Coach uses the **latest active** version for the user's current phase. Pinning lets
a caller force a **specific** version instead — which is what makes before/after eval
comparisons possible.

This is a general capability of the coach pipeline, not just the eval harness: any
caller of `process_message` can pin versions.

## Behavior

- **Default:** latest active prompt for every phase (unchanged from before).
- **Pinned:** a caller passes a `{phase → version}` map. A pin applies **only while
  the user is in that phase**. Phases not in the map keep using their latest active
  prompt.
- **Phase-scoped on purpose:** a single conversation can transition across several
  phases. Pinning `get_to_know_you` to v10 must not force v10 onto
  `identity_warm_up` after the conversation advances (v10 may not even exist there).
  The override is resolved against the user's *current* phase on every turn, so it
  cleanly stops applying once the phase changes.

## How it flows through the code

```
process_message(user, message, actions, model, prompt_versions={...})
        │   server/apps/coach/functions/public/process_message.py
        ▼
build_coach_prompt(user, model, prompt_versions={...})
        │   server/apps/coach/utils/build_coach_prompt.py
        │   reads CoachState.current_phase, looks up prompt_versions[current_phase]
        ▼
PromptManager.create_chat_prompt(user, model, version_override=<int|None>)
        │   server/services/prompt_manager/manager.py
        ▼
Prompt.objects.filter(coaching_phase=..., is_active=True)
              .filter(version=version_override)   # only when override is not None
              .order_by("-version").first()
```

- `prompt_versions` is `Optional[Dict[str, int]]` — keys are coaching-phase values
  (e.g. `"get_to_know_you"`), values are version numbers.
- `build_coach_prompt` resolves the pin for the *current* phase only and passes a
  single `version_override: int | None` down.
- `PromptManager.create_chat_prompt` already supported `version_override`; when set
  it adds a `version=` filter, otherwise it takes the newest active prompt.

## Using it from the eval harness

The spike command exposes a single phase's pin via `--prompt-version`:

```bash
... manage.py run_coach_eval_spike --prompt-version 10
```

Internally it builds `{<phase under test>: 10}` and threads it through
`process_message`. The pinned version is echoed in the run header and recorded in
the report as `prompt_version`, so a saved run records exactly what was tested.

## Using it programmatically

```python
from apps.coach.functions.public.process_message import process_message

# Pin get_to_know_you to v10; every other phase uses its latest active prompt.
ok, data, err = process_message(
    user,
    "I love designing things",
    None,
    model,
    prompt_versions={"get_to_know_you": 10},
)
```

Passing `prompt_versions=None` (the default) preserves the normal latest-active
behavior exactly.

## Tests

Behavior is covered by mocked unit tests (no DB/LLM needed):

- `server/services/prompt_manager/tests/test_manager.py` — `version_override`
  filters the prompt queryset.
- `server/apps/coach/tests/test_build_coach_prompt.py` — a pin for the current
  phase resolves to the right `version_override`; a pin for a *different* phase does
  not leak into the current phase.

## Related Documentation

- **[Running Evals](/docs/testing/eval-harness/running-evals)** — the `--prompt-version` flag in context
- **[Overview](/docs/testing/eval-harness/overview)** — why before/after needs version pinning
- **[Prompt Manager](/docs/core-systems/prompt-manager/overview)** — prompt assembly
- **[Prompt Model](/docs/database/models/prompt)** — versions, `is_active`, fields
