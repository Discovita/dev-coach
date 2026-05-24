# Coaching Phase Videos — PR Coordination

**Spec:** [`notes/coaching-phase-videos.md`](./coaching-phase-videos.md)
**Feature flag:** `COACHING_PHASE_VIDEOS_ENABLED` (hardcoded boolean in `server/settings/common.py`, **Summer Program pattern**). Created in PR 1, flipped via code change in PR 22, optionally removed in PR 23 (default: keep as kill switch).
**Owner / coordinator:** Casey

## Approach (locked in)

**Handler-driven injection.** Session boundaries are detected by enriching two existing/new action handlers:

- **`transition_phase` handler** — when the LLM transitions, the handler consults the `SESSIONS` map:
  - If leaving session has an outro → attach the outro video component to the LLM's response message.
  - Else if entering session has an intro → attach the intro video component to the LLM's response message.
  - Else → just transition.
- **`END_BREAK` handler** — after closing the break, if `current_phase` is the first phase of a session whose intro is not in `shown_videos` → return the intro video component.

Welcome video is seeded in `ensure_initial_message_exists`. The video Continue button dispatches `{message: null, actions: [ACK, ...]}`; the break "I'm Ready" button dispatches `{message: "I'm ready", actions: [END_BREAK]}` (canned-response pattern).

**What this approach intentionally avoids vs. the prior plan:**
- No multi-message coach response shape — components ride along on the existing single-message-with-component pattern.
- No pre-LLM intro gate or post-LLM outro hook in `process_message` — handlers carry the logic.
- No `process_message` surgery beyond the null-message contract and skip-LLM-on-component rule (both lightweight).

## Codebase paths reference (verified 2026-05-24)

Treat this as the source of truth. Every `<coach>` / `<core>` / `<users>` placeholder in the PR sections below resolves to one of these. Patterns called out here are what new code mirrors.

**Backend layout**
- Django settings: `server/settings/common.py` (plus `local.py`, `staging.py`, `production.py`, `test.py`, `previews.py`)
- API router: `server/apps/api_urls.py` — `DefaultRouter` instances registered here, mounted by `server/urls.py` at `/api/v1/`
- Test runner: `pytest` via `server/pytest.ini`. Run as `pytest server/` from repo root, or `cd server && pytest`. **Note:** the homeschool-backend Summer Program tests use Django's test runner (`manage.py test ...`) — for dev-coach we follow the local convention and use pytest.

**Apps (`server/apps/<name>/`)**
- `coach/` — coach orchestration:
  - `functions/public/process_message.py` (orchestrator)
  - `utils/` — `apply_coach_response_actions.py`, `apply_user_component_actions.py`, `build_coach_prompt.py`, `build_coach_response_data.py`, `generate_coach_ai_response.py`, `get_recent_chat_messages_for_prompt.py`
  - `views/coach_view_set.py`, `views/admin_coach_view_set.py`
  - `serializers/coach_request_serializer.py`, `serializers/coach_response_serializer.py`, `serializers/admin_coach_request_serializer.py`
- `coach_states/` — `CoachState` model (`models/coach_state.py`), `admin/coach_state_admin.py`, `serializers/coach_state_serializer.py`, `migrations/`. **New `Break` model and `SESSION_VIDEOS` registry live in this app** (next to CoachState).
- `chat_messages/` — `ChatMessage` model (`models/chat_message.py`, includes `component_config` JSONField), `INITIAL_MESSAGE` constant at `constants/initial_messages.py`, `utils/ensure_initial_message_exists.py`, `utils/add_chat_message.py`
- `users/` — `UserViewSet` at `views/user_viewset.py` serves `/api/v1/user/me/*` (actions: `me`, `complete`, `coach-state`, …). `AdminTestUserViewSet` at `views/test_user_viewset.py` serves `/api/v1/admin/test-user/{pk}/*`. Serializers: `serializers/user_serializer.py` (full nested), `serializers/user_profile_serializer.py` (profile only)
- `core/` — `CoreViewSet` registered as `r"core"` in `api_urls.py`. **No `functions/` directory exists yet — PR 1 creates `apps/core/functions/__init__.py` and `apps/core/functions/public/__init__.py`.**
- `actions/` — `Action` model (audit log of action invocations). Action handlers themselves live in `services/action_handler/` (see below).
- `prompts/`, `identities/`, `reference_images/`, `test_scenario/`, `user_notes/`, `authentication/` — out of scope for this feature

**Services (`server/services/<name>/`)**
- `action_handler/` — all action handlers + dispatch:
  - State-mutation actions: `actions/<name>.py` (e.g., `transition_phase.py`, `accept_identity.py`, `create_identity.py`)
  - Component-returning actions: `actions/components/show_*.py`
  - Persistent-component-returning actions: `actions/persistent_components/persist_*.py`
  - Sentinel actions (not Action-logged): `actions/sentinel/*.py`
  - Param models (single file — append to it): `models/params.py`
  - Action handler dispatch + `ACTION_REGISTRY`: `handler.py`
  - Export aggregator: `actions/__init__.py`
  - Tests: `tests/test_*_action.py` (`test_transition_phase_action.py` exists — mirror its structure)
- `logger/`, `image_generation/` — out of scope

**Enums (`server/enums/`)**
- `action_type.py`, `component_type.py`, `coaching_phase.py`, `message_role.py`, `ai.py`, `identity_state.py`, `prompt_type.py`, `context_keys.py`, `identity_category.py`, `get_to_know_you_questions.py`

**Top-level models (`server/models/`)**
- `CoachChatResponse.py` — pydantic schema for the LLM's structured response. **New actions get added as optional fields here** so the LLM can emit them.
- `SentinelChatResponse.py` — similar for sentinel responses
- `components/ComponentConfig.py` — `ComponentConfig`, `ComponentButton`, `ComponentAction`, `ComponentIdentity` (mirror these when building new components)

**Action handler contract (mirror this exactly for new actions):**
```python
# services/action_handler/actions/<name>.py
def my_action(
    coach_state: CoachState,
    params: MyActionParams,
    coach_message: ChatMessage,
) -> Optional[ComponentConfig]:
    # 1. Mutate state on coach_state (call .save() if needed)
    # 2. Optionally build a ComponentConfig and return it (skip-LLM rule fires if so)
    # 3. Log to Action.objects.create(user=..., action_type=ActionType.<NAME>.value, parameters=params.model_dump(), result_summary=..., coach_message=coach_message)
    return component_config_or_None
```

**To register a new action, edit all 5 of these:**
1. `enums/action_type.py` — add the enum value
2. `services/action_handler/models/params.py` — append a `<Name>Params` pydantic class
3. `services/action_handler/actions/<name>.py` — implement the handler
4. `services/action_handler/actions/__init__.py` — add the import/export
5. `services/action_handler/handler.py` — add to `ACTION_REGISTRY` dict
6. `models/CoachChatResponse.py` — add an optional field so the LLM can emit it (only for LLM-callable actions; the three new video/break actions are user-button-only, so this step is **skipped** for them — they never appear in `CoachChatResponse`)

**To register a new component type:**
1. `enums/component_type.py` — add the enum value
2. `client/src/enums/componentType.ts` — mirror on the frontend
3. `client/src/pages/chat/components/coach-message-with-component/<Name>Component.tsx` — implement (mirror `IntroCannedResponseComponent.tsx`)
4. `client/src/pages/chat/components/coach-message-with-component/CoachMessageWithComponent.tsx` — add a `case` arm in the switch

**Coach response shape note:** the `on_break: bool` field is built into the response by `apps/coach/utils/build_coach_response_data.py` (call site that constructs the dict), **and** declared in `apps/coach/serializers/coach_response_serializer.py` (the DRF serializer). Both touchpoints are required.

**Skip-LLM rule wiring:** `apply_user_component_actions` lives in `apps/coach/utils/apply_user_component_actions.py` but the skip-LLM check happens in the orchestrator `apps/coach/functions/public/process_message.py` — modify the orchestrator to check whether the user-action call returned a `ComponentConfig`, and skip the `generate_coach_ai_response` call if so.

**Frontend layout (`client/src/`)**
- API clients: `api/*.ts` (camelCase — `coach.ts`, `user.ts`, `auth.ts`, …)
- Hooks: `hooks/use-*.ts` (kebab-case — `use-coach-state.ts`, `use-chat-messages.ts`, `use-profile.ts`)
- Chat page entry: `pages/chat/Chat.tsx`
- Chat children: `pages/chat/components/*.tsx` (`ChatInterface.tsx`, `ChatControls.tsx`, `ChatMessages.tsx`, `CoachMessage.tsx`, `UserMessage.tsx`)
- Component renderer (the registry): `pages/chat/components/coach-message-with-component/CoachMessageWithComponent.tsx` — a switch statement on `component_type`. Adding a new component type means adding a `case` arm here AND a sibling component file.
- Existing component implementations to mirror: `IntroCannedResponseComponent.tsx`, `CombineIdentitiesConfirmation.tsx`, `IAmStatementsSummaryComponent.tsx` (all in the same dir)
- Enum types: `enums/componentType.ts`, `enums/actionType.ts`, `enums/coachingPhase.ts`, …
- TS type definitions: `types/componentConfig.ts`, `types/coachRequest.ts`, …
- Test runner: `vitest` — `cd client && npm test` (which is `vitest run`). Test files are `*.test.tsx` colocated under `__tests__/` directories.
- **Composer / message input location:** not 100% confirmed at audit time. The composer-disable wiring goes wherever the chat input lives — likely `pages/chat/components/ChatControls.tsx` or `ChatInterface.tsx`. PR 15's first step is to identify the exact file and add the disable rule there.

## Workflow rules (strict)

1. **Strictly serial.** Each PR lands on `main` before the next one is started. No parallel work, no stacking.
2. **One branch per PR.** Use the branch name listed in the status table. Branch off of `main` (which always has the previous PR merged).
3. **Tests gate the push.** Every test listed under `Tests required to pass before push` must pass locally before the PR is opened.
4. **Full suites green every time.** `pytest server/` and `cd client && npm test` must both pass — no regressions.
5. **Update this doc as part of the PR.** When you claim a PR, edit the status table in the same branch. When the PR merges, the merge SHA + date go in the table.
6. **Discoveries log is mandatory.** Surprises, design clarifications, gotchas — append to the bottom so the next PR's author starts informed.

## How to claim a PR

1. Pick the next `[ ]` in the table (everything is serial; you only ever pick the next one).
2. Edit the row: status `[~]`, fill in your handle + ISO date.
3. Read the per-PR section in full + the linked spec section before coding.
4. Create the branch using the exact name in the `Branch` column.
5. Write the tests listed under `Tests required to pass before push`. Add more if you find gaps; record additions in `Discoveries`.
6. Open the PR against `main`. Update the table: status `[👀]` + PR link.
7. After merge: status `[✓]` + merge SHA + date.

## Status legend

- `[ ]` Not started
- `[~]` In progress — claim with handle + ISO date
- `[👀]` In review — PR open
- `[✓]` Merged
- `[⛔]` Blocked — explain in Notes

## Status table

| #   | Title                                                                       | Branch                                       | Status | Claim | PR  | Logical deps |
|-----|-----------------------------------------------------------------------------|----------------------------------------------|--------|-------|-----|--------------|
| 1   | Feature flag scaffold                                                       | `casey/cpv-01-feature-flag`                  | `[✓]`  | casey 2026-05-24 | [#89](https://github.com/Discovita/dev-coach/pull/89) merged `5e3919d` 2026-05-24 | — |
| 2   | SESSIONS map + helpers                                                      | `casey/cpv-02-sessions-map`                  | `[✓]`  | casey 2026-05-24 | [#90](https://github.com/Discovita/dev-coach/pull/90) merged `f97336b` 2026-05-24 | — |
| 3   | `CoachState.shown_videos` migration                                         | `casey/cpv-03-shown-videos-migration`        | `[👀]` | casey 2026-05-24 | [#91](https://github.com/Discovita/dev-coach/pull/91) | — |
| 4   | `Break` model + migration                                                   | `casey/cpv-04-break-model`                   | `[ ]`  | —     | —   | — |
| 5   | Video registry + new enum values                                            | `casey/cpv-05-video-registry-enums`          | `[ ]`  | —     | —   | 2 |
| 6   | `ACKNOWLEDGE_SESSION_VIDEO` handler                                         | `casey/cpv-06-ack-session-video-action`      | `[ ]`  | —     | —   | 3, 5 |
| 7   | `START_BREAK` handler                                                       | `casey/cpv-07-start-break-action`            | `[ ]`  | —     | —   | 4, 5 |
| 8   | `END_BREAK` handler (basic close)                                           | `casey/cpv-08-end-break-action`              | `[ ]`  | —     | —   | 4 |
| 9   | `on_break` API field                                                        | `casey/cpv-09-on-break-api-field`            | `[ ]`  | —     | —   | 4 |
| 10  | `process_message` null-message contract + skip-LLM-on-component rule        | `casey/cpv-10-null-message-contract`         | `[ ]`  | —     | —   | — |
| 11  | History serialization + count bump (LLM read shim)                          | `casey/cpv-11-history-serialization`         | `[ ]`  | —     | —   | 3, 4 |
| 12  | Welcome injection (flag-gated)                                              | `casey/cpv-12-welcome-injection`             | `[ ]`  | —     | —   | 1, 5 |
| 13  | `transition_phase` handler enrichment — outro/intro auto-emit (flag-gated)  | `casey/cpv-13-transition-phase-enrichment`   | `[ ]`  | —     | —   | 1, 2, 5 |
| 14  | `END_BREAK` handler enrichment — intro auto-emit (flag-gated)               | `casey/cpv-14-end-break-enrichment`          | `[ ]`  | —     | —   | 1, 2, 5, 8 |
| 15  | FE: `on_break` composer disable + read shape                                | `casey/cpv-15-fe-on-break-composer`          | `[ ]`  | —     | —   | 9 |
| 16  | FE: `SessionVideoCard` + modal shell                                        | `casey/cpv-16-fe-session-video-card`         | `[ ]`  | —     | —   | 5 |
| 17  | FE: video modal threshold gate + action dispatch                            | `casey/cpv-17-fe-session-video-modal-action` | `[ ]`  | —     | —   | 6, 7, 16 |
| 18  | FE: `SessionBreakComponent` + unacked-video composer rule                   | `casey/cpv-18-fe-session-break-composer`     | `[ ]`  | —     | —   | 8, 15, 17 |
| 19  | Rename `dev-coach/videos/` files to match session keys                      | `casey/cpv-19-rename-video-files`            | `[ ]`  | —     | —   | — |
| 20  | S3 upload + populate registry URLs                                          | `casey/cpv-20-s3-upload-registry-urls`       | `[ ]`  | —     | —   | 5, 19 |
| 21  | Docs update — phases, transition-phase, persistent-components, new actions  | `casey/cpv-21-docs-update`                   | `[ ]`  | —     | —   | 2, 5, 6, 7, 8, 13, 14 |
| 22  | Flip flag to `True` (one-line code change)                                  | `casey/cpv-22-flip-flag`                     | `[ ]`  | —     | —   | 12–14, 18, 20, 21 |
| 23  | Remove flag plumbing (OPTIONAL — default skip)                              | `casey/cpv-23-remove-flag-plumbing`          | `[ ]`  | —     | —   | 22 |
| 24  | Delete `INITIAL_MESSAGE` constant                                           | `casey/cpv-24-delete-initial-message`        | `[ ]`  | —     | —   | 23 |
| 25  | Procedure MCP doc — Add a Session Video                                     | n/a — Procedures MCP `create_document`       | `[ ]`  | —     | —   | 24 |

> The `Logical deps` column shows real code dependencies. Because the workflow is strictly serial, you'll always have all of them merged anyway — they're listed for sanity-checking the order, not for branching.

## Cross-cutting verification

Every code PR must satisfy these before push:

- ✅ All tests listed in the PR's `Tests required to pass before push` section pass locally
- ✅ Full backend test suite green (`pytest server/`)
- ✅ Full frontend test suite green (`cd client && npm test`)
- ✅ `python manage.py makemigrations --check --dry-run` clean (backend PRs)
- ✅ Type-check passes (`mypy` if configured; `tsc --noEmit` for frontend)
- ✅ Lint passes (`ruff` / `eslint`)
- ✅ No `console.log`, `print`, or debugger statements left behind
- ✅ Manual verification step (where listed) is performed and noted in the PR description
- ✅ This doc updated in the same branch (status row, plus any `Discoveries` entries)

---

## PR 1 — Feature flag scaffold

**Branch:** `casey/cpv-01-feature-flag`
**Pattern reference:** Copy the **Summer Program flag pattern** from `AlphaAnywhere/homeschool-backend` verbatim. Specifically:
- `homeschool-backend/server/settings/common.py:707` (hardcoded boolean + comment)
- `homeschool-backend/server/apps/core/functions/public/get_summer_program.py` (TypedDict + helper)
- `homeschool-backend/server/apps/core/views/summer_program_view_set.py` (public ViewSet)
- `homeschool-backend/server/apps/core/tests/test_get_summer_program.py` (helper tests)
- `homeschool-backend/server/apps/core/tests/test_summer_program_endpoint.py` (endpoint tests)

**Scope:** Add a `COACHING_PHASE_VIDEOS_ENABLED` flag as a **hardcoded boolean** in `server/settings/common.py` (not env-driven — flip via code change + deploy). Add a `get_coaching_phase_videos()` helper returning a TypedDict config. Expose it on a public ViewSet at `GET /api/v1/core/public/coaching-phase-videos/`. The endpoint always returns the full shape; `enabled` is the only field for now (shape can grow later if we expose tunables like the video Continue threshold).

**Files to create / touch:**
- `server/settings/common.py` — add the constant with a comment explaining the deploy-to-flip convention (mirror the wording from `common.py:703-706` in homeschool-backend)
- `server/apps/core/functions/__init__.py` — create directory + re-export `get_coaching_phase_videos`
- `server/apps/core/functions/public/__init__.py` — re-export
- `server/apps/core/functions/public/get_coaching_phase_videos.py` — new (mirror `get_summer_program.py`)
- `server/apps/core/views/__init__.py` — add export of the new ViewSet
- `server/apps/core/views/coaching_phase_videos_view_set.py` — new (mirror `summer_program_view_set.py`)
- `server/apps/api_urls.py` — register the new ViewSet on one of the existing routers (probably a new `public_router` since this is `AllowAny`, OR register directly on `default_router` with the path `r"core/public/coaching-phase-videos"`). Match the homeschool-backend convention: `router.register(r"core/public/coaching-phase-videos", CoachingPhaseVideosViewSet, basename="coaching-phase-videos")`. Mount the router in `urlpatterns` in the same file.
- `server/apps/core/tests/test_get_coaching_phase_videos.py` — new (mirror `test_get_summer_program.py`)
- `server/apps/core/tests/test_coaching_phase_videos_endpoint.py` — new (mirror `test_summer_program_endpoint.py`). **Use pytest** (dev-coach convention), not Django's test runner.

**Code skeleton** (copy-this-shape, change names):

```python
# server/settings/common.py
# -------------------------------------------------------------------------
# Coaching Phase Videos feature flag
# -------------------------------------------------------------------------
# Exposed to the frontend via GET /api/v1/core/public/coaching-phase-videos/
# so the UI can decide whether to expect / render video and break components.
#
# COACHING_PHASE_VIDEOS_ENABLED is the feature flag — flip it to control
# visibility without an env-var change. Flipping is a code change + deploy.
COACHING_PHASE_VIDEOS_ENABLED = False
```

```python
# server/apps/core/functions/public/get_coaching_phase_videos.py
from typing import TypedDict
from django.conf import settings


class CoachingPhaseVideosConfig(TypedDict):
    enabled: bool


def get_coaching_phase_videos() -> CoachingPhaseVideosConfig:
    """
    Return the Coaching Phase Videos config as a JSON-serializable dict.

    Always returns the full shape regardless of whether the feature is
    enabled — the frontend / backend decide what to render based on `enabled`.
    """
    return {
        "enabled": settings.COACHING_PHASE_VIDEOS_ENABLED,
    }
```

```python
# server/apps/core/views/coaching_phase_videos_view_set.py
import logging
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from apps.core.functions import get_coaching_phase_videos

log = logging.getLogger(__name__)


class CoachingPhaseVideosViewSet(viewsets.GenericViewSet):
    """
    Public Coaching Phase Videos config.

    Endpoints:
        GET /api/v1/core/public/coaching-phase-videos/ → list()
    """

    permission_classes = [AllowAny]

    def list(self, request: Request) -> Response:
        return Response(get_coaching_phase_videos(), status=status.HTTP_200_OK)
```

**Backend gating convention going forward (other PRs):** check the flag with `from django.conf import settings` and read `settings.COACHING_PHASE_VIDEOS_ENABLED` directly in app code (handlers, `ensure_initial_message_exists`, etc.). The helper function is for the endpoint contract; in-code gates use the setting directly. No `videos_enabled()` wrapper helper.

**Tests required to pass before push** (mirror Summer Program tests one-for-one):
- [ ] `test_get_coaching_phase_videos_returns_full_shape` — result keys == `{"enabled"}`
- [ ] `test_get_coaching_phase_videos_reflects_enabled_true` — `@override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)` → `enabled` is `True`
- [ ] `test_get_coaching_phase_videos_reflects_enabled_false` — `@override_settings(COACHING_PHASE_VIDEOS_ENABLED=False)` → `enabled` is `False`
- [ ] `test_get_coaching_phase_videos_returns_full_shape_even_when_disabled` — shape doesn't shrink based on flag
- [ ] `test_endpoint_returns_200` — `GET /api/v1/core/public/coaching-phase-videos/` returns 200
- [ ] `test_endpoint_accessible_without_authentication` — `self.client.logout()` then GET still returns 200 (matches `AllowAny`)
- [ ] `test_endpoint_response_has_expected_keys` — `set(response.data.keys()) == {"enabled"}`
- [ ] `test_endpoint_reflects_enabled_flag_when_on` — `@override_settings(COACHING_PHASE_VIDEOS_ENABLED=True)` → response `enabled` True
- [ ] `test_endpoint_reflects_enabled_flag_when_off` — `@override_settings(COACHING_PHASE_VIDEOS_ENABLED=False)` → response `enabled` False, full shape still returned
- [ ] `test_endpoint_post_not_allowed` — POST returns 405 (read-only)
- [ ] Full backend test suite green (no regressions)

**Manual verification:** `curl http://localhost:8000/api/v1/core/public/coaching-phase-videos/` returns `{"enabled": false}` without auth.

**Notes:**
- **Not env-driven.** The Summer Program flag is hardcoded; we follow that. No `os.environ.get(...)`, no `.env` line, no Render dashboard env var. Flipping the flag in PR 22 is a one-line code change + merge.
- **No frontend hook in this PR.** Backend handlers gate their own behavior on `settings.COACHING_PHASE_VIDEOS_ENABLED`, so when the flag is off the frontend never sees video/break components and renders normally. A frontend hook can be added later if there's a use case (e.g., showing a "video feature available" banner outside chat) — none today.
- **No removal planned in PR 23 by default.** Summer Program does not remove its flag plumbing; it's kept as a kill switch. We follow the same pattern (see PR 23 notes for the trade-off).

---

## PR 2 — SESSIONS map + helpers

**Branch:** `casey/cpv-02-sessions-map`
**Spec section:** Core design decision 1.
**Scope:** Add the `SESSIONS` dict and three helpers (`session_of`, `is_first_phase_of_session`, `is_last_phase_of_session`) to `server/enums/coaching_phase.py`. Pure data + functions, no behavior change anywhere else.
**Files likely touched:**
- `server/enums/coaching_phase.py`
- `server/enums/__tests__/test_coaching_phase.py` (new)

**Tests required to pass before push:**
- [ ] `test_sessions_map_covers_every_coaching_phase_exactly_once` — every `CoachingPhase` value appears in exactly one session's `phases` list
- [ ] `test_session_of_returns_correct_session` — parametrized over every phase
- [ ] `test_session_of_raises_for_unknown_phase`
- [ ] `test_is_first_phase_of_session_true_for_first_phase` — parametrized over every session
- [ ] `test_is_first_phase_of_session_false_for_non_first_phases` — parametrized
- [ ] `test_is_last_phase_of_session_true_for_last_phase` — parametrized
- [ ] `test_is_last_phase_of_session_false_for_non_last_phases` — parametrized
- [ ] `test_welcome_session_outro_is_none` — asymmetric session sanity
- [ ] `test_visualization_session_outro_is_none` — asymmetric session sanity
- [ ] `test_session_keys_all_end_with_underscore_session_suffix` — naming convention guard
- [ ] Full backend test suite green

**Manual verification:** none.

---

## PR 3 — `CoachState.shown_videos` migration

**Branch:** `casey/cpv-03-shown-videos-migration`
**Spec section:** Core design decision 3.
**Scope:** Add `shown_videos = ArrayField(CharField(max_length=255), default=list, blank=True)` to `CoachState`. Migration only — nothing reads or writes it yet.
**Files likely touched:**
- `server/apps/coach_states/models/coach_state.py` — add the field
- `server/apps/coach_states/serializers/coach_state_serializer.py` — verify the field appears in the serializer (pin explicitly if `fields = "__all__"` isn't in use)
- `server/apps/coach_states/migrations/00XX_coach_state_shown_videos.py` — generated via `python manage.py makemigrations coach_states`

**Tests required to pass before push:**
- [ ] `python manage.py makemigrations --check --dry-run` returns no pending migrations after the new one is added
- [ ] `python manage.py migrate` succeeds on a fresh DB
- [ ] `python manage.py migrate <app> <prev_migration>` rolls back cleanly
- [ ] `test_coach_state_shown_videos_defaults_to_empty_list` — new instance has `shown_videos == []`
- [ ] `test_coach_state_shown_videos_accepts_appended_strings` — can append and re-fetch
- [ ] `test_coach_state_serializer_includes_shown_videos` — exposed via API if the serializer auto-includes fields (verify or pin it explicitly)
- [ ] Full backend test suite green

**Manual verification:** none.

---

## PR 4 — `Break` model + migration

**Branch:** `casey/cpv-04-break-model`
**Spec section:** Core design decision 9.
**Scope:** New `Break` model with `user`, `started_at` (auto_now_add), `ended_at` (nullable), `triggered_by_session` (CharField), `coach_message` (nullable FK). Basic admin registration. Nothing creates rows yet. **App ownership decided: `Break` lives in the `coach_states` app** — it's a piece of coaching session state, lives next to `CoachState`, and shares migrations/admin conventions.
**Files likely touched:**
- `server/apps/coach_states/models/break.py` — new model file
- `server/apps/coach_states/models/__init__.py` — export `Break`
- `server/apps/coach_states/admin/break_admin.py` — new admin file (mirror `coach_state_admin.py`)
- `server/apps/coach_states/admin/__init__.py` — register the new admin
- `server/apps/coach_states/migrations/00XX_break.py` — generated via `python manage.py makemigrations coach_states`

**Tests required to pass before push:**
- [ ] `python manage.py makemigrations --check --dry-run` clean after migration added
- [ ] `python manage.py migrate` succeeds
- [ ] Rollback succeeds
- [ ] `test_break_model_create_with_required_fields` — happy path
- [ ] `test_break_started_at_auto_set` — `auto_now_add` populates it
- [ ] `test_break_ended_at_nullable` — can save with `ended_at=None`
- [ ] `test_break_user_relationship` — FK works in both directions
- [ ] `test_break_admin_list_view_loads` — basic smoke through Django test client as superuser
- [ ] Full backend test suite green

**Manual verification:** none.

---

## PR 5 — Video registry + new enum values

**Branch:** `casey/cpv-05-video-registry-enums`
**Spec section:** Core design decision 4 + "Net surface area" enum rows.
**Scope:** Add static `SESSION_VIDEOS = {video_key: {"name": ..., "url": ""}}` dict with all 12 keys derivable from the SESSIONS map. URLs blank — populated in PR 20. Add `ACKNOWLEDGE_SESSION_VIDEO`, `START_BREAK`, `END_BREAK` to `ActionType`. Add `SESSION_VIDEO`, `SESSION_BREAK` to `ComponentType`. Add a `get_video(key)` helper.
**Files likely touched:**
- `server/apps/coach_states/constants/__init__.py` (new directory + file)
- `server/apps/coach_states/constants/session_videos.py` (new) — registry + `get_video(key)` helper. **Locating the registry in `coach_states` keeps it next to the `shown_videos` field and the `Break` model.**
- `server/enums/action_type.py` — add `ACKNOWLEDGE_SESSION_VIDEO`, `START_BREAK`, `END_BREAK`
- `server/enums/component_type.py` — add `SESSION_VIDEO`, `SESSION_BREAK`
- `client/src/enums/actionType.ts` — mirror the three new action types (the frontend uses these when constructing `ComponentAction` objects on button clicks)
- `client/src/enums/componentType.ts` — mirror the two new component types
- `server/apps/core/views/core_view_set.py` (or wherever `CoreViewSet` lives — confirm via `apps/core/views/__init__.py`) — if there's an `/enums` endpoint exposing enum values, verify the new ones appear. If no such endpoint exists, skip this bullet.

**Tests required to pass before push:**
- [ ] `test_session_videos_has_intro_entry_for_every_session` — derived from SESSIONS map
- [ ] `test_session_videos_has_outro_entry_only_for_sessions_with_outro`
- [ ] `test_get_video_returns_dict_with_name_and_url`
- [ ] `test_get_video_raises_keyerror_on_unknown_key`
- [ ] `test_actiontype_has_acknowledge_session_video`
- [ ] `test_actiontype_has_start_break`
- [ ] `test_actiontype_has_end_break`
- [ ] `test_componenttype_has_session_video`
- [ ] `test_componenttype_has_session_break`
- [ ] `test_enums_endpoint_response_includes_new_action_types` — `/api/core/enums/` JSON contains them
- [ ] `test_enums_endpoint_response_includes_new_component_types`
- [ ] Full backend test suite green

**Manual verification:** none.

---

## PR 6 — `ACKNOWLEDGE_SESSION_VIDEO` handler

**Branch:** `casey/cpv-06-ack-session-video-action`
**Spec section:** Core design decision 7.
**Scope:** Action handler that appends a `video_key` to `coach_state.shown_videos`. Idempotent. Param model with `video_key: str`. **Validates `video_key` against the `SESSION_VIDEOS` registry — raises `ValidationError` on unknown key.** Registered in the action handler dispatch table. Note: this is a **user-button-only action** — it does NOT appear in `models/CoachChatResponse.py` (the LLM cannot emit it).
**Files likely touched:**
- `server/services/action_handler/actions/acknowledge_session_video.py` — new handler (mirror `transition_phase.py` for the signature + Action logging)
- `server/services/action_handler/models/params.py` — append `AcknowledgeSessionVideoParams(BaseModel)` with `video_key: str`
- `server/services/action_handler/actions/__init__.py` — export
- `server/services/action_handler/handler.py` — add to `ACTION_REGISTRY`
- `server/services/action_handler/tests/test_acknowledge_session_video_action.py` — new (mirror `test_transition_phase_action.py`)

**Tests required to pass before push:**
- [ ] `test_ack_appends_video_key_to_shown_videos`
- [ ] `test_ack_is_idempotent` — calling twice doesn't duplicate the key
- [ ] `test_ack_persists_to_db` — re-fetched CoachState reflects the change
- [ ] `test_ack_raises_validation_error_for_unknown_video_key` — locked in: validate against registry
- [ ] `test_ack_returns_no_component_config` — does not trigger skip-LLM rule by itself
- [ ] `test_ack_dispatchable_through_action_handler` — end-to-end via the action handler entrypoint
- [ ] Full backend test suite green

**Manual verification:** none.

---

## PR 7 — `START_BREAK` handler

**Branch:** `casey/cpv-07-start-break-action`
**Spec section:** Core design decision 7.
**Scope:** Creates a `Break` row with `triggered_by_session=session_key, coach_message=<id>` and returns a `SESSION_BREAK` `ComponentConfig` (with the "I'm Ready" button + `END_BREAK()` action baked in). Param model with `session_key: str`. **Hard rule: it must be impossible to start a new break while one is already open. If `Break.objects.filter(user=u, ended_at__isnull=True).exists()`, raise `ValidationError`. No silent reuse, no replace, no overlap.** User-button-only action — not added to `CoachChatResponse`.
**Files likely touched:**
- `server/services/action_handler/actions/persistent_components/start_break.py` — new handler. **Place in the `persistent_components/` subdir** because it returns a `ComponentConfig` (mirror `persist_combine_identities.py` for structure).
- `server/services/action_handler/models/params.py` — append `StartBreakParams(BaseModel)` with `session_key: str`
- `server/services/action_handler/actions/__init__.py` — export
- `server/services/action_handler/handler.py` — add to `ACTION_REGISTRY`
- `server/services/action_handler/tests/test_start_break_action.py` — new

**Tests required to pass before push:**
- [ ] `test_start_break_creates_break_row_with_correct_triggered_by_session`
- [ ] `test_start_break_returns_session_break_component_config` — has the right `component_type`, contains an "I'm Ready" button bound to `END_BREAK()`
- [ ] `test_start_break_links_break_to_coach_message_when_provided`
- [ ] `test_start_break_raises_validation_error_when_open_break_exists_for_user` — locked in: no overlap, ever
- [ ] `test_start_break_allowed_after_previous_break_closed` — once `ended_at` is stamped, a new break can be started
- [ ] `test_start_break_isolates_per_user` — user A's open break does not block user B from starting one
- [ ] `test_start_break_raises_for_unknown_session_key` — validate against SESSIONS map
- [ ] `test_start_break_returned_component_triggers_skip_llm_rule_via_apply_user_component_actions` — integration: confirms PR 10's rule fires when this is the user action
- [ ] Full backend test suite green

**Manual verification:** none.

**Notes:**
- The `session_key` is the session **being left**, not the user's current_phase session. Spec is explicit on this.

---

## PR 8 — `END_BREAK` handler (basic close)

**Branch:** `casey/cpv-08-end-break-action`
**Spec section:** Core design decision 7.
**Scope:** Zero-param handler that closes the user's single open `Break` (`ended_at__isnull=True`) by stamping `ended_at=now()`. Because PR 7 guarantees at most one open break per user, this can safely use `.get()` (or `.filter().first()` + null-check). **Intro-emission logic is added in PR 14** — this PR keeps the handler scope minimal. User-button-only action — not added to `CoachChatResponse`.
**Files likely touched:**
- `server/services/action_handler/actions/end_break.py` — new handler. **Place at the `actions/` top level (not under `persistent_components/`)** because in this PR it returns `None`. PR 14 will extend it to optionally return a `ComponentConfig` — at that point either leave it in place or move it to `persistent_components/` (your call when you do PR 14). Mirror `transition_phase.py` for shape.
- `server/services/action_handler/models/params.py` — append `EndBreakParams(BaseModel)` (zero fields, but the param class must exist for the dispatcher pattern)
- `server/services/action_handler/actions/__init__.py` — export
- `server/services/action_handler/handler.py` — add to `ACTION_REGISTRY`
- `server/services/action_handler/tests/test_end_break_action.py` — new

**Tests required to pass before push:**
- [ ] `test_end_break_stamps_ended_at_on_open_break`
- [ ] `test_end_break_no_op_when_no_open_break` — handle gracefully (no exception)
- [ ] `test_end_break_only_closes_current_users_break` — isolation between users
- [ ] `test_end_break_does_not_touch_already_closed_breaks`
- [ ] `test_end_break_returns_no_component_config_in_this_pr` — locks the split with PR 14
- [ ] Full backend test suite green

**Manual verification:** none.

---

## PR 9 — `on_break` API field

**Branch:** `casey/cpv-09-on-break-api-field`
**Spec section:** Core design decision 9.
**Scope:** Add `on_break: bool` to coach response serializer AND user-state endpoint (regular + admin test-user variants). Derived from `Break.objects.filter(user=u, ended_at__isnull=True).exists()`.
**Files likely touched:**
- `server/apps/coach/serializers/coach_response_serializer.py` — add `on_break = serializers.BooleanField(...)`
- `server/apps/coach/utils/build_coach_response_data.py` — include `on_break` in the returned dict (this is the actual call site; the serializer just validates the shape)
- `server/apps/users/views/user_viewset.py` — `me`, `complete`, and `coach-state` actions all expose user state. Add `on_break` to at least the `coach-state` and `complete` responses (the frontend reads it on initial chat load). Update `CoachStateSerializer` (`apps/coach_states/serializers/coach_state_serializer.py`) and/or `UserSerializer` (`apps/users/serializers/user_serializer.py`) accordingly — pick whichever already aggregates derived fields.
- `server/apps/users/views/test_user_viewset.py` — `AdminTestUserViewSet` mirror of the above for admin parity (`/api/v1/admin/test-user/{pk}/coach-state` and `/complete`)

**Tests required to pass before push:**
- [ ] `test_user_state_on_break_false_when_no_break_rows`
- [ ] `test_user_state_on_break_true_when_open_break_exists`
- [ ] `test_user_state_on_break_false_when_break_ended_at_set`
- [ ] `test_coach_response_includes_on_break_field`
- [ ] `test_admin_test_user_state_includes_on_break_field`
- [ ] `test_on_break_isolated_per_user` — user A's open break doesn't make user B `on_break`
- [ ] Full backend test suite green

**Manual verification:** none.

---

## PR 10 — `process_message` null-message contract + skip-LLM-on-component rule

**Branch:** `casey/cpv-10-null-message-contract`
**Spec section:** "process_message null-message contract" + Skip-LLM rule.
**Scope:** Two changes:
1. **Null-message contract.** Accept `message=None` programmatically — no user ChatMessage saved, user actions still apply. `message=""` continues to be treated as a real (empty) user message. Required for the video Continue button which dispatches `{message: null, actions: [...]}`.
2. **Skip-LLM-on-component rule.** If any user action returned a `component_config`, skip the LLM call this turn. Required for the `START_BREAK` → `SESSION_BREAK` flow and the `END_BREAK` → intro-video flow (added in PR 14).

**No intro-gate clause, no pre/post-LLM injection hooks** — those don't exist in this approach. The handlers in PRs 13 + 14 attach components directly to messages they produce.

**Files likely touched:**
- `server/apps/coach/functions/public/process_message.py` — orchestrator. Today it always calls `add_chat_message(user, message, MessageRole.USER)` and `generate_coach_ai_response`. Change: (a) skip the user-message save when `message is None`, (b) capture the return of `apply_user_component_actions` and skip `generate_coach_ai_response` if it returned a `ComponentConfig`. **Note:** `apply_user_component_actions` currently has no return path for ComponentConfig — modify `server/apps/coach/utils/apply_user_component_actions.py` to return `Optional[ComponentConfig]` (mirror the return contract of `apply_coach_response_actions`).
- `server/apps/coach/utils/apply_user_component_actions.py` — add return value plumbing
- `server/apps/coach/serializers/coach_request_serializer.py` — change `message` field to `Optional[str]` / `allow_null=True`
- `server/apps/coach/tests/test_process_message.py` — new or extended (check existing test layout under `apps/coach/tests/`)

**Tests required to pass before push:**
- [ ] `test_message_none_does_not_save_user_chatmessage`
- [ ] `test_message_none_still_applies_user_actions`
- [ ] `test_message_empty_string_saves_user_chatmessage_with_empty_content`
- [ ] `test_message_string_saves_user_chatmessage_with_content`
- [ ] `test_skip_llm_when_user_action_returns_component_config` — use a mock action that returns a config
- [ ] `test_llm_called_when_no_component_config_returned`
- [ ] `test_existing_process_message_flows_unchanged` — regression
- [ ] Full backend test suite green

**Manual verification:** none.

---

## PR 11 — History serialization + count bump (LLM read shim)

**Branch:** `casey/cpv-11-history-serialization`
**Spec section:** Core design decision 10.
**Scope:** Update `get_recent_chat_messages_for_prompt` to render `component_config` as bracketed narrative text using `shown_videos` and the `Break` table as sources of truth. Bump default `count` from 5 to 10. DB rows unchanged — only LLM-facing strings differ.
**Files likely touched:**
- `server/apps/coach/utils/get_recent_chat_messages_for_prompt.py` — modify the serialization
- `server/apps/coach/tests/test_get_recent_chat_messages_for_prompt.py` — new or extended (verify existing test location first)

**Tests required to pass before push:**
- [ ] `test_acked_session_video_serialized_as_bracketed_watched_text`
- [ ] `test_unacked_session_video_serialized_as_bracketed_not_watched_text`
- [ ] `test_closed_break_serialized_as_bracketed_returned_text`
- [ ] `test_open_break_serialized_as_bracketed_not_returned_text`
- [ ] `test_normal_text_messages_passed_through_unchanged`
- [ ] `test_coach_message_with_text_and_component_serialized_with_both` — verifies the new common case (LLM text + outro/intro card in same row)
- [ ] `test_default_count_is_10` (was 5)
- [ ] `test_explicit_count_override_still_works`
- [ ] `test_serialization_uses_video_name_from_registry`
- [ ] Full backend test suite green

**Manual verification:** none.

---

## PR 12 — Welcome injection (flag-gated)

**Branch:** `casey/cpv-12-welcome-injection`
**Spec section:** Core design decision 6.A.
**Scope:** Rewrite `ensure_initial_message_exists` so that when `settings.COACHING_PHASE_VIDEOS_ENABLED` is `True`, it seeds a coach message with `text=""` and a `SESSION_VIDEO(welcome_session_intro)` `component_config`. When flag is `False`, preserve today's behavior (seed `INITIAL_MESSAGE` text from `apps/chat_messages/constants/initial_messages.py`). Check the flag with `from django.conf import settings` — direct setting access, no wrapper helper. The `INITIAL_MESSAGE` constant stays — it's deleted in PR 24.
**Files likely touched:**
- `server/apps/chat_messages/utils/ensure_initial_message_exists.py` — the file to modify
- `server/apps/chat_messages/tests/test_ensure_initial_message_exists.py` — new or extended (verify existing test location first; `apps/chat_messages/tests/` should exist)

**Tests required to pass before push:**
- [ ] `test_flag_off_seeds_initial_message_text_only` (regression)
- [ ] `test_flag_on_seeds_session_video_welcome_card_with_empty_text`
- [ ] `test_flag_on_component_config_uses_welcome_session_intro_key`
- [ ] `test_idempotent_when_initial_message_already_exists` (either branch)
- [ ] Full backend test suite green

**Manual verification:** with flag off, create a new user — first message is "Hi I'm Leigh-Ann..." as today. With flag on, first message is the welcome video card with empty text.

---

## PR 13 — `transition_phase` handler enrichment — outro/intro auto-emit (flag-gated)

**Branch:** `casey/cpv-13-transition-phase-enrichment`
**Spec section:** Core design decisions 1 + 6.B/C (revised — handler-driven).
**Scope:** Modify the existing `transition_phase` action handler. After the phase transition runs, consult the `SESSIONS` map (using `session_of(old_phase)` and `session_of(new_phase)`):

1. **If `is_last_phase_of_session(old_phase)` AND the leaving session has an outro** → attach a `SESSION_VIDEO(outro_key)` component config to the coach message this turn. The Continue button on the outro card carries `[ACK(outro_key), START_BREAK(leaving_session_key)]`.
2. **Else if `is_first_phase_of_session(new_phase)` AND the entering session has an intro AND that intro is not in `shown_videos`** → attach a `SESSION_VIDEO(intro_key)` component config to the coach message this turn. The Continue button carries `[ACK(intro_key)]`.
3. **Else** → no component attached. Normal transition.

When `settings.COACHING_PHASE_VIDEOS_ENABLED` is `False`, this enrichment short-circuits — the handler behaves identically to today. Check the flag with `from django.conf import settings` — direct setting access, no wrapper helper. The transition itself is unchanged in both branches.

**Implementation note:** the handler ATTACHES the component to the coach message the LLM is producing this turn — it does not create a new message row. This is the existing message-with-component pattern. No multi-message response shape required.

**Files likely touched:**
- `server/services/action_handler/actions/transition_phase.py` — extend. Current signature: `transition_phase(coach_state, params: TransitionPhaseParams, coach_message: ChatMessage) -> None`. Change return type to `Optional[ComponentConfig]` and return the attached component when one applies. Note: the existing handler doesn't return anything — `apply_coach_actions` in `services/action_handler/handler.py` already handles `Optional[ComponentConfig]` returns from other handlers, so this fits the existing contract.
- `server/apps/coach_states/utils/session_video_helpers.py` — new module with the predicate helpers `should_emit_outro(old_phase) -> bool`, `outro_component_for(leaving_session) -> ComponentConfig`, `should_emit_intro(new_phase, shown_videos) -> bool`, `intro_component_for(entering_session) -> ComponentConfig`. **Place in `coach_states/utils/` because the logic reads the SESSIONS map (from `enums/coaching_phase.py`) and the `shown_videos` field on `CoachState`.** Reuse across PR 14.
- `server/services/action_handler/tests/test_transition_phase_action.py` — extend existing test file (already at this path — mirror its current structure)

**Tests required to pass before push:**
- [ ] `test_transition_phase_attaches_outro_when_leaving_session_has_outro` — parametrized over every session with an outro
- [ ] `test_transition_phase_outro_button_carries_ack_and_start_break_with_leaving_session_key`
- [ ] `test_transition_phase_attaches_intro_when_leaving_session_has_no_outro_and_entering_has_intro` — INTRODUCTION → GET_TO_KNOW_YOU case
- [ ] `test_transition_phase_intro_button_carries_only_ack_with_intro_key`
- [ ] `test_transition_phase_no_video_for_intra_session_transition` — e.g., GET_TO_KNOW_YOU → IDENTITY_WARMUP
- [ ] `test_transition_phase_no_intro_when_entering_session_intro_already_in_shown_videos` — idempotency
- [ ] `test_transition_phase_prefers_outro_over_intro_when_both_would_apply` — locks rule precedence
- [ ] `test_transition_phase_no_video_when_flag_off` — regression
- [ ] `test_transition_phase_phase_change_unchanged_in_both_flag_branches` — pure transition behavior preserved
- [ ] Integration: end-to-end LLM turn with `transition_phase` action → response coach message has both text and component_config
- [ ] Full backend test suite green

**Manual verification:** with a test user, force the LLM to emit `transition_phase` at a session boundary — expect the LLM's text + the outro card in the same response. Force a transition out of `welcome_session` → expect the LLM's text + the intro card for `get_to_know_session`.

---

## PR 14 — `END_BREAK` handler enrichment — intro auto-emit (flag-gated)

**Branch:** `casey/cpv-14-end-break-enrichment`
**Spec section:** Core design decisions 1 + 6.B (revised — handler-driven).
**Scope:** Extend the `END_BREAK` handler (built in PR 8) to also emit the next session's intro video when the user returns from a break.

After stamping `ended_at`:
1. Look up `session_of(coach_state.current_phase)`.
2. If `is_first_phase_of_session(current_phase)` AND that session has an intro AND the intro is not in `shown_videos` → return a `SESSION_VIDEO(intro_key)` `ComponentConfig`. The Continue button carries `[ACK(intro_key)]`.
3. Else → return nothing (basic close, same as PR 8).

This is what makes the post-break intro fire deterministically. The component return triggers PR 10's skip-LLM rule, so the LLM doesn't run this turn — the user must ack the intro first, then the LLM speaks in the new session on the next turn.

When `settings.COACHING_PHASE_VIDEOS_ENABLED` is `False`, this enrichment short-circuits — the handler behaves like PR 8. Check the flag with `from django.conf import settings` — direct setting access, no wrapper helper.

**Files likely touched:**
- `server/services/action_handler/actions/end_break.py` — extend. Change return type from `None` to `Optional[ComponentConfig]`. Use the shared helpers from PR 13.
- `server/apps/coach_states/utils/session_video_helpers.py` — already created in PR 13; reuse the intro helpers here
- `server/services/action_handler/tests/test_end_break_action.py` — extend
- **Optional consideration:** if `end_break.py` now returns a `ComponentConfig`, you may want to move the file to `services/action_handler/actions/persistent_components/end_break.py` for consistency with other component-returning actions. Not strictly required — the dispatcher doesn't care about file location.

**Tests required to pass before push:**
- [ ] `test_end_break_returns_intro_component_when_current_phase_is_session_first_phase_with_unacked_intro` — parametrized
- [ ] `test_end_break_intro_button_carries_only_ack_with_intro_key`
- [ ] `test_end_break_no_intro_when_intro_already_acked` — idempotency
- [ ] `test_end_break_no_intro_when_current_phase_is_not_first_phase_of_session` — edge case if break ever closes mid-session
- [ ] `test_end_break_no_intro_when_flag_off` — regression
- [ ] `test_end_break_still_closes_break_in_both_flag_branches` — core behavior preserved
- [ ] `test_end_break_returned_component_triggers_skip_llm_rule_via_apply_user_component_actions` — integration with PR 10
- [ ] Integration: full break-close cycle — user clicks "I'm Ready" → break closes → intro card returned → LLM does not run this turn
- [ ] Full backend test suite green

**Manual verification:** with a test user mid-break, click "I'm Ready" — expect the intro card for the new session as the next coach message, with no LLM text. ACK it on the following turn → expect the LLM's first message in the new session.

---

## PR 15 — FE: `on_break` composer disable + read shape

**Branch:** `casey/cpv-15-fe-on-break-composer`
**Spec section:** Core design decision 9 + composer disable rule.
**Scope:** Frontend reads `on_break: bool` from coach response + user-state endpoint. Composer is disabled when `on_break === true`. **No multi-message response handling needed** — the response shape is unchanged. The unacked-SESSION_VIDEO clause is added in PR 18.
**Files likely touched:**
- `client/src/hooks/use-coach-state.ts` — extend to expose `on_break` from the `/api/v1/user/me/coach-state` response (handles initial-load case)
- `client/src/hooks/use-chat-messages.ts` (or wherever the `process-message` POST is wrapped) — read `on_break` from the coach response after each turn
- `client/src/api/coach.ts` — update the response TS type to include `on_break: boolean`
- `client/src/types/` — verify a `CoachResponse` type lives here; update it if so
- **Composer location:** identify by grepping `client/src/pages/chat/components/` for the `<input>` or `<textarea>` used for chat input. Best candidates: `ChatControls.tsx` or `ChatInterface.tsx`. Wire the disabled prop to the `on_break` flag. **Record the actual file path in `Discoveries` when you find it** so the next agent doesn't have to re-discover.
- `client/src/pages/chat/components/__tests__/` — vitest tests colocated here

**Tests required to pass before push:**
- [ ] `useUserState exposes on_break`
- [ ] `Composer is disabled when on_break is true`
- [ ] `Composer is enabled when on_break is false`
- [ ] `Composer remains enabled when on_break field is missing` (graceful)
- [ ] `on_break from coach response updates composer state after a message turn`
- [ ] Full frontend test suite green

**Manual verification:** toggle `on_break` in test-user state → composer disables / re-enables. Run a full break flow (when the FE work in PRs 17/18 is in place) and confirm composer disables on `START_BREAK` and re-enables on `END_BREAK`.

---

## PR 16 — FE: `SessionVideoCard` + modal shell

**Branch:** `casey/cpv-16-fe-session-video-card`
**Spec section:** Core design decision 8 (card + modal shell only — no threshold gate, no action dispatch).
**Scope:** Build the visual shell. New React component for `SESSION_VIDEO`: thin card with video name + `[Watch]` / `[Watch Again]` button (label derives from `shownVideos.includes(video_key)`). Clicking opens a modal containing the `<video>` element. Modal closes on Esc or backdrop click — no actions fire on close. **No Continue button yet, no threshold logic, no action dispatch.** This PR is testable in browser by clicking through Watch → modal opens → modal closes.
**Files likely touched:**
- `client/src/pages/chat/components/coach-message-with-component/SessionVideoCard.tsx` — new (mirror `IntroCannedResponseComponent.tsx` for the wrapper shape; the card itself is custom)
- `client/src/pages/chat/components/coach-message-with-component/SessionVideoModal.tsx` — new, shell only
- `client/src/pages/chat/components/coach-message-with-component/CoachMessageWithComponent.tsx` — add a `case ComponentType.SESSION_VIDEO:` arm that renders `<SessionVideoCard ... />`. **This file IS the component registry** — there's no separate `registry.ts`.
- `client/src/types/componentConfig.ts` — extend the `ComponentConfig` type to include the SESSION_VIDEO shape (`video_key: string`, etc.). Check the existing type definitions before adding.
- `client/src/pages/chat/components/__tests__/SessionVideoCard.test.tsx` — new vitest tests (mirror `CoachMessageWithComponent.test.tsx` for setup)

**Tests required to pass before push:**
- [ ] `SessionVideoCard renders video name from registry`
- [ ] `SessionVideoCard renders Watch button when video_key not in shown_videos`
- [ ] `SessionVideoCard renders Watch Again button when video_key in shown_videos`
- [ ] `Card click opens the modal`
- [ ] `SessionVideoModal renders <video> element with src from registry`
- [ ] `Esc key closes the modal`
- [ ] `Backdrop click closes the modal`
- [ ] `Modal does NOT render a Continue button in this PR` (negative test — locks the split)
- [ ] `Modal close fires no API action` (negative test)
- [ ] `SESSION_VIDEO is registered in the component renderer registry`
- [ ] Full frontend test suite green

**Manual verification:** in `npm run dev:local`, force a SESSION_VIDEO card into chat (dev shortcut or hardcoded mock with a placeholder MP4 URL like Big Buck Bunny). Click Watch → modal opens with video playing → Esc → modal closes, card still showing Watch. Click Watch Again toggle by mocking `shownVideos`.

---

## PR 17 — FE: video modal threshold gate + action dispatch

**Branch:** `casey/cpv-17-fe-session-video-modal-action`
**Spec section:** Core design decision 8 (threshold-gated Continue) + 7 (action dispatch).
**Scope:** Add the Continue button to `SessionVideoModal` with threshold-disabled state (20s before end for videos > 30s; 50% for videos ≤ 30s). Wire bundled action dispatch on Continue click (ACK for intros; ACK + START_BREAK for outros, with the `session_key` carried by the card's `component_config`). Esc / backdrop close still fires no action. Watch Again modal still has no Continue button.
**Files likely touched:**
- `client/src/pages/chat/components/coach-message-with-component/SessionVideoModal.tsx` — add Continue + threshold + dispatch
- `client/src/hooks/use-video-threshold.ts` — new (kebab-case to match `use-*.ts` convention)
- `client/src/api/coach.ts` — ensure the process-message POST accepts `{ message: null, actions: [...] }` (the TS type should allow `message: string | null`)
- `client/src/types/coachRequest.ts` — update if needed for the null-message case
- `client/src/hooks/__tests__/use-video-threshold.test.ts` — new vitest unit test for the hook
- `client/src/pages/chat/components/__tests__/SessionVideoModal.test.tsx` — new vitest tests

**Tests required to pass before push:**
- [ ] `Continue button rendered for active (unacked) modal`
- [ ] `Continue button NOT rendered for Watch Again (acked) modal`
- [ ] `Continue button is disabled at start of video`
- [ ] `Continue button enables at 20s before end for videos > 30s` — simulate `timeupdate` events
- [ ] `Continue button enables at 50% for videos ≤ 30s` — simulate
- [ ] `Continue click for intro video dispatches {message: null, actions: [ACK(video_key)]}`
- [ ] `Continue click for outro video dispatches {message: null, actions: [ACK(video_key), START_BREAK(session_key)]}` with correct session_key from component_config
- [ ] `Continue click closes the modal`
- [ ] `Esc still closes modal without dispatching actions`
- [ ] `Backdrop click still closes modal without dispatching actions`
- [ ] `useVideoThreshold returns enabled when threshold reached` — unit test the hook in isolation
- [ ] `useVideoThreshold returns disabled before threshold` — unit test
- [ ] Full frontend test suite green

**Manual verification:** in browser with `COACHING_PHASE_VIDEOS_ENABLED=True` in local settings and a placeholder MP4 in the registry, walk through: Watch → modal opens → Continue disabled → scrub close to end (or wait) → Continue enables → click → modal closes → confirm API call fired with the correct actions.

---

## PR 18 — FE: `SessionBreakComponent` + unacked-video composer rule

**Branch:** `casey/cpv-18-fe-session-break-composer`
**Spec section:** Core design decisions 7 + 9 + composer disable rule.
**Scope:** New React component for `SESSION_BREAK` — renders "I'm Ready" button that dispatches `{message: "I'm ready", actions: [END_BREAK()]}` (canned-response pattern, same as `IntroCannedResponseComponent`). Extend composer-disable hook with the unacked-SESSION_VIDEO clause.
**Files likely touched:**
- `client/src/pages/chat/components/coach-message-with-component/SessionBreakComponent.tsx` — new (mirror `IntroCannedResponseComponent.tsx` exactly — it's the canned-response pattern)
- `client/src/pages/chat/components/coach-message-with-component/CoachMessageWithComponent.tsx` — add `case ComponentType.SESSION_BREAK:` arm
- **Composer file** (located in PR 15) — extend the disable rule to also fire when latest coach message is an unacked SESSION_VIDEO
- `client/src/hooks/use-composer-disabled.ts` — new hook centralizing the disable logic (recommended — keeps the rule in one place for testability)
- `client/src/hooks/__tests__/use-composer-disabled.test.ts` — new
- `client/src/pages/chat/components/__tests__/SessionBreakComponent.test.tsx` — new

**Tests required to pass before push:**
- [ ] `SessionBreakComponent renders I'm Ready button`
- [ ] `I'm Ready click dispatches {message: "I'm ready", actions: [END_BREAK()]}`
- [ ] `I'm Ready label becomes a real user ChatMessage` (integration via mock)
- [ ] `Composer disabled when latest coach message is SESSION_VIDEO and key not in shown_videos`
- [ ] `Composer enabled when latest SESSION_VIDEO is in shown_videos`
- [ ] `Composer disabled when on_break is true regardless of latest message type`
- [ ] `Composer enabled when on_break false and no unacked video card is latest`
- [ ] `Both rules combine correctly` — truth table coverage
- [ ] Full frontend test suite green

**Manual verification:** trigger the full break flow in browser — see break card, composer disabled, click I'm Ready, see "I'm ready" appear as user message, composer re-enable after intro card lands.

---

## PR 19 — Rename `dev-coach/videos/` files to match session keys

**Branch:** `casey/cpv-19-rename-video-files`
**Spec section:** "Sessions & videos" table.
**Scope:** Pure rename — bring filenames in `dev-coach/videos/` into line with the spec's table (e.g. `01-welcome-session-intro.mov`). No code changes unless something references a filename.
**Files likely touched:**
- `dev-coach/videos/*.mov` — rename via `git mv`
- Any upload script that hard-codes old names

**Tests required to pass before push:**
- [ ] All 12 files exist at the new paths listed in the spec's "Sessions & videos" table
- [ ] `grep -r "<old-filename>" --include='*.py' --include='*.ts' --include='*.tsx' --include='*.md' .` returns no hits for any renamed file (excluding this doc + the spec)
- [ ] Upload script (if any) updated to reference new names
- [ ] Full backend + frontend test suites green (sanity — should be unaffected)

**Manual verification:** none.

---

## PR 20 — S3 upload + populate registry URLs

**Branch:** `casey/cpv-20-s3-upload-registry-urls`
**Spec section:** Core design decision 5.
**Scope:** Upload all 12 video files to the project's S3 bucket (same pattern as user images — match key prefix convention used by `apps/reference_images/` or `apps/identities/` image storage). Populate `SESSION_VIDEOS[video_key]["url"]` with the resulting S3 URL for each entry.
**Files likely touched:**
- `server/apps/coach_states/constants/session_videos.py` — fill in URLs
- Upload script — one-off bash or Python script. Place at the repo root or under an existing `scripts/` directory if one exists. Reference the existing S3 upload pattern by grepping for `boto3` or `s3.upload_file` in `server/apps/reference_images/` — mirror that.

**Tests required to pass before push:**
- [ ] All 12 S3 URLs respond `200 OK` to `curl -I` (smoke)
- [ ] HTTP Range requests work — `curl -r 0-1024 <url>` returns `206 Partial Content`
- [ ] `test_session_videos_all_urls_non_empty` — backend test enforcing no blanks
- [ ] `test_session_videos_all_urls_are_https` — guard against accidental http
- [ ] `test_session_videos_all_urls_unique` — no copy-paste collisions
- [ ] Full backend test suite green

**Manual verification:** in browser, hit each S3 URL once to confirm playback (or scripted: `ffprobe` each URL).

---

## PR 21 — Docs update — phases, transition-phase, persistent-components, new actions

**Branch:** `casey/cpv-21-docs-update`
**Spec section:** all of them — this is the doc consolidation.
**Scope:** Update the dev-coach repo docs (`docs/docs/...`) to describe the new sessions / video / break framework. These docs sync into the Procedures MCP server, so the source of truth is the markdown in this repo. Single consolidated PR — easier to review the framework holistically than scatter doc edits across the implementation PRs.

**Files to edit:**
- `docs/docs/coach/phases.md` — add a "Sessions" section explaining that phases roll up into sessions via the `SESSIONS` map, and that session boundaries trigger intro/outro videos + breaks. Link to the per-action docs below.
- `docs/docs/core-systems/action-handler/actions/transition-phase.md` — add a "Session-boundary side effects" section documenting the outro/intro auto-emit rules (PR 13). Include the precedence rule (outro wins over intro when both would apply).
- `docs/docs/core-systems/component-renderer/persistent-components.md` — add entries for `SESSION_VIDEO` and `SESSION_BREAK`. Document the `SessionVideoCard` deviation from the no-buttons-on-history convention (Watch Again is allowed because it's frontend-only). Document `on_break` composer disable + unacked-video composer disable rules.
- `docs/docs/core-systems/component-renderer/overview.md` — mention the two new component types in the registry list.
- `docs/docs/core-systems/action-handler/overview.md` — mention the three new actions.

**Files to create:**
- `docs/docs/core-systems/action-handler/actions/acknowledge-session-video.md` — param model (`video_key: str`), idempotency, registry validation.
- `docs/docs/core-systems/action-handler/actions/start-break.md` — param model (`session_key: str`), `Break` row creation, returned component config, one-open-break-per-user invariant.
- `docs/docs/core-systems/action-handler/actions/end-break.md` — zero-param close + the intro auto-emit side effect (PR 14). Document that this is the post-break intro trigger.

**Tests required to pass before push:**
- [ ] All edited files pass any project-level markdown lint or link check (if configured)
- [ ] `grep -rn "SESSION_VIDEO\|SESSION_BREAK\|ACKNOWLEDGE_SESSION_VIDEO\|START_BREAK\|END_BREAK" docs/docs/` returns matches in the expected files (sanity)
- [ ] Cross-links resolve: every `[link](other-doc.md)` introduced in this PR points to an existing file
- [ ] If the doc sync to Procedures MCP runs in CI: confirm it succeeds and the new/edited docs appear in `mcp__procedures__browse(doc_type="system", category="dev-coach")` output post-merge

**Manual verification:** read each edited / new doc top-to-bottom. The framework should be derivable from the docs alone — i.e., a new engineer should be able to understand session boundaries, video triggers, and break flow without reading the spec.

**Notes:**
- This PR carries no code changes. It exists because the feature ships in PR 22 and the docs should describe the shipped behavior, not the prior architecture.
- The "Add a Session Video" procedure (PR 25) is separate — it lives in the Procedures MCP server, not in the repo.

---

## PR 22 — Flip flag to `True`

**Branch:** `casey/cpv-22-flip-flag`
**Spec section:** prerequisite for cleanup PRs.
**Scope:** **One-line code change** flipping `COACHING_PHASE_VIDEOS_ENABLED = False` → `True` in `server/settings/common.py`. This matches the Summer Program pattern — the flag is hardcoded in the settings file, so flipping it is a PR + merge + deploy, not an env-var change in the Render dashboard. Smoke test in staging (post-merge auto-deploy) before merging to prod (or before promoting the build to prod if staging/prod are separate deploys).
**Files likely touched:**
- `server/settings/common.py` — the one-line flip

**Verification required before marking complete:**
- [ ] PR merged with single-line diff: `COACHING_PHASE_VIDEOS_ENABLED = False` → `True`
- [ ] Staging auto-deploys the change; `GET /api/v1/core/public/coaching-phase-videos/` on staging returns `{"enabled": true}`
- [ ] Production deploys the change; `GET /api/v1/core/public/coaching-phase-videos/` on prod returns `{"enabled": true}`
- [ ] Staging smoke (manual):
  - [ ] Create a new test user → see welcome video card as first message
  - [ ] Walk through INTRODUCTION → first session boundary → see LLM transition message with intro card attached → ACK → LLM continues in new session
  - [ ] Walk to first outro boundary → see LLM transition message with outro card attached → ACK → break opens → composer disabled
  - [ ] Click "I'm Ready" → next session intro appears (no LLM text on that turn) → ACK → LLM continues in new session
  - [ ] Refresh mid-break → composer correctly remains disabled (via `on_break` on initial user-state load)
- [ ] Production smoke (manual, with a test account):
  - [ ] Same walkthrough as staging on a real user account
  - [ ] Existing pre-flip user chats still render correctly — historical messages don't crash
- [ ] Monitor error rates / logs for 24h after flip; no anomalies

**Notes:**
- This is the moment the feature goes live. Coordinate timing with Casey before flipping prod.

---

## PR 23 — Remove flag plumbing (OPTIONAL — see notes)

**Branch:** `casey/cpv-23-remove-flag-plumbing`
**Spec section:** cleanup (not in spec).

**Decision required before claiming this PR:** the Summer Program pattern we copied in PR 1 does **not** remove its flag after rollout — it stays in `settings/common.py` as a long-lived kill switch. Two options:

- **Option A — keep the flag (default, matches Summer Program exactly).** Skip this PR entirely. The flag stays at `True`, the endpoint stays public, the `if settings.COACHING_PHASE_VIDEOS_ENABLED:` branches stay. If videos ever break in prod, ops can flip the boolean to `False` and redeploy in minutes. Cost: a handful of dead-looking `if` branches and an endpoint that always returns `{"enabled": true}`.
- **Option B — remove the flag (clean cut).** Run this PR. Justified if we're confident we'll never want to disable the feature again. Delete the constant, the helper, the ViewSet, the URL route, the tests, and every `if settings.COACHING_PHASE_VIDEOS_ENABLED:` branch (collapsing to the on-branch). The `INITIAL_MESSAGE` constant (the off-branch in `ensure_initial_message_exists`) is then dead — PR 24 removes it.

**If running Option B (scope of this PR):**
- `server/settings/common.py` — delete the `COACHING_PHASE_VIDEOS_ENABLED` constant + comment
- `server/apps/core/functions/public/get_coaching_phase_videos.py` — delete
- `server/apps/core/functions/public/__init__.py` and `server/apps/core/functions/__init__.py` — drop the re-export (delete the file entirely if it becomes empty)
- `server/apps/core/views/coaching_phase_videos_view_set.py` — delete
- `server/apps/core/views/__init__.py` — drop the re-export
- `server/apps/api_urls.py` — drop the `core/public/coaching-phase-videos` route registration
- `server/apps/core/tests/test_get_coaching_phase_videos.py` — delete
- `server/apps/core/tests/test_coaching_phase_videos_endpoint.py` — delete
- `server/services/action_handler/actions/transition_phase.py` — collapse flag check, keep only the videos-on branch
- `server/services/action_handler/actions/end_break.py` (or `actions/persistent_components/end_break.py` if you moved it in PR 14) — collapse flag check
- `server/apps/chat_messages/utils/ensure_initial_message_exists.py` — collapse to on-branch
- `server/apps/coach_states/utils/session_video_helpers.py` — collapse flag check (if it grew one)

**Tests required to pass before push (Option B only):**
- [ ] `grep -rn "COACHING_PHASE_VIDEOS_ENABLED" .` returns no hits
- [ ] `grep -rn "get_coaching_phase_videos" .` returns no hits
- [ ] `grep -rn "coaching-phase-videos" .` returns no hits in URL config / route files
- [ ] Backend test suite green — all previously-flag-on tests now pass without conditional setup
- [ ] Frontend test suite green
- [ ] `GET /api/v1/core/public/coaching-phase-videos/` returns 404 (route removed) — verified via test or manual curl
- [ ] Manual smoke in staging — full flow still works identically to PR 22's smoke

**Manual verification:** repeat PR 22's staging smoke walkthrough — behavior must be identical. Confirm `GET /api/v1/core/public/coaching-phase-videos/` is gone.

**Recommendation:** default to **Option A** (skip this PR) unless we have a strong reason to remove the flag. Kill switches are cheap; rebuilding one under pressure is not.

---

## PR 24 — Delete `INITIAL_MESSAGE` constant

**Branch:** `casey/cpv-24-delete-initial-message`
**Spec section:** "Net surface area" — `ensure_initial_message_exists` rewrite says delete `INITIAL_MESSAGE`.
**Scope:** Pure dead-code cleanup. The constant has been unreachable since PR 12's on-branch became the only branch in PR 23. Delete the constant, any dead imports referencing it, and any tests that asserted on its content. Keep this PR minimal — one constant, its imports, any tests using it.
**Files likely touched:**
- `server/apps/chat_messages/constants/initial_messages.py` — delete `INITIAL_MESSAGE` (the file also exports `INITIAL_MESSAGE_OLD` — keep `INITIAL_MESSAGE_OLD` unless explicitly told otherwise, since the docstring notes it's "preserved for reference")
- `server/apps/chat_messages/constants/__init__.py` — drop the `INITIAL_MESSAGE` re-export and remove `"INITIAL_MESSAGE"` from `__all__`
- Any file with `from apps.chat_messages.constants import INITIAL_MESSAGE` — drop the import
- Any test using `INITIAL_MESSAGE` — delete the test (these only existed to assert the old welcome-text behavior)

**Tests required to pass before push:**
- [ ] `grep -rn "INITIAL_MESSAGE" server/` returns no hits
- [ ] Backend test suite green
- [ ] Frontend test suite green (should be unaffected)

**Manual verification:** none.

---

## PR 25 — Procedure MCP doc: Add a Session Video

**Branch:** none — Procedures MCP `create_document` call.
**Spec section:** "Reframe" + "Net surface area" — Procedure doc is a first-class deliverable.
**Scope:** Create a `procedure / dev-coach / coach / add-session-video` document in the Procedures MCP server. NOP-style walkthrough: how Leigh Ann or a developer adds, swaps, or removes a video given the architecture this branch shipped. Must demonstrate that zero code changes are needed for video swaps.

**Verification required before marking complete:**
- [ ] Doc created via `mcp__procedures__create_document` and retrievable via `mcp__procedures__get_documents` with the returned ID
- [ ] Doc appears under `mcp__procedures__browse(doc_type="procedure", category="dev-coach", subject="coach")`
- [ ] **Dry-run the procedure**: pick one existing video (e.g. `brainstorming_session_intro`), follow the doc step-by-step to swap its S3 URL to a test bucket URL, confirm:
  - [ ] No code changes were required (only registry edit + S3 upload)
  - [ ] The new video plays end-to-end for a test user
  - [ ] Roll back by re-running the procedure with the original URL
- [ ] Doc references the `SESSIONS` map and `SESSION_VIDEOS` registry by absolute path so future readers can find them
- [ ] Doc explicitly calls out the three-step procedure from the spec: upload to S3, edit `SESSIONS` map intro/outro key (if mapping changes), edit registry entry (`video_key → { name, url }`)
- [ ] Doc explicitly states "no prompt edits, no migrations, no enum updates, no frontend work" for the common case of swapping a video file
- [ ] Doc links to the in-repo system docs updated in PR 21 (transition-phase side effects, persistent-components entries, etc.) for the architecture context

**Manual verification:** dry-run as above.

---

## Discoveries

> Append-only log. Add entries with date + your handle + what you found. The next agent should read this top-to-bottom before starting work.

### 2026-05-24 — casey — PR 1

- **Endpoint URL has no trailing slash.** The dev-coach `default_router` is `DefaultRouter(trailing_slash=False)`, so the public endpoint is `GET /api/v1/core/public/coaching-phase-videos` (not `…/`). This diverges from the spec text — the spec was written with a trailing slash matching the Summer Program reference, but in homeschool-backend the router uses `trailing_slash=True`. Match this convention in any FE fetch later.
- **`pytest server/` from the repo root collects two pre-existing collection errors** (`apps/test_scenario/admin/test_scenario_admin.py` and `apps/test_scenario/models/test_scenario.py`) because they match `test_*.py` but aren't tests. The issue exists on `main` independently of this PR. Workaround when running the full suite: `pytest --ignore=apps/test_scenario/admin --ignore=apps/test_scenario/models --ignore=apps/test_scenario/views`. With those ignores, the full suite is 654 passing on this branch.
- **Tests must run inside the backend container.** Test settings (`settings.test`) point at `LOCAL_DB_HOST=db` (the Docker compose hostname). Use: `COMPOSE_PROJECT_NAME=dev-coach-local docker compose --profile local -f docker/docker-compose.yml -f docker/docker-compose.local.yml exec backend pytest <path>`.
- **`apps/core/functions/` did not exist before PR 1.** Created `__init__.py` for both `functions/` and `functions/public/`. The convention is to re-export from `apps.core.functions` (mirroring how `apps.core.views.__init__` aggregates).
- **No frontend hook added.** Per the PR spec, backend handlers gate their own behavior on `settings.COACHING_PHASE_VIDEOS_ENABLED`. The endpoint exists for future FE wiring (e.g., banner outside chat) but nothing consumes it yet.

### 2026-05-24 — casey — PR 3

- **Pre-existing pending migration on `actions.timestamp`.** `python manage.py makemigrations --check --dry-run` flags `actions/0009_alter_action_timestamp.py` as unmade. Confirmed on `main` independently of this PR. PR 3's `coach_states` portion is clean; the `actions` drift is unrelated and not fixed here.
- **`CoachStateSerializer` uses an explicit `fields` tuple** (not `fields = "__all__"`). New fields on `CoachState` must be added to that tuple manually or they won't appear over the API. Updated in this PR.
- **No serializer test file existed for `coach_states`.** Created `test_coach_state_serializer.py` to assert `shown_videos` is exposed. Future serializer-shape assertions for this app should land in the same file.
