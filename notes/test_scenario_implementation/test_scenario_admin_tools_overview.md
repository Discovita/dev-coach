# Test Scenario Admin Tools: Overview & Implementation

This document summarizes the major changes and new features added to support **admin-driven test scenario chat**, test user impersonation, and robust test tooling in the Discovita project. Use this as a reference or to onboard colleagues to the new system.

---

## 1. Test Scenario User Endpoints (Backend)

- **New ViewSet:** `TestUserViewSet` provides admin/superuser-only endpoints for fetching and managing test scenario user data.
- **Endpoints:**
  - `/api/v1/test-user/{user_id}/profile/` — Get test user profile
  - `/api/v1/test-user/{user_id}/complete/` — Get all test user data (chat, coach state, etc.)
  - `/api/v1/test-user/{user_id}/coach-state/` — Get coach state
  - `/api/v1/test-user/{user_id}/identities/` — Get identities
  - `/api/v1/test-user/{user_id}/chat-messages/` — Get chat messages
- **Permissions:** Only admin/superuser can access these endpoints.
- **Purpose:** Enables admins to simulate any test user for scenario-based QA and debugging.

---

## 2. Admin-Only Chat & Impersonation (Backend)

- **New Endpoint:** `/api/v1/coach/process-message-for-user/`
  - Allows an admin to send a chat message as any user (by user_id).
  - Uses the same business logic as the regular chat endpoint, but impersonates the specified user.
- **Security:** Only admin/superuser can use this endpoint.
- **Use Case:** Enables full test scenario chat simulation without logging in/out or switching users.

---

## 3. Test Scenario Chat UI (Frontend)

- **New Component:** `TestScenarioChatInterface`
  - Mimics the main `ChatInterface` but uses test scenario user hooks and endpoints.
  - Supports optimistic UI: messages appear instantly while sending.
  - Handles loading, error, and identity choice just like the main chat.
- **Integration:** Used in the test scenario admin page to provide a real chat experience for any test user.

---

## 4. New Test Scenario Hooks (Frontend)

- **Hooks Directory:** `client/src/hooks/test-scenario/`
- **Hooks Implemented:**
  - `useTestScenarioChatMessages` — Fetch/send chat messages (with optimistic UI)
  - `useTestScenarioUserCoachState` — Fetch coach state
  - `useTestScenarioUserIdentities` — Fetch identities
  - `useTestScenarioUserActions` — Get actions from cache
  - `useTestScenarioUserFinalPrompt` — Get final prompt from cache
- **API Parity:** All hooks mirror the main user hooks for easy UI reuse and maintenance.

---

## 5. API Documentation

- **Docs:** `server/docs/api/test_user_api.md` documents all new test user endpoints, permissions, and example responses.
- **Purpose:** Ensures clarity for backend/frontend devs and future maintainers.

---

## 6. Database Restore & Migration Tips

- **Restoring Only One Table:** Use `pg_restore --table=public.prompts ...` to restore just the prompts table from a backup.
- **Dockerized Postgres:** Always use `-h localhost -p 5432 -U <user> -d <db>` when restoring to a Dockerized database.
- **Migration Errors:**
  - If you see errors like `relation ... already exists`, use `python manage.py migrate <app> 0001 --fake` to mark migrations as applied.
  - Or, drop the table manually if you want Django to recreate it.

---

## 7. Superuser Password Management

- **Change Password:** Use `python manage.py changepassword <username>` (or `docker compose exec backend python manage.py changepassword <username>` if running in Docker).

---

## 8. Summary Table

| Area                | What Was Added/Changed                                      |
|---------------------|------------------------------------------------------------|
| Backend API         | TestUserViewSet, process-message-for-user, admin-only perms|
| Frontend Components | TestScenarioChatInterface, TestChat, TestScenarioTable     |
| Frontend Hooks      | useTestScenarioUser* hooks for all user data               |
| Optimistic UI       | Full parity with main chat interface                       |
| Docs                | API docs, this summary, migration/restore tips             |

---

## 9. Next Steps & Maintenance

- All test scenario features are admin-only and safe for QA/debugging.
- Keep test user endpoints and hooks in sync with main user features for best UX.
- Use the provided docs and scripts for onboarding and troubleshooting.

---

**For questions or further improvements, see the code comments or ask the dev team!** 