---
sidebar_position: 2
---

# Personas

A **persona** is who the simulated user (the "user-bot") *is* and *how* they
answer. It's a swappable Markdown file. The user-bot reads it as its system
prompt and then role-plays that person for the whole conversation.

Personas are deliberately **phase-independent**. A persona describes a *person*,
not a script of answers keyed to coaching phases — so when phases change, personas
don't. (The phase-specific *starting state* is handled separately by the
[Scenario Chain](/docs/testing/eval-harness/scenario-chain).)

## Why files, not scripts

Two rejected alternatives and why:

- **Scripting answers per phase/question** — brittle. When phases or questions
  change, every script breaks. A real client doesn't have "answers indexed by
  phase"; they have a life and answer whatever's asked from it.
- **Hardcoding the persona in code** — not swappable. Files let you point the
  user-bot at a different person, or a contrarian/edge-case persona, with a flag.

Reproducibility for before/after comparisons comes from
[replay mode](/docs/testing/eval-harness/roadmap) (reusing a baseline's exact user
turns), **not** from scripting the persona.

## File location and format

Persona files live in:

```
server/apps/coach/eval/personas/<persona_id>.md
```

The `<persona_id>` is the filename stem — that's what you pass to `--persona`.

Each file is YAML frontmatter + a Markdown body:

```markdown
---
persona_id: casey
name: Casey Schmid
description: Short summary of who this persona is.
source: Where the content was extracted from.
---

# Persona: Casey Schmid

You are role-playing **Casey Schmid**, a coaching CLIENT ... (instructions to the
user-bot, written in the second person) ...

## Background
...
## Values
...
## Goals
...
## Pain points
...
## How you communicate
...
## Ground-truth identities (stay consistent if these come up)
...
```

How it's loaded (`harness.load_persona`):

- The **frontmatter** is stripped; `name:` is read for display.
- The **Markdown body** becomes the user-bot's system prompt verbatim. So write the
  body as direct instructions to the user-bot ("You are role-playing… answer in the
  first person, one short message at a time, never break character…").

## Recommended sections

The body should cover, at minimum, the five basics plus voice:

| Section | What it anchors |
| --- | --- |
| **Background** | Life situation, history, work, family — the facts the client draws on. |
| **Values** | What matters to them; informs how they react. |
| **Goals** | What they want to become / get out of coaching. |
| **Pain points** | What they're struggling with — often the heart of the conversation. |
| **How you communicate** | Tone, length, formality — keeps replies in character. |
| **Ground-truth identities** | (Optional) the identities they've developed, so the bot stays consistent if a later phase references them. |

## The Casey persona

`casey.md` is the primary realistic persona, extracted from Casey Schmid's
hand-built per-phase test scenarios (the `Casey - * Testing` scenarios) in the
database — chat history, identities, who-you-are, and Sentinel notes. The scenario
plumbing in those old scenarios has drifted (actions/breaks/videos changed), but
the *persona content* is still valid, which is why it was extracted into a file.

## Adding a new persona

1. Create `server/apps/coach/eval/personas/<id>.md` with frontmatter + body.
2. Write the body as second-person instructions to the user-bot.
3. Use it: `--persona <id>`.

Ideas:

- **Other real clients** — the DB also has Leigh Ann, Leigh Orsi, and Jake
  scenarios that could be extracted the same way.
- **Contrarian / edge personas** — terse, skeptical, oversharing, evasive — to
  stress-test how the coach handles difficult clients.

## Using a persona

Both commands take `--persona`:

```bash
# Eval a phase as Casey
docker exec dev-coach-local-backend-1 \
  python manage.py run_coach_eval_spike --persona casey

# Build a scenario chain as Casey
docker exec dev-coach-local-backend-1 \
  python manage.py build_eval_scenario --persona casey
```

If the id doesn't match a file, the error lists the available personas.

## Related Documentation

- **[Overview](/docs/testing/eval-harness/overview)** — where personas fit
- **[Scenario Chain](/docs/testing/eval-harness/scenario-chain)** — starting state (separate from persona)
- **[Running Evals](/docs/testing/eval-harness/running-evals)** — the `--persona` flag
