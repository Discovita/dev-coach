# AGENTS.md

Orientation for coding agents working in this repository.

Everything here was verified against the code at the time of writing. Where this
file and a doc or comment disagree, prefer what the code says — and fix the
stale source. See [Known-stale sources](#known-stale-sources) for traps already
identified.

## What this is

A conversational identity-coaching product. A user talks to "the Coach" (an
LLM), and the conversation moves through a fixed sequence of coaching phases.
The LLM's replies are structured: alongside its message it emits **actions**
that mutate application state (create an identity, transition phase, and so on).

Two things follow from that, and they explain most of the architecture:

- The LLM's prompt is **assembled per-turn from the database**, not hardcoded.
- The LLM's output is **schema-constrained**, and what it is allowed to do
  varies by phase.

## Stack

**Backend** (`server/`) — Django 5.1.3 + Django REST Framework 3.15.2 on Python
3.11, Postgres, Celery 5.5.3 + Redis for async work, drf-spectacular for the
OpenAPI schema, SimpleJWT for auth. LLM providers: `openai`, `google-genai`.

**Frontend** (`client/`) — React 19 + Vite 6, TanStack Router (file-based) and
TanStack Query, Tailwind 4, Radix primitives, Zod. Node 22. Biome for lint and
format; Vitest + Testing Library for tests.

**Docs** (`docs/`) — a Docusaurus site. See [Documentation](#documentation).

## Repository layout

```
server/          Django backend
  apps/          One Django app per domain (see below)
  services/      Cross-app services: action_handler, ai, prompt_manager,
                 sentinel, image_generation, media, pdf, logger
  settings/      One module per environment
  enums/         Shared enums (TextChoices)
client/          React frontend
  src/api/       One module per backend resource
  src/hooks/     TanStack Query hooks
  src/routes/    File-based routes; routeTree.gen.ts is GENERATED
  src/enums/     TypeScript mirrors of server/enums
docs/            Docusaurus documentation site
docker/          Compose files (base + per-environment overrides)
scripts/         fresh-start.sh, upload_session_videos.py
```

Backend apps: `actions`, `authentication`, `chat_messages`, `coach`,
`coach_states`, `core`, `identities`, `meditations`, `prompts`,
`reference_images`, `test_scenario`, `user_notes`, `users`.

## Running it

Everything runs in Docker Compose. There are two profiles, and the commands
differ only by profile and project name.

**Local** — full stack including a Postgres container:

```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose --profile local \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.local.yml up --build -d
```

**Dev** — same code, no database container:

```sh
COMPOSE_PROJECT_NAME=dev-coach-dev \
  docker compose --profile dev \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.dev.yml up --build -d
```

Ports: backend `8000`, frontend `5173`, docs `5174`, Postgres `5432`, Redis
`6379`.

The `db` service is declared `profiles: ["local"]`, so **the dev profile has no
database container**. Note that `settings/development.py` reads the same
`LOCAL_DB_*` environment variables as `settings/local.py` — the difference
between the two environments is what those variables point at, not the settings
module. Under the dev profile they must resolve to a reachable remote host.

The backend container's command is `manage.py migrate && manage.py runserver`,
so **pending migrations are applied every time the backend starts**.

More commands: `docs/docs/development/common-commands.md`.

## Tests

**Backend — pytest, run inside the container.** `server/pytest.ini` sets
`DJANGO_SETTINGS_MODULE = settings.test`; you do not pass it yourself.

```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend pytest
```

Narrow to a path to run a subset, e.g. `pytest apps/coach/tests/`.

`settings/test.py` uses a separate Postgres database and defaults `LOCAL_DB_HOST`
to `db`, the compose service name — which is why the suite is run in-container.
It stubs the AWS SES environment variables so the suite imports without a `.env`,
uses the in-memory email backend, and forces Celery eager.

Shared fixtures and factory helpers live in `server/conftest.py`.

**Frontend — Vitest**, from `client/`:

```sh
npm run test     # vitest run
npm run check    # biome lint + format check
npm run build    # vite build, which also runs tsc
```

Tests are colocated in `__tests__/` directories next to their source.

## CI

`.github/workflows/client-ci.yml` runs `npm run check`, `npm run build`, and
`npm run test` on pull requests and on pushes to `main`. It is scoped to
`client/**`, so server- and docs-only changes do not trigger it.

Only Biome **errors** fail the build. There is an accepted backlog of Biome
*warnings* (mostly a11y and hook-deps); do not treat them as failures, and do not
mass-fix them as a side effect of unrelated work.

There is currently no CI workflow for the backend — the Python suite is not run
automatically on pull requests. Run it locally before shipping backend changes.

## Backend conventions

**Apps are structured by role, not by file type.** A typical app has `models/`,
`serializers/`, `views/`, `functions/`, `admin/`, `migrations/`, `tests/` — each
a package of small modules rather than one large file.

**Views are thin; logic lives in `functions/`.** ViewSets validate with a
serializer, delegate to a function, and serialize the result. Functions are
grouped by audience: `functions/public/` for authenticated-user endpoints,
`functions/admin/` where an app has admin-only behaviour. Follow this when
adding endpoints — `apps/coach/views/coach_view_set.py` is a clear example.

**Routing.** All routes are registered in `server/apps/api_urls.py` on
`DefaultRouter(trailing_slash=False)` — **no trailing slashes**. There are two
routers: regular viewsets at the root, and `admin_router` mounted under
`/admin/`. Everything is served under `/api/v1/`.

**Permissions.** `server/permissions/` holds the shared permission classes.
`IsAdminUser` there is the single source of truth for admin checks — it grants
access to `is_staff` **or** `is_superuser`. Use it instead of DRF's built-in
class (which only checks `is_staff`) or inline checks.

**Logging.** Use the project logger, not `logging.getLogger`:

```python
from services.logger import configure_logging
log = configure_logging(__name__, log_level="INFO")
```

This is used in ~90 modules across `apps/`.

**Enums** are Django `TextChoices` in `server/enums/`, with TypeScript mirrors in
`client/src/enums/`. Changing one side generally means changing the other.

**Migrations** are made inside the running container so the volume mount writes
the files back to the host:

```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend python manage.py makemigrations
```

## Frontend conventions

- **Biome**, configured in `client/biome.json`: **tab** indentation, **double**
  quotes, imports auto-organized. `src/routeTree.gen.ts` is generated and
  excluded — never hand-edit it.
- **Never use the `any` type.**
- **Server state goes through TanStack Query hooks** in `src/hooks/`, which call
  the modules in `src/api/`. Components should not fetch directly.
- **Authenticated requests go through `authFetch`** (`src/utils/authFetch.ts`),
  used by ~22 modules. Do not hand-roll `fetch` for authenticated endpoints.

## Core systems

Each has real documentation under `docs/docs/core-systems/` — read it before
changing behaviour. Briefly:

**Prompt Manager** (`services/prompt_manager/`) — assembles each turn's prompt.
Prompt bodies are rows in the `Prompt` table, selected by coaching phase, with
versioning: only one version per `(prompt_type, coaching_phase)` is active.
Bodies are templates rendered with `str.format(**context)`, so **literal braces
in a prompt body are a formatting hazard**. The assembled prompt is
`[System Context][User Notes][Template][Action Instructions][Recent Messages]`.

**Action Handler** (`services/action_handler/`) — `ACTION_REGISTRY` in
`handler.py` maps action types to handler functions; parameters are validated by
Pydantic models. Which actions the LLM may emit is constrained per-phase by the
prompt's `allowed_actions`. Two behaviours worth knowing: the apply loop does
**not** wrap individual handlers in try/except, so one raising handler aborts the
rest; and a small set of actions are user-button-only, deliberately kept out of
the LLM's response schema so they cannot be hallucinated.

**Sentinel** (`services/sentinel/`) — the memory system. A post-save signal on
`ChatMessage` triggers a Celery task that extracts durable user notes via a
separate LLM call using `SENTINEL`-type prompts. Its three note actions are not
available to the coaching LLM and are not written to the `Action` table.

**Coaching phases** — defined in `server/enums/coaching_phase.py`. Eleven values,
of which `SYSTEM_CONTEXT` is a meta-phase (it controls global system context, it
is not a phase a user occupies). The same file defines `SESSIONS`, which groups
phases into sessions for intro/outro video and break boundaries, plus the helpers
`session_of`, `is_first_phase_of_session`, `is_last_phase_of_session`.

**Test scenarios** — admin-only fixtures that snapshot a complete user session
(profile, coach state, identities, chat history, notes, actions) so coaching
situations can be replayed while iterating on prompts. See
`docs/docs/testing/overview.md`.

## Documentation

`docs/docs/` holds ~130 markdown files, and it is unusually complete — API
endpoints, database models, per-action pages, per-context-key pages, and
how-to guides under `docs/docs/how-to/`. **Check there before reverse-engineering
anything.**

The docs are also served over MCP: a separate server (repo:
`CD-Tech-Solutions-Inc/dev-coach-mcp`) indexes this directory for semantic
search, and exposes tools for reading prompts and running coach evals. If that
MCP server is connected, prefer searching it over grepping the docs by hand.

When you change behaviour, update the corresponding page under `docs/docs/`.

## Git conventions

Branches are `<type>/<kebab-case-description>` — e.g. `feat/invite-only-access`,
`fix/register-jwt-token-routes`, `chore/client-ci-workflow`. Older branches use a
`casey/<slug>` form; follow the current convention, not the old one.

Commits follow Conventional Commits. Both bare (`fix: ...`) and scoped
(`feat(coach): ...`) forms are in use; scoped is the more recent habit. Subject
in the imperative, no emojis, and explain the change rather than restating the
diff. `.cursor/rules/write-commit-messages.mdc` has the full guidance.

Pull requests are squash-merged, so a branch's commits will not appear in
`main`'s history individually. **Do not conclude a branch is unmerged just
because `git cherry` or `git log main..branch` shows commits** — compare file
contents, or check the merged PR list.

There is no pull request template in this repository.

## Traps

- **Adding an npm package does not reach the running container.** The frontend
  and docs services mask `node_modules` with an anonymous volume
  (`- /client/node_modules`), populated at image build. A host `npm install`
  is invisible to the container, and a plain `up --build` reuses the stale
  volume. Install inside the container, or rebuild with `--renew-anon-volumes`.
- **`copy_prompts_to_staging` and `copy_prompts_to_production` OVERWRITE the
  target.** They are `pg_dump`/`psql` table copies, not merges, and they treat
  the local database as the source of truth. Never run them against an
  unverified or freshly-seeded local database.
- **Feature flags fail closed and are independent of permissions.** Being an
  admin is not enough to see a flagged feature; if a surface is missing, check
  the flag before assuming a permissions bug.
- `server/db.sqlite3` exists in the tree but the project runs on Postgres in
  every environment.

## Known-stale sources

`.cursor/rules/` predates parts of the current setup. Two rules in
`project-rules.mdc` are **wrong** and should not be followed:

- It says to activate a virtualenv at `.venv` before every command. The project
  runs in Docker; the repo-root `.venv` is a leftover.
- It gives the test command as
  `python manage.py test ... --settings=server.settings.test`. Both halves are
  wrong: the suite runs under **pytest**, and the settings module is
  `settings.test` — `server.settings.test` does not exist.

`.cursor/rules/index.mdc` is still titled "Inbox Zero AI - Master Rule Index",
carried over from another project, and has duplicated frontmatter. The rules it
indexes are otherwise a useful map of the how-to guides.

Treat the rest of `.cursor/rules/` as helpful but verify against code before
relying on any specific command or path.
