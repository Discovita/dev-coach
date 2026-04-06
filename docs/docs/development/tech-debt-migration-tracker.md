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
  F1. Refactor test scenario components to eliminate duplication (standalone, benefits from B3) ✓ DONE
  F2. Reconcile shared code drift between the two frontends (standalone) ✓ DONE
  F3. Port gold-only features into the purple frontend (depends on B3, F1 ✓, F2 ✓)
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

**Status:** Partially complete

**Problem 1: Dual `AIModel` enum**

~~Two completely separate `AIModel` enums exist~~

**Resolved as part of B1.** The `server/services/ai/openai_service/enums/ai_models.py` file was deleted when the AI service was refactored. `openai_service.py` now imports from `enums.ai` exclusively.

**Problem 2: `DEFAULT_TOKEN_LIMITS` dict is defined but never used**

In `server/enums/ai.py`, a `DEFAULT_TOKEN_LIMITS` dict is defined at module level but `AIModel.get_default_token_limit()` uses a hardcoded if/elif chain instead of looking up the dict. Either use the dict or remove it.

**Resolved.** `get_default_token_limit()` now uses `DEFAULT_TOKEN_LIMITS.get(model_str, 1024)`. The if/elif chain was also incomplete — it was missing `gpt-4.1`, `o3`, and `o4-mini`.

**Problem 3: `apps.core` not in `INSTALLED_APPS`**

`apps.core` has models (`ImageMixin`), serializers, middleware, and a viewset — but it is **not listed** in `INSTALLED_APPS` in `settings/common.py`. The viewset works because DRF doesn't require app registration for viewsets, but if `ImageMixin` is ever used as a concrete model or if signals are added, this will break silently.

**Resolved.** `apps.core` added to `INSTALLED_APPS` in `settings/common.py`. No migrations needed — `ImageMixin` is abstract.

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
- [x] Remove or use `DEFAULT_TOKEN_LIMITS` dict in `enums/ai.py`
- [x] Add `apps.core` to `INSTALLED_APPS`
- [x] Consolidate to a single `AIModel` enum (resolved by B1)
- [ ] (Lower priority) Add test coverage for `apps.coach` and core services

**Touches:** `server/enums/ai.py`, `server/settings/common.py`, various test directories

---
---

# FRONTEND WORKSTREAMS

---

## Workstream F1: Refactor Test Scenario Frontend Components

**Goal:** Eliminate duplicated components and hooks by making regular components work in both "logged-in user" and "admin impersonating another user" contexts.

**Status:** Complete

**Problem:**
The test scenario feature required duplicating ~5 components and ~6 hooks because the regular versions hardcode their data source (query keys like `["user", "chatMessages"]` and endpoints like `/user/me/...`). The test versions use different query keys (`["testScenarioUser", userId, "..."]`) and different endpoints (`/test-user/{id}/...` or `/admin/...`).

**Duplicated components (deleted):**

| Test version | Regular version it duplicates |
|-------------|------------------------------|
| `TestScenarioChatInterface` | `ChatInterface` |
| `TestScenarioChatControls` | `ChatControls` |
| `TestScenarioCoachStateVisualizer` | `CoachStateVisualizer` |
| `TestScenarioTabContent` | `TabContent` |
| `TestScenarioConversationResetter` | `ConversationResetter` |

**Duplicated hooks (merged into regular versions):**

| Test hook | Regular hook |
|-----------|-------------|
| `use-test-scenario-chat-messages` | `use-chat-messages` |
| `use-test-scenario-user-coach-state` | `use-coach-state` |
| `use-test-scenario-user-actions` | `use-actions` |
| `use-test-scenario-user-final-prompt` | `use-final-prompt` |
| `use-test-scenario-user` | _(deleted — was unused)_ |

**Note:** `use-test-scenario-user-identities` was **not** merged. It is still used by the images page (`pages/images/`), which was outside the scope of this refactor. It can be unified when the images page is addressed.

**Approach:** Created a `UserTargetContext` (`context/UserTargetContext.ts`) and `UserTargetProvider` (`providers/UserTargetProvider.tsx`). The context provides `isImpersonating`, `targetUserId`, `scenarioId`, and a computed `queryKeyPrefix` (`["user"]` or `["testScenarioUser", userId]`). All refactored hooks call `useUserTarget()` to dynamically select query keys, query functions, and mutation behavior. `TestChat.tsx` wraps the standard `ChatInterface` and `CoachStateVisualizer` in `<UserTargetProvider>` instead of rendering separate test-specific component trees.

**Hooks/components that stay unique (NOT duplicates):**
- `use-test-scenarios` — scenario list CRUD (its own resource)
- `use-freeze-test-scenario-session` — freeze action
- `use-test-scenario-user-identities` — still used by images page (see note above)
- `TestScenarioTable`, `TestScenarioEditor`, all form components — scenario editing UI
- `TestScenarioSessionFreezer` — already shared between both contexts
- `DeleteTestScenarioDialog` — scenario-specific

**Known bug fixed:**
`TestScenarioSessionFreezer` was invalidating `["testScenarios"]` but `useTestScenarios` uses `["test-scenarios", "all"]`. Fixed to use the correct query key.

**Tasks:**
- [x] Create `UserTargetContext` and `UserTargetProvider`
- [x] Refactor each regular hook to read from context and branch on `isImpersonating`
- [x] Delete each duplicate test-scenario hook (5 deleted, 1 retained — see note)
- [x] Update `TestChat.tsx` to wrap regular components in `UserTargetProvider` instead of using test-specific components
- [x] Delete each duplicate test-scenario component (all 5 deleted)
- [x] Fix the query key mismatch bug in `TestScenarioSessionFreezer`
- [ ] Test that regular chat still works (no `UserTargetProvider` = normal behavior)
- [ ] Test that test scenario chat still works through the provider

**Result:** 9 files deleted (~1,240 lines removed), 2 files created (~95 lines), net reduction of ~880 lines. TypeScript compiles cleanly.

**Touches:** Gold frontend only (but the refactored hooks are what get ported to purple later)

---

## Workstream F2: Reconcile Shared Code Drift

**Goal:** Identify and resolve differences in code that exists in both frontends so the migration is a clean swap, not a merge conflict nightmare. Since Purple is the target frontend, "reconcile" means updating Purple to absorb the improvements from Gold without breaking Purple's architecture or design.

**Status:** Complete (quick wins done; deferred items move to F3)

**Problem:**
Both frontends evolved independently. A file-by-file comparison has been completed. Most shared code is identical or differs only cosmetically (`import` vs `import type`). The real drift falls into three categories: (1) Gold has admin/impersonation support that Purple lacks, (2) Gold has stricter typing in some areas, and (3) the two have different design systems by intention.

---

### Comparison Results: Files That Are Identical (No Work Needed)

These files are functionally identical across both frontends (some have trivial `import` vs `import type` style differences that don't affect behavior):

**Hooks:** `use-auth`, `use-download-i-am-pdf`, `use-previous`, `use-theme`, `use-prompts`
**API:** `coach.ts`, `prompts.ts`
**Types:** `componentConfig.ts`, `imageSizes.ts`, `testScenario.ts`, `userAppearance.ts`, `action.ts`\*, `auth.ts`\*, `coachRequest.ts`\*, `coachResponse.ts`\*, `coachState.ts`\*, `message.ts`\* (\* = import style only)
**Enums:** `actionType.ts`, `getToKnowYouQuestions.ts`, `identityCategory.ts`, `identityState.ts`, all `appearance/*` files (8 files)
**Utils:** `getIdentityCategoryIcon.ts`, `MarkdownRenderer.tsx`, `componentConfig.ts`
**Lib:** `logger.ts`, `utils.ts`
**Constants:** `icon-map.ts`

---

### Comparison Results: Files With Meaningful Differences

#### Types that need updating in Purple

| File | What's different | Action |
|------|-----------------|--------|
| `prompt.ts` | Gold adds `prompt_type: string` field on both `Prompt` and `PromptCreate`. Gold allows `coaching_phase: string \| null`. Purple has `coaching_phase: string` (required, non-null) and no `prompt_type`. | Update Purple to match Gold — these are backend contract fields |
| `sceneInputs.ts` | Gold: `clothing?`, `mood?`, `setting?` as `string \| null`. Purple: all three required `string`. | Update Purple — nullable/optional matches backend reality |
| `user.ts` | Gold: appearance fields typed as `string \| null`. Purple: typed as `Gender \| null`, `SkinTone \| null`, etc. | Keep Purple's stricter typing — it's better. Gold should adopt it. |
| `identity.ts` | Purple adds `UpdateIdentityRequest` (with `clothing?`, `mood?`, `setting?`). Same core `Identity` shape. | Keep Purple's addition — Gold lacks this type |
| `imageGeneration.ts` | Gold has `GenerateImageRequest`/`GenerateImageResponse` + optional `user_id` on chat requests (admin). Purple omits these. | Port Gold's admin types to Purple when adding admin features (F3) |
| `referenceImage.ts` | Gold has optional `user_id?: string` on `CreateReferenceImageRequest` (admin). | Port when adding admin features (F3) |
| `coreEnums.ts` | Gold-only. Typed response for `/core/enums/` API. | Port to Purple — improves type safety |

#### Enums that need updating in Purple

| File | What's different | Action |
|------|-----------------|--------|
| `coachingPhase.ts` | Gold includes `ANYTHING_MISSING = "anything_missing"` with display name and color. Purple omits it. | Add to Purple — this is a real backend phase |
| `componentType.ts` | Different member declaration order. Same values. | No action needed — order is irrelevant for string enums |

#### Hooks that need updating in Purple

| Hook | What's different | Action |
|------|-----------------|--------|
| `use-chat-messages` | Gold uses `UserTargetContext` for dynamic query keys/functions. Purple hardcodes `["user", "chatMessages"]`. | Port Gold's context-aware version to Purple (F3, after adding `UserTargetContext`) |
| `use-coach-state` | Same pattern — Gold is context-aware, Purple is hardcoded. | Port Gold version (F3) |
| `use-identities` | Same pattern. | Port Gold version (F3) |
| `use-final-prompt` | Same pattern (simpler — just query key prefix). | Port Gold version (F3) |
| `use-core` | Gold has typed `CoreEnumsResponse` generic. Purple infers. | Update Purple to use typed response |
| `use-profile` | Purple includes `isAdmin` on return value. Gold separates into `use-is-admin`. | Keep Purple's approach (cleaner — one fewer hook) |
| `use-image-generation` | Gold has legacy `generateIdentityImage` path, `UseImageGenerationOptions`, admin invalidation of `["testScenarioUser"]`. Purple is simpler (chat-based only). | Port Gold's admin support when adding admin features (F3). Decide if legacy generate path is still needed. |
| `use-reference-images` | Gold accepts optional `userId` param for admin; Purple always current user. | Port admin support (F3) |
| `use-user-appearance` | Gold accepts `userId` param, branches between user/test-user APIs. Purple always current user. | Port admin support (F3) |

#### API modules that need updating in Purple

| File | What's different | Action |
|------|-----------------|--------|
| `auth.ts` | Cookie names (`discovita-*` vs `neovita-*`). Purple has logging. | Decide on cookie name (see decision below). Keep Purple's logging. |
| `core.ts` | Gold has typed `CoreEnumsResponse` return. | Update Purple to use typed return |
| `identities.ts` | Gold has `adminUpdateIdentity` and richer error parsing. | Port admin function + error handling to Purple (F3) |
| `imageGeneration.ts` | Gold: `generateIdentityImage` (admin), `saveGeneratedImage` via JSON. Purple: `saveGeneratedImage` via FormData PATCH. Gold's chat endpoints branch on admin. | Port admin endpoints to Purple (F3). Investigate save mechanism discrepancy. |
| `referenceImages.ts` | Gold: optional `userId` param on list/create for admin. | Port admin support (F3) |
| `testScenarios.ts` | Gold supports `FormData` for create/update (file uploads). Purple is JSON-only. | Port FormData support to Purple (F3) |
| `testScenarioUser.ts` | Gold: `/test-user/...`. Purple: `/admin/test-user/...`. | Purple is correct (admin prefix). Gold needs updating (see B3). |
| `user.ts` | Gold has `fetchActions()`. Purple does not. | Port to Purple (F3, with `use-actions` hook) |
| `userAppearance.ts` | Gold has `getTestUserAppearance` / `updateTestUserAppearance`. | Port admin functions to Purple (F3) |

#### Utils with differences

| File | What's different | Action |
|------|-----------------|--------|
| `authFetch.ts` | Cookie names. Gold uses `console.log`; Purple uses structured logger. Both have suspect `process.env.NEXT_PUBLIC_ENV` (should be `import.meta.env` in Vite). | Decide on cookie name. Keep Purple's logging. Fix the `process.env` → `import.meta.env` in whichever version we keep. |
| Gold-only: `xmlExport.ts` | XML export utility for conversation download. | Port to Purple when adding ConversationExporter (F3) |
| Purple-only: `getArticle.ts` | Simple "a"/"an" grammar helper. | Keep in Purple |

#### Constants with differences

| File | What's different | Action |
|------|-----------------|--------|
| `api.ts` | Gold: `TEST_SCENARIOS = "/test-scenarios"`, `FREEZE_SESSION = "/test-scenarios/freeze-session"`. Purple: `"/admin/test-scenarios"`, `"/admin/test-scenarios/freeze-session"`. | Purple is correct (admin prefix). Gold needs updating (see B3). |

---

### CSS / Theme

The two frontends have **intentionally different** design systems. Purple is the target, so Purple's theme stays.

| Aspect | Gold | Purple |
|--------|------|--------|
| **Font** | Segoe UI system stack | Montserrat (Google Fonts) |
| **shadcn base color** | `neutral` | `zinc` |
| **Primary palette** | Gold scale (`gold-50` – `gold-950`) with warm paper background (`#e5e0d0`) | Purple/violet (`#591B89` primary) with white background |
| **Brand tokens** | None | `--nv-*` Neovita tokens, gradient utilities |
| **Heading styles** | `text-gold-700` for `h1`–`h6` | `font-family: inherit` on all headings |
| **Extra tokens** | `--shadow-gold-*`, `--color-error/success` | Chart colors, sidebar colors, accent, radius scale |
| **Plugin** | `tailwind-scrollbar` | None |
| **CSS entry file** | `index.css` | `styles.css` |

**Action:** No reconciliation needed — Purple's theme is the keeper. When porting components from Gold, strip gold-specific styling and adapt to Purple's design tokens.

---

### Shadcn UI Components

| Gold only | Purple only | Both |
|-----------|-------------|------|
| badge, card, command, dialog, dropdown-menu, multi-select, popover, tabs | sheet, sidebar, skeleton, slider, switch, tooltip | button, input, label, select, separator, sonner, textarea |

**Action:** When porting Gold features to Purple, install needed shadcn components in Purple via `npx shadcn@latest add <component>`. Gold's `multi-select` is custom (not official shadcn) — will need manual porting.

---

### Structural Differences (Already Decided)

| Aspect | Gold | Purple | Decision |
|--------|------|--------|----------|
| Router | React Router 7 (`react-router-dom`) | TanStack Router (file-based) | **Keep Purple** |
| Linter | ESLint (flat config) | Biome | **Keep Purple** |
| Storybook | Yes (+ MSW mocks) | No | **Defer** (low priority) |
| Testing | Playwright + Vitest browser | Vitest + jsdom + Testing Library | **Keep Purple** (evaluate later) |
| Dependencies | `ag-grid`, `axios`, `xmldom`, `msw` | `@tanstack/react-form`, `zod` | Port `ag-grid` + `xmldom` when needed (F3) |
| Admin routing | `useIsAdmin()` hook + conditional route tree in `App.tsx` | No admin routing — all auth routes are `_authenticated` | Add `_admin` pathless layout in TanStack Router (F3) |

---

### Decisions (Resolved)

1. **Cookie naming: `neovita-*`**. Purple is the customer-facing site and the target frontend. Its conventions take precedence. Gold will adopt `neovita-*` when the frontends merge. Backend CORS config will need updating at that point.

2. **`process.env.NEXT_PUBLIC_ENV` in `authFetch.ts`: dead code — delete it.** This is a copy-paste from another project (incept.school). `process.env.NEXT_PUBLIC_ENV` is a Next.js pattern and will never be truthy in a Vite app, so the `secure` flag and `domain=.incept.school` never execute. Purple's `auth.ts` already has the correct Vite approach (`import.meta.env.MODE === "production"` + `import.meta.env.VITE_COOKIE_DOMAIN`). The fix is to align `authFetch.ts`'s `setCookie` with that same pattern. Bonus: both `auth.ts` and `authFetch.ts` define their own `getCookie`/`setCookie` — consider deduplicating into a shared cookie utility.

3. **Legacy image generation: keep and port.** The direct `generateIdentityImage` endpoint is still used as an admin dev tool. Build functionality there first, test it, then build customer-facing versions. Port the legacy generate types, API functions, and hook support to Purple as part of F3.

---

### Tasks

**Quick wins (done):**
- [x] Add `ANYTHING_MISSING` phase to Purple's `coachingPhase.ts`
- [x] Update `prompt.ts` in Purple to add `prompt_type` field and make `coaching_phase` nullable
- [x] Update `sceneInputs.ts` in Purple to make fields optional/nullable
- [x] Port `coreEnums.ts` type to Purple and update `use-core` + `core.ts` API to use it
- [x] Fix `process.env.NEXT_PUBLIC_ENV` → `import.meta.env` in Purple's `authFetch.ts`
- [x] Cookie naming: `neovita-*` (already correct in Purple, no change needed)

**Remaining items moved to F3** — all deferred work (admin hooks, context-aware hooks, admin API functions, shadcn components, etc.) is now tracked in F3's task list.

**Touches:** Purple frontend.

---

## Workstream F3: Port Gold-Only Features into Purple Frontend

**Goal:** The purple frontend has every feature that currently only exists in gold.

**Status:** Phase 1 complete ✓. Phase 2+ not started.

---

### Phase 1: Foundation (must be done first) ✓

These are prerequisites for everything else — admin routing and the context system that makes hooks work for both regular users and admin impersonation.

- [x] **Frontend permissions module** — Created `permissions/isAdminUser.ts` that mirrors the backend's `IsAdminUser` permission class (`server/permissions/is_admin_user.py`). Checks `is_staff OR is_superuser`. Updated `useProfile` to use it for its `isAdmin` return value. Updated `useAuth` to use it for cache hydration. Fixes the bug where a superuser who isn't staff passed backend checks but was blocked on the frontend.
- [x] **Admin routing** — Added an `admin` layout route under `_authenticated` at `/admin` (not pathless — TanStack Router's generator conflicts when nesting pathless layouts under `_public`). Admin pages nest under this layout at `/admin/test`, `/admin/prompts`, `/admin/demo`. The layout guard checks `isAdmin` via `useProfile` and redirects non-admins to `/chat`.
- [x] **Admin layout + navbar** — Extended Purple's `AuthLayout` sidebar with a conditional admin nav section (Shield icon + "Admin" divider, lucide icons for Test/Prompts/Demo). Admin items only render when `isAdminUser(profile)` is true. Uses the same pill-button style as the main nav.
- [x] **`UserTargetContext` + `UserTargetProvider`** — Ported from Gold (`context/UserTargetContext.ts`, `providers/UserTargetProvider.tsx`). Hooks are not yet wired up to use `useUserTarget()` — that happens when admin pages are ported in Phase 2+.
- [x] **Install shadcn components** — Installed via `npx shadcn@latest add`: `badge`, `card`, `command`, `dialog`, `dropdown-menu`, `popover`, `tabs`. Ported Gold's custom `multi-select` component with styling adapted from gold theme to shadcn semantic CSS variables.

### Phase 2: Admin-Aware Hooks & API (builds on Phase 1) — Phase 2 complete ✓

Port the context-aware hooks and admin API functions so that ported pages have data to work with.

**Hooks ported/updated:**
- [x] **`use-chat-messages`** — Now context-aware via `useUserTarget()`. Dynamic query keys, conditional fetch (test-user vs user), conditional send (`sendTestScenarioMessage` when impersonating), scoped cache invalidation.
- [x] **`use-coach-state`** — Context-aware, branches between `fetchCoachState` and `fetchTestScenarioUserCoachState`.
- [x] **`use-identities`** — Context-aware, branches between `fetchIdentities` and `fetchTestScenarioUserIdentities`.
- [x] **`use-final-prompt`** — Context-aware via dynamic `queryKeyPrefix`.
- [x] **`use-actions`** — Created from scratch (ported from Gold). Context-aware with `fetchActions`/`fetchTestScenarioUserActions`. Also added `fetchActions()` to `api/user.ts`.
- [x] **`use-image-generation`** — Added legacy `generateIdentityImage` mutation (admin endpoint), `UseImageGenerationOptions` callback support, `getErrorMessage`/`getToastDuration` helpers, admin cache invalidation of `["testScenarioUser"]`.
- [x] **`use-reference-images`** — Added optional `userId` param. Query key now includes userId for cache isolation.
- [x] **`use-user-appearance`** — Now takes `userId: string | null`. Branches between current-user and test-user API calls. Updated `Account.tsx` call site to pass `profile?.id ?? null`.

**API modules updated:**
- [x] **`testScenarioUser.ts`** — Created (new file). All admin test-user API functions: profile, complete, coach-state, identities, actions, chat-messages.
- [x] **`user.ts`** — Added `fetchActions()` function.
- [x] **`identities.ts`** — Added `adminUpdateIdentity()` function with admin endpoint.
- [x] **`imageGeneration.ts`** — Added `generateIdentityImage()` (admin legacy), admin-branching on `startImageChat`/`continueImageChat` (uses admin endpoint when `user_id` provided). Kept Purple's `saveGeneratedImage` (FormData PATCH to identity upload-image endpoint) — Gold's JSON POST approach targets a different admin endpoint; both are available.
- [x] **`referenceImages.ts`** — Added optional `userId` param on `listReferenceImages` (query string) and `createReferenceImage` (form data field).
- [x] **`testScenarios.ts`** — Added `FormData` support for `createTestScenario`/`updateTestScenario`. Cleaned up `any` casts in JSON path.
- [x] **`userAppearance.ts`** — Added `getTestUserAppearance()` and `updateTestUserAppearance()`. Refactored with shared `extractAppearance()` helper to reduce duplication.

**Types updated:**
- [x] **`imageGeneration.ts`** — Added `GenerateImageRequest`, `GenerateImageResponse`. Added optional `user_id` on `StartImageChatRequest` and `ContinueImageChatRequest`. Fixed missing space in import.
- [x] **`referenceImage.ts`** — Added optional `user_id` on `CreateReferenceImageRequest`.

### Phase 3: Port Pages & Features — Phase 3 complete ✓

Each page/feature can be ported independently once Phase 1 and Phase 2 are done.

- [x] **Test Scenarios page** (`/admin/test`) — Ported `Test.tsx`, `TestScenarioTable` (installed `ag-grid-community` + `ag-grid-react`), `TestScenarioEditor`, all 7 form components (`GeneralForm`, `CoachStateForm`, `ActionsForm`, `IdentitiesForm`, `ChatMessagesForm`, `UserForm`, `UserNotesForm`), `TestScenarioPageHeader`, `TestScenarioSessionFreezer`, `TestScenarioConversationResetterDialog`, `DeleteTestScenarioDialog`, `TestChat`. Ported hooks: `use-test-scenarios`, `use-freeze-test-scenario-session`, `use-test-scenario-user-identities`, `use-previous`. Created TanStack Router route at `routes/_authenticated/admin/test.tsx`.
- [x] **Coach State Visualizer** — Ported `CoachStateVisualizer.tsx` + all utils (`tabConfiguration.ts`, `tabContentFactory.tsx`, `dataUtils.ts`, `renderUtils.tsx`, `ActionItem.tsx`, `IdentityItem.tsx`) + `types.ts` + `index.ts`. All gold-specific styling converted to shadcn semantic CSS variables.
- [x] **Prompts management page** (`/admin/prompts`) — Ported `Prompts.tsx` (refactored to use shared `renderPromptEditor()` instead of duplicating form 3 times), `DeletePromptDialog`, `NewPromptForm`. Created TanStack Router route at `routes/_authenticated/admin/prompts.tsx`.
- [x] **ConversationExporter** — Ported component + `xmlExport.ts` utility. Installed `@xmldom/xmldom` dependency.
- [x] **ConversationResetter** — Ported unified version from Gold that branches between regular reset and test scenario reset based on `UserTargetContext`. Ported `ConversationResetterDialog` and `TestScenarioConversationResetterDialog`. Integrated into `ChatInterface` via new `onResetSuccess` prop.
- [x] **SessionRestorer** — Ported `SessionRestorer.tsx` component.
- [x] **Button `xs` size variant** — Added to shadcn Button component for use by test scenario forms.
- [x] **Image save impersonation support** — Made `Images.tsx` fully impersonation-aware. Added `adminSaveGeneratedImage()` to `api/imageGeneration.ts` (JSON POST to `/admin/identities/save-generated-image`). Updated `use-image-generation.ts` save mutation to accept `admin` flag. `Images.tsx` now: (1) branches `handleSceneSave` to `adminUpdateIdentity` when impersonating, (2) passes `user_id` to `startChat`/`continueChat` for admin endpoint routing, (3) passes `admin: true` to save mutation for admin save endpoint, (4) passes impersonated user ID to `useReferenceImages` for correct ref image checks, (5) invalidates correct query key prefix. Resolves Open Question 7.
- ~~**Demo page** (`/demo`)~~ — Intentionally skipped (not needed)
- ~~**Storybook + MSW**~~ — Intentionally skipped (deferred)

**Implementation notes:**
- Installed 3 new dependencies: `ag-grid-community`, `ag-grid-react`, `@xmldom/xmldom`
- All gold-specific Tailwind classes (`gold-50/100/200/500/600/700/800/900`) converted to shadcn semantic variables (`bg-muted`, `bg-background`, `text-foreground`, `text-muted-foreground`, `border-border`, `text-primary`, etc.)
- All type-only imports updated with `import type` for `verbatimModuleSyntax` compliance
- TypeScript check and full Vite build pass cleanly
- Gold's `UserSelector` component is no longer needed — replaced by global admin impersonation feature

### Phase 3.5: Admin Impersonation Feature (bonus, not in original plan)

Added a global admin impersonation system that lets admins "view as" any user across the entire app. This replaces Gold's per-page `UserSelector` pattern with a unified approach.

- [x] **Backend** — Added `list_all` action to `TestUserViewSet` returning all users with `is_test_user` and `test_scenario_name` fields
- [x] **ImpersonationContext / ImpersonationProvider** — Global context for impersonation state (`impersonatedUser`, `startImpersonating`, `stopImpersonating`)
- [x] **ImpersonationTargetBridge** — Bridges `ImpersonationContext` into `UserTargetProvider`, wrapping the entire authenticated app so all hooks automatically use admin endpoints when impersonating
- [x] **Admin Users page** (`/admin/users`) — Lists all users with search, type column (real user vs test scenario name), and "View As" button
- [x] **ImpersonationBanner** — Sticky amber banner at top of content area showing who is being impersonated, with "Exit View" button
- [x] **Account page** — Made impersonation-aware: shows impersonated user's profile, reference images, and appearance; hides logout button
- [x] **Images page** — Made impersonation-aware: scene save, image generation, image save, and reference image checks all route through admin endpoints when impersonating

### Phase 4: Verification

- [ ] Verify all regular user flows still work (chat, identities, images) — testing in staging
- [ ] Verify all admin flows work (test scenarios, prompts, admin image generation) — testing in staging
- [ ] Verify image generation + save works for both regular and impersonated paths — testing in staging
- [ ] Strip any remaining gold-specific styling from ported components (adapt to Purple's design tokens) — fix as encountered

**Touches:** Purple frontend, possibly backend if any missed API adjustments.

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

1. ~~**Cookie naming:** `discovita-*` or `neovita-*`?~~ **Resolved: `neovita-*`.** Purple conventions take precedence.
2. ~~**Linter:** Keep ESLint (gold) or Biome (purple)?~~ **Resolved: Biome.** Keep Purple's tooling.
3. **Admin user URL naming:** `/admin/user/{id}/...` (generic) or `/admin/test-user/{id}/...` (test-specific)? _(Needed for B3)_
4. ~~**Demo page:** Worth porting or can it be dropped?~~ **Resolved: Dropped.** Not needed.
5. ~~**Storybook:** Priority to port, or defer?~~ **Resolved: Deferred.** Not blocking migration.
6. **Branding in landing page:** Purple landing says "NeoVita" — does that stay or change to Discovita?
7. ~~**`saveGeneratedImage` discrepancy:** Gold uses JSON POST to `/admin/identities/save-generated-image`. Purple uses FormData PATCH to `/identities/{id}/upload-image`. Which endpoint is correct?~~ **Resolved: Both kept.** Purple uses FormData PATCH for regular users (own identities). Added `adminSaveGeneratedImage()` using Gold's JSON POST for admin impersonation (other users' identities). The save mutation branches based on an `admin` flag.
8. **Cookie utility deduplication:** Both `auth.ts` and `authFetch.ts` define their own `getCookie`/`setCookie`. Should these be consolidated into a shared utility? _(Low priority, can do during F5)_
