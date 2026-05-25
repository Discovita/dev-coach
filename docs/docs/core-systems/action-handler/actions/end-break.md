---
sidebar_position: 23
---

# End Break

The `end_break` action closes the user's open `Break` row and may emit the next session's intro video card.

## Action Details

**Action Type**: `end_break`
**Enum Value**: `ActionType.END_BREAK`
**Handler Function**: `end_break()`
**Models Used**: `Break`, [CoachState](/docs/database/models/coach-state), [Action](/docs/database/models/action), `ComponentConfig`

## What It Does

Stamps `ended_at = now()` on the user's single open `Break` row (the one [`start_break`](start-break) opened). The `on_break: bool` derived field flips back to `false`; the frontend's `on_break` clause of the composer-disable rule clears.

Then — if `current_phase` is the first phase of a session whose intro video has not yet been acknowledged — the handler returns a `SESSION_VIDEO` `ComponentConfig` for that intro. Returning the component triggers the **skip-LLM rule** in `process_message`: the intro card becomes the coach response without invoking the LLM. The user clicks Continue on the intro, ACK fires, and the LLM speaks in the new session on the following turn.

This action is **user-button-only**: it is never emitted by the LLM. It fires as the only action on the break card's **I'm Ready** button — `{message: "I'm Ready", actions: [END_BREAK()]}` (the canned-response pattern; the label becomes a real user `ChatMessage`).

## Parameters

None. The handler operates on `coach_state.user`'s single open `Break` row, which [`start_break`](start-break) guarantees to be unique. The corresponding `EndBreakParams` pydantic class exists with zero fields for dispatcher symmetry.

## Implementation Steps

1. **Open-Break Lookup**: Finds the user's `Break` row with `ended_at IS NULL`. No-op if none exists (graceful — repeated clicks should not error).
2. **Close**: Stamps `ended_at = timezone.now()` and saves the row.
3. **Intro Auto-Emit Check**: Reads `current_phase`. If `is_first_phase_of_session(current_phase)` AND the session has an intro key AND that key is NOT in `coach_state.shown_videos`, builds the intro `SESSION_VIDEO` `ComponentConfig` via the shared `intro_component_for(session_key)` helper.
4. **Return**: Returns the intro `ComponentConfig` if built, else `None`.
5. **Action Logging**: Records the action.

## Example Usage

```json
{
  "action": "end_break",
  "params": {}
}
```

## Result

- **Success (no intro to emit)**: Closes the break. Returns `None`. LLM runs on the next turn based on chat history alone.
- **Success (intro emitted)**: Closes the break AND returns the intro video `ComponentConfig`. Skip-LLM rule fires; the intro card becomes the next coach message.
- **No Open Break**: No-op. Does not raise. (Defensive — repeated clicks or a stale UI shouldn't 500.)
- **Composer State**: `on_break` flips to `false` immediately. If an intro is emitted, the unacked-SESSION_VIDEO clause of `useComposerDisabled` then keeps the composer disabled until the user clicks Continue on the intro and ACK lands. The two clauses hand off cleanly with no gap.
- **Logging**: Records the action with result summary: `"Ended break"` (or `"Ended break (no open break found)"` for the no-op case).

## Related Actions

- [Start Break](start-break) — opens the `Break` row this action closes.
- [Acknowledge Session Video](acknowledge-session-video) — fires from the intro card's Continue button after this action emits it.
- [Transition Phase](transition-phase) — runs the *other* injection point for intros (when transitioning into a session with no preceding outro).
