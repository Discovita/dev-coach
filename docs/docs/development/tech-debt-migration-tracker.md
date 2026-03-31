# Tech Debt & Frontend Migration Tracker

This document tracks all identified tech debt items and the work needed to consolidate the two frontends (gold/dev-coach and purple/customer-facing) into a single frontend living in the dev-coach monorepo.

The work is broken into independent workstreams that can be tackled in logical order. Each workstream can be completed and merged on its own without depending on the others being done first — but the recommended order minimizes rework.

---

## Recommended Order of Operations

```
BACKEND (can be done in parallel with frontend workstreams 2-3):
  B1. Gut the AI service — remove dead code (standalone)
  B2. Clean up dead backend services & research code (standalone)
  B3. Fix backend API route inconsistencies (standalone)
  B4. Backend housekeeping — dual enums, missing INSTALLED_APPS, test gaps (standalone)

FRONTEND:
  F1. Refactor test scenario components to eliminate duplication (standalone, benefits from B3)
  F2. Reconcile shared code drift between the two frontends (standalone)
  F3. Port gold-only features into the purple frontend (depends on B3, F1, F2)
  F4. Move unified frontend into the dev-coach monorepo (depends on F3)
  F5. Cleanup & retire the standalone frontend repo (depends on F4)
```

---

# BACKEND WORKSTREAMS

---

## Workstream B1: Gut the AI Service

**Goal:** Replace the bloated, over-engineered AI service with a minimal service that only does what the app actually needs.

**Status:** Not started

**Problem:**
The AI service at `server/services/ai/` has **40 Python files** organized into a deeply nested hierarchy of mixins, factories, adapters, and plugins. The app uses exactly **two methods** from it: `create_messages()` and `create_structured_chat_completion()`. Everything else is dead weight.

**The entire call chain in production:**

```
generate_coach_ai_response.py  ──→  AIServiceFactory.create(model)
                                         │
sentinel.py  ──────────────────→  AIServiceFactory.create(model)
                                         │
                                         ▼
                                  OpenAIServicePlugin
                                    ├── .generate()     → create_messages() + create_structured_chat_completion()
                                    └── .call_sentinel() → create_messages() + create_structured_chat_completion()
```

That's it. Two callers. Two underlying OpenAI SDK calls. Wrapped in 40 files.

**Dead code to remove (never called from production code):**

| File/Module | What it is | Why it's dead |
|-------------|-----------|---------------|
| `anthropic_service.py` | Anthropic/Claude integration | Broken (helper commented out), hardcoded to `claude-2`, factory raises `NotImplementedError` for Anthropic |
| `core/chat/generic/` (3 files) | Generic chat completion mixin | Never called from outside the AI service |
| `core/chat/structured/streaming.py` | Structured streaming | Never called |
| `core/chat/structured/stream_with_final.py` | Stream with final response | Never called |
| `core/chat/structured/stream_completion.py` | Stream completion helper | Never called |
| `core/image/` (5 files) | DALL-E image generation mixin | Never called — image gen uses Gemini, not DALL-E |
| `scripts/generate_image.py` | Standalone GPT-5 image gen script | Dev experiment, not production code |
| `scripts/edit_image.py` | Standalone GPT-5 image edit script | Dev experiment, not production code |
| `models/image.py` | ImageModel, ImageSize enums for DALL-E | Only used by dead image mixin |
| `enums/` (4 files) | Duplicate AIModel, AIProvider, ModelFeatures | Duplicates `server/enums/ai.py` (see workstream B4) |
| `utils/image.py` | encode_image for API | Only used by messages mixin for image support, not called in production |
| `models/openai_compatibility.py` | NOT_GIVEN sentinel, NotGiven type, Stream type | Used by dead generic/streaming code; structured completion only needs NOT_GIVEN |

**What to keep (the ~5 files that actually matter):**

| What | Why |
|------|-----|
| `ai_service_factory.py` | Entry point for coach + sentinel |
| `base.py` | `AIService` ABC + `parse_response` / `parse_sentinel_response` / `extract_json_from_response` |
| `core/coach_plugin.py` (`OpenAIServicePlugin`) | The adapter that calls OpenAI |
| `core/messages/utils.py` (`create_messages`) | Builds the OpenAI message array |
| `core/chat/structured/structured_completion.py` | The actual `beta.chat.completions.parse` call |

**Bugs to fix during this work:**
- `OpenAIServicePlugin.generate()` has no `return` statement when `response_format` is not a Pydantic subclass — returns `None` silently
- Log typo: `"OenAI response"` should be `"OpenAI response"` (appears twice)

**Tasks:**
- [ ] Identify the minimal set of files/functions needed (listed above)
- [ ] Flatten the service — collapse the 40-file mixin hierarchy into a simple, direct service
- [ ] Remove all dead code (AnthropicService, generic chat, streaming, DALL-E, scripts, duplicate enums)
- [ ] Fix the missing return bug in `generate()`
- [ ] Fix log typos
- [ ] Verify coach chat still works end-to-end
- [ ] Verify sentinel still works

**Touches:** `server/services/ai/` only — no other code imports the dead pieces

---

## Workstream B2: Clean Up Dead Backend Services & Research Code

**Goal:** Remove experimental/research code and dead service directories that aren't used in production.

**Status:** Not started

**Problem:**
There are entire directories of experimental code sitting in the services tree that nothing imports.

**Dead code to remove:**

| Directory | Files | What it is | Evidence it's dead |
|-----------|-------|------------|-------------------|
| `services/gemini/` | 4 files | Standalone Gemini experiment scripts | Zero imports from anywhere in `server/`. The actual Gemini service used in production is at `services/image_generation/gemini_image_service.py` |
| `services/image_generation/research/gemini/` | 17 files | Research scripts for various image gen approaches (face swap, character views, portraits, etc.) | Zero imports from anywhere in `server/`. Names like `first.py`, `face_swap_final.py` confirm these are experiments |

**That's 21 files of dead experimental code.**

**Tasks:**
- [ ] Delete `services/gemini/` directory (4 files)
- [ ] Delete `services/image_generation/research/` directory (17 files)
- [ ] Verify image generation still works (the production `orchestration.py` + `gemini_image_service.py` are untouched)

**Touches:** `server/services/gemini/`, `server/services/image_generation/research/` — nothing depends on these

---

## Workstream B3: Fix Backend API Route Inconsistencies

**Goal:** All admin-only endpoints live under the `/api/v1/admin/` prefix with consistent naming.

**Status:** Not started

**Problem:**
`TestUserViewSet` and `TestScenarioViewSet` are registered on the default router but are admin-only operations. This breaks the convention established by `AdminCoachViewSet`, `AdminIdentityViewSet`, and `AdminIdentityImageChatViewSet`, which correctly live under `/api/v1/admin/`.

**Current state:**

| Endpoint | Router | Should be |
|----------|--------|-----------|
| `/api/v1/admin/coach/process-message-for-user` | Admin | Correct |
| `/api/v1/admin/identities/generate-image` | Admin | Correct |
| `/api/v1/admin/identities/update-identity` | Admin | Correct |
| `/api/v1/admin/identities/download-i-am-statements-pdf-for-user` | Admin | Correct |
| `/api/v1/admin/identity-image-chat/start` | Admin | Correct |
| `/api/v1/admin/identity-image-chat/continue` | Admin | Correct |
| `/api/v1/test-user/{id}/profile` | **Default** | Move to admin |
| `/api/v1/test-user/{id}/complete` | **Default** | Move to admin |
| `/api/v1/test-user/{id}/coach-state` | **Default** | Move to admin |
| `/api/v1/test-user/{id}/identities` | **Default** | Move to admin |
| `/api/v1/test-user/{id}/actions` | **Default** | Move to admin |
| `/api/v1/test-user/{id}/chat-messages` | **Default** | Move to admin |
| `/api/v1/test-scenarios/` | **Default** | Move to admin |
| `/api/v1/test-scenarios/{id}/reset` | **Default** | Move to admin |
| `/api/v1/test-scenarios/freeze-session` | **Default** | Move to admin |

**Naming decision needed:** The `test-user` prefix conflates "admin impersonation" with "test scenarios." Consider renaming:
- Option A: `/api/v1/admin/user/{id}/...` — treats it as generic admin user viewing (more flexible)
- Option B: `/api/v1/admin/test-user/{id}/...` — keeps the test-specific naming but at least puts it under admin

**Tasks:**
- [ ] Decide on naming convention (Option A vs B)
- [ ] Move `TestUserViewSet` to admin router in `api_urls.py`
- [ ] Move `TestScenarioViewSet` to admin router in `api_urls.py`
- [ ] Update all frontend API calls in **both** frontends (gold `client/src/api/testScenarioUser.ts` and purple `client/src/api/testScenarioUser.ts`)
- [ ] Update frontend constants in `constants/api.ts`
- [ ] Update any backend tests referencing old URLs
- [ ] Update API documentation

**Touches:** Backend (`server/apps/api_urls.py`, viewsets, tests), both frontends (API modules)

---

## Workstream B4: Backend Housekeeping — Dual Enums, Missing App Registration, Test Gaps

**Goal:** Fix structural issues in the backend that create confusion or risk.

**Status:** Not started

**Problem 1: Dual `AIModel` enum**

Two completely separate `AIModel` enums exist:
- `server/enums/ai.py` — `AIModel(models.TextChoices)` — the one used by the app (`generate_coach_ai_response.py`, `sentinel.py`, `coach_plugin.py`)
- `server/services/ai/openai_service/enums/ai_models.py` — `AIModel(Enum)` — used only internally by the OpenAI service code

These have overlapping but not identical model lists, different base classes, and different method signatures. If B1 (gutting the AI service) is done first, the duplicate in the openai_service will be deleted as part of that work. If not, consolidate to the one in `server/enums/ai.py`.

**Problem 2: `DEFAULT_TOKEN_LIMITS` dict is defined but never used**

In `server/enums/ai.py`, a `DEFAULT_TOKEN_LIMITS` dict is defined at module level but `AIModel.get_default_token_limit()` uses a hardcoded if/elif chain instead of looking up the dict. Either use the dict or remove it.

**Problem 3: `apps.core` not in `INSTALLED_APPS`**

`apps.core` has models (`ImageMixin`), serializers, middleware, and a viewset — but it is **not listed** in `INSTALLED_APPS` in `settings/common.py`. The viewset works because DRF doesn't require app registration for viewsets, but if `ImageMixin` is ever used as a concrete model or if signals are added, this will break silently.

**Problem 4: Test coverage gaps**

| Area | Status |
|------|--------|
| `apps.coach` (CoachService, process_message) | **No tests** — highest-risk gap, this is the core of the app |
| `services/ai/` | **No tests** |
| `services/prompt_manager/` | **No direct tests** (only covered indirectly via app tests that mock it) |
| `services/action_handler/` | **No direct tests** |
| `services/sentinel/` | **No tests** |
| `apps.actions` | Empty `tests/__init__.py` only |
| `apps.core` | Empty `tests/__init__.py` only |

**Tasks:**
- [ ] Remove or use `DEFAULT_TOKEN_LIMITS` dict in `enums/ai.py`
- [ ] Add `apps.core` to `INSTALLED_APPS` (or verify it's intentionally excluded and document why)
- [ ] Consolidate to a single `AIModel` enum (may be handled by B1)
- [ ] (Lower priority) Add test coverage for `apps.coach` and core services

**Touches:** `server/enums/ai.py`, `server/settings/common.py`, various test directories

---
---

# FRONTEND WORKSTREAMS

---

## Workstream F1: Refactor Test Scenario Frontend Components

**Goal:** Eliminate duplicated components and hooks by making regular components work in both "logged-in user" and "admin impersonating another user" contexts.

**Status:** Not started

**Problem:**
The test scenario feature required duplicating ~5 components and ~6 hooks because the regular versions hardcode their data source (query keys like `["user", "chatMessages"]` and endpoints like `/user/me/...`). The test versions use different query keys (`["testScenarioUser", userId, "..."]`) and different endpoints (`/test-user/{id}/...` or `/admin/...`).

**Duplicated components (delete after refactor):**

| Test version | Regular version it duplicates |
|-------------|------------------------------|
| `TestScenarioChatInterface` | `ChatInterface` |
| `TestScenarioChatControls` | `ChatControls` |
| `TestScenarioCoachStateVisualizer` | `CoachStateVisualizer` |
| `TestScenarioTabContent` | `TabContent` |
| `TestScenarioConversationResetter` | `ConversationResetter` |

**Duplicated hooks (merge into regular versions):**

| Test hook | Regular hook |
|-----------|-------------|
| `use-test-scenario-chat-messages` | `use-chat-messages` |
| `use-test-scenario-user-coach-state` | `use-coach-state` |
| `use-test-scenario-user-identities` | `use-identities` |
| `use-test-scenario-user-actions` | `use-actions` |
| `use-test-scenario-user-final-prompt` | `use-final-prompt` |
| `use-test-scenario-user` | `use-profile` |

**Approach:** Create a `UserTargetContext` that hooks read from internally. When a component tree is wrapped in `<UserTargetProvider targetUserId={id}>`, all hooks inside automatically switch to admin endpoints and scoped query keys. No prop threading needed.

**Hooks/components that stay unique (NOT duplicates):**
- `use-test-scenarios` — scenario list CRUD (its own resource)
- `use-freeze-test-scenario-session` — freeze action
- `TestScenarioTable`, `TestScenarioEditor`, all form components — scenario editing UI
- `TestScenarioSessionFreezer` — already shared between both contexts
- `DeleteTestScenarioDialog` — scenario-specific

**Known bug to fix during this work:**
`TestScenarioSessionFreezer` invalidates `["testScenarios"]` but `useTestScenarios` uses `["test-scenarios", "all"]` — cache key mismatch means the scenario list doesn't refresh after freezing.

**Tasks:**
- [ ] Create `UserTargetContext` and `UserTargetProvider`
- [ ] Refactor each regular hook to read from context and branch on `isImpersonating`
- [ ] Delete each duplicate test-scenario hook
- [ ] Update `TestChat.tsx` to wrap regular components in `UserTargetProvider` instead of using test-specific components
- [ ] Delete each duplicate test-scenario component
- [ ] Fix the query key mismatch bug in `TestScenarioSessionFreezer`
- [ ] Test that regular chat still works (no `UserTargetProvider` = normal behavior)
- [ ] Test that test scenario chat still works through the provider

**Touches:** Gold frontend only (but the refactored hooks are what get ported to purple later)

---

## Workstream F2: Reconcile Shared Code Drift

**Goal:** Identify and resolve differences in code that exists in both frontends so the migration is a clean swap, not a merge conflict nightmare.

**Status:** Not started

**Problem:**
Both frontends evolved independently. Files with the same name may have diverged in implementation even though they serve the same purpose.

**Areas to diff:**

- [ ] **Hooks** — Compare each shared hook implementation (use-auth, use-profile, use-coach-state, use-chat-messages, use-identities, use-core, use-prompts, use-user-appearance, use-reference-images, use-image-generation, use-download-i-am-pdf, use-final-prompt, use-previous, use-theme)
- [ ] **API modules** — Compare auth.ts, user.ts, coach.ts, identities.ts, imageGeneration.ts, userAppearance.ts, referenceImages.ts, core.ts, prompts.ts, testScenarios.ts, testScenarioUser.ts
- [ ] **Types** — Compare all 17 type files
- [ ] **Enums** — Compare all enum files including appearance sub-enums
- [ ] **Chat page components** — Compare bulletins, coach message components, ChatMessages, ChatInterface, ChatControls
- [ ] **Images page** — Compare image generation UI, appearance selectors, scene inputs
- [ ] **UI primitives** — Catalog which shadcn components exist in each; purple has extras (sheet, sidebar, skeleton, slider, switch, tooltip)
- [ ] **Utils** — Compare authFetch, MarkdownRenderer, componentConfig, getIdentityCategoryIcon, logger

**Cookie name decision:** Gold uses `discovita-*` cookies, purple uses `neovita-*`. Pick one and standardize. This affects backend CORS config too.

**Key structural differences that need a decision:**
- Gold uses React Router 7; purple uses TanStack Router (file-based). Purple's router is the one to keep.
- Gold uses ESLint; purple uses Biome. Pick one.
- Both use Tailwind 4 but with different design tokens / color palettes in their CSS.

**Tasks:**
- [ ] Run file-by-file diffs of all shared code
- [ ] For each difference, decide which version to keep (or merge)
- [ ] Decide on cookie naming convention
- [ ] Decide on linter (ESLint vs Biome)
- [ ] Reconcile Tailwind design tokens / theme

**Touches:** Both frontends

---

## Workstream F3: Port Gold-Only Features into Purple Frontend

**Goal:** The purple frontend has every feature that currently only exists in gold.

**Status:** Not started — depends on B3, F1, F2

**Features to port:**

- [ ] **Admin routing** — Add admin route gating to TanStack Router (pathless `_admin` layout that checks `is_staff`)
- [ ] **Admin layout + navbar** — Port or adapt for purple's sidebar-based layout
- [ ] **`use-is-admin` hook** — Copy (small)
- [ ] **`use-actions` hook** — Copy (small)
- [ ] **Test Scenarios page** (`/test`) — Port page, table (ag-grid), editor, all form components, all unique hooks. Add `ag-grid` dependency.
- [ ] **Coach State Visualizer** — Port (already deduplicated in workstream 2)
- [ ] **Prompts management page** (`/prompts`) — Port page + DeletePromptDialog + NewPromptForm
- [ ] **Demo page** (`/demo`) — Port if desired, or skip
- [ ] **SessionRestorer** — Compare with purple's session handling; port if missing
- [ ] **ConversationExporter** — Port component + `xmlExport.ts` utility, add `xmldom` dependency
- [ ] **ConversationResetter** — Verify purple has this; port if missing
- [ ] **Admin image generation API calls** — Add admin-specific endpoints to purple's `api/imageGeneration.ts`
- [ ] **Storybook + MSW** — Optional; port if desired. Lower priority.

**Tasks:**
- [ ] Add admin route infrastructure to TanStack Router
- [ ] Port each feature (see checklist above)
- [ ] Verify all regular user flows still work
- [ ] Verify all admin flows work
- [ ] Verify image generation flows work for both regular and admin paths

**Touches:** Purple frontend, possibly backend if any missed API adjustments

---

## Workstream F4: Move Unified Frontend into Dev-Coach Monorepo

**Goal:** The dev-coach monorepo's `client/` directory contains the unified frontend.

**Status:** Not started — depends on F3

**Tasks:**
- [ ] Replace `dev-coach/client/` contents with the unified purple frontend
- [ ] Update Docker configs (`docker-compose.yml`, Dockerfiles) if they reference client-specific paths or configs
- [ ] Update CI/CD pipelines for the new client structure
- [ ] Update any monorepo-level scripts that reference the client
- [ ] Update environment variable names if changed (cookie names, API URLs)
- [ ] Verify local dev environment works (docker compose up, hot reload, etc.)
- [ ] Verify staging deployment works
- [ ] Update the docs site if it references client code paths

**Touches:** Monorepo config, Docker, CI/CD, docs

---

## Workstream F5: Cleanup & Archive

**Goal:** Remove dead code and retire the standalone frontend repo.

**Status:** Not started — depends on F4

**Tasks:**
- [ ] Archive the standalone `frontend` repo (or mark deprecated)
- [ ] Remove any leftover gold-specific code that wasn't needed
- [ ] Clean up unused dependencies from `package.json`
- [ ] Verify nothing references the old frontend repo (deployment configs, docs, etc.)
- [ ] Update project README / onboarding docs

**Touches:** Repo management, documentation

---

## Open Questions

These need answers before or during the work above:

1. **Cookie naming:** `discovita-*` or `neovita-*`? Affects backend CORS + both frontends.
2. **Linter:** Keep ESLint (gold) or Biome (purple)?
3. **Admin user URL naming:** `/admin/user/{id}/...` (generic) or `/admin/test-user/{id}/...` (test-specific)?
4. **Demo page:** Worth porting or can it be dropped?
5. **Storybook:** Priority to port, or defer?
6. **Branding in landing page:** Purple landing says "NeoVita" — does that stay or change to Discovita?
