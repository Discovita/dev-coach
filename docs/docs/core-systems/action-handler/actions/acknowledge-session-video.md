---
sidebar_position: 21
---

# Acknowledge Session Video

The `acknowledge_session_video` action records that the user has finished watching a session video by appending its key to `coach_state.shown_videos`.

## Action Details

**Action Type**: `acknowledge_session_video`
**Enum Value**: `ActionType.ACKNOWLEDGE_SESSION_VIDEO`
**Handler Function**: `acknowledge_session_video()`
**Models Used**: [CoachState](/docs/database/models/coach-state), [Action](/docs/database/models/action)

## What It Does

Appends a session-video key to the user's `coach_state.shown_videos` list. The frontend reads `shown_videos` to switch the video card's button label from **Watch** to **Watch Again** and to lift the unacked-video clause of the composer-disable rule. Idempotent — appending the same key twice is a no-op.

This action is **user-button-only**: it is never emitted by the LLM. It fires when the user clicks **Continue** on the video modal (PR 17). The `video_key` parameter is baked into the card's button by the server when the card is constructed — the frontend forwards `config.buttons[0].actions` verbatim without inspecting them.

## Parameters

| Parameter   | Type   | Required | Description                                                                     |
| ----------- | ------ | -------- | ------------------------------------------------------------------------------- |
| `video_key` | string | Yes      | Registry key for the video (e.g., `"welcome_session_intro"`). Must exist in `SESSION_VIDEOS`. |

## Implementation Steps

1. **Registry Validation**: Looks up `video_key` in `SESSION_VIDEOS`. Raises `ValidationError` on unknown key (defense-in-depth — clients should never send unknown keys, but a stale frontend should not silently corrupt state).
2. **Idempotency Check**: If `video_key` is already in `coach_state.shown_videos`, returns without modifying state. No Action row is created in this case.
3. **Append**: Appends `video_key` to the `shown_videos` list.
4. **Save**: Saves the updated coach state.
5. **Action Logging**: Records the action with the video key.

## Example Usage

```json
{
  "action": "acknowledge_session_video",
  "params": {
    "video_key": "welcome_session_intro"
  }
}
```

## Result

- **Success**: Appends the key to `shown_videos` and saves the coach state. Returns `None` (does not return a `ComponentConfig`).
- **Already Acked**: Skips update if the key is already present (idempotency). No Action row created.
- **Unknown Key**: Raises `ValidationError`. No state change, no Action row.
- **Logging**: Records the action with result summary: `"Acknowledged session video 'welcome_session_intro'"`

## Related Actions

- [Start Break](start-break) — typically chained after `acknowledge_session_video` on outro Continue clicks (the outro card's button dispatches `[ACK, START_BREAK]`).
- [Transition Phase](transition-phase) — emits the video card whose Continue button dispatches this action (intro card on session entry, outro card on session exit).
