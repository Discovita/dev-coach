---
sidebar_position: 22
---

# Start Break

The `start_break` action opens a between-session pause by creating a `Break` row and returning a `SESSION_BREAK` component for the frontend to render.

## Action Details

**Action Type**: `start_break`
**Enum Value**: `ActionType.START_BREAK`
**Handler Function**: `start_break()`
**Models Used**: `Break`, [CoachState](/docs/database/models/coach-state), [Action](/docs/database/models/action), `ComponentConfig`

## What It Does

Opens a `Break` row (`ended_at IS NULL`) tagged with the session the user is leaving, then returns a `SESSION_BREAK` `ComponentConfig` carrying a single **I'm Ready** button bound to [`END_BREAK`](end-break). Because the handler returns a `ComponentConfig`, the **skip-LLM rule** fires in `process_message` — the break card becomes the coach response without invoking the LLM.

The `on_break: bool` derived field on the coach response and user-state endpoints flips to `true` while this row stays open. The frontend disables the chat composer for the duration (`useComposerDisabled` checks `coachState.on_break`).

This action is **user-button-only**: it is never emitted by the LLM. It fires as the second action on an outro video's Continue button (the chain is `[ACKNOWLEDGE_SESSION_VIDEO, START_BREAK]`). The `session_key` parameter identifies the session being **left**, not the user's current session — by the time this action runs, `transition_phase` has already advanced `current_phase` into the next session.

## Parameters

| Parameter     | Type   | Required | Description                                                                                                  |
| ------------- | ------ | -------- | ------------------------------------------------------------------------------------------------------------ |
| `session_key` | string | Yes      | The session key being left (e.g., `"get_to_know_session"`). Must exist in the `SESSIONS` map. Stored on the new `Break` row as `triggered_by_session`. |

## Implementation Steps

1. **Session Validation**: Verifies `session_key` exists in the `SESSIONS` map. Raises `ValidationError` on unknown key.
2. **Overlap Check (hard rule)**: If `Break.objects.filter(user=u, ended_at__isnull=True).exists()`, raises `ValidationError`. There is never more than one open break per user; silently reusing or replacing would corrupt the soft-block guarantee.
3. **Break Row Creation**: Creates a `Break` with `user`, `triggered_by_session=session_key`, `coach_message=<coach_message>` (the message the Continue click came from). `started_at` is set via `auto_now_add`.
4. **Component Build**: Constructs a `SESSION_BREAK` `ComponentConfig` containing the "I'm Ready" button with `actions=[END_BREAK()]`.
5. **Return**: Returns the `ComponentConfig` (triggers the skip-LLM rule downstream).
6. **Action Logging**: Records the action with the triggering session.

## Example Usage

```json
{
  "action": "start_break",
  "params": {
    "session_key": "get_to_know_session"
  }
}
```

## Result

- **Success**: Opens a `Break` row, returns the `SESSION_BREAK` `ComponentConfig`. `on_break` derives to `true` on the next state read. Composer disables on the frontend.
- **Overlap**: Raises `ValidationError` if another open `Break` exists for the user. No state change, no Action row.
- **Unknown Session Key**: Raises `ValidationError`. No state change, no Action row.
- **Logging**: Records the action with result summary: `"Started break for session 'get_to_know_session'"`

## Component Structure

The returned component is:

- **Component Type**: `ComponentType.SESSION_BREAK`
- **Buttons**:
  - **"I'm Ready"** with `actions=[END_BREAK()]`. Click dispatches `{message: "I'm Ready", actions: [END_BREAK()]}` (canned-response pattern — the label becomes a real user `ChatMessage`).

The frontend renderer for this component is `SessionBreakComponent` (see [Persistent Components](../../component-renderer/persistent-components)).

## Related Actions

- [Acknowledge Session Video](acknowledge-session-video) — the action that precedes this one in the outro Continue chain.
- [End Break](end-break) — closes the break this action opened; bound to the **I'm Ready** button via the server-baked action chain.
- [Transition Phase](transition-phase) — runs once per session boundary and emits the outro video card whose Continue button dispatches `[ACK, START_BREAK]`.
