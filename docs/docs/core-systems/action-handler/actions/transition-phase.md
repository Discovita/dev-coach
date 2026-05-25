---
sidebar_position: 11
---

# Transition Phase

The `transition_phase` action updates the current coaching phase in the [CoachState](/docs/database/models/coach-state).

## Action Details

**Action Type**: `transition_phase`  
**Enum Value**: `ActionType.TRANSITION_PHASE`  
**Handler Function**: `transition_phase()`  
**Models Used**: [CoachState](/docs/database/models/coach-state), [Action](/docs/database/models/action)

## What It Does

Updates the `current_phase` field of the user's coach state to move between coaching phases (e.g., from "identity_brainstorming" to "identity_refinement").

## Parameters

| Parameter  | Type   | Required | Description                                |
| ---------- | ------ | -------- | ------------------------------------------ |
| `to_phase` | string | Yes      | The target coaching phase to transition to |

## Implementation Steps

1. **Phase Update**: Updates the `current_phase` field in the [CoachState](/docs/database/models/coach-state)
2. **Special Handling**: Depending on the target phase:
   - **Identity Refinement**: Accepts all current identities for the user, then calls `set_current_identity_to_next_pending(coach_state, IdentityState.REFINEMENT_COMPLETE)`
   - **Identity Commitment**: Calls `set_current_identity_to_next_pending(coach_state, IdentityState.COMMITMENT_COMPLETE)`
   - **I Am Statement**: Calls `set_current_identity_to_next_pending(coach_state, IdentityState.I_AM_COMPLETE)`
3. **Save**: Saves the updated coach state
4. **Action Logging**: Records the action with old and new phase labels

## Example Usage

```json
{
  "action": "transition_phase",
  "params": {
    "to_phase": "identity_refinement"
  }
}
```

## Result

- **Success**: Updates the coaching phase and saves the coach state
- **Logging**: Records the action with result summary: "Transitioned from 'Identity Brainstorming' to 'Identity Refinement'"

## Session-Boundary Side Effects

Phases roll up into **sessions** via the `SESSIONS` map in `server/enums/coaching_phase.py` (see the [Coaching Sessions](/docs/coach/phases#coaching-sessions) section of the Phases doc). When a `transition_phase` crosses a session boundary, the handler attaches an intro or outro video card to the LLM's transition coach message via the existing `component_config` field — no new `ChatMessage` row is created, no multi-message response shape is introduced.

### The Two Cases

After the phase change is applied, the handler computes `leaving_session = session_of(old_phase)` and `entering_session = session_of(new_phase)` and applies these rules in order:

1. **Leaving session has an outro** (`is_last_phase_of_session(old_phase)` AND the session's `outro` key is non-null): attach the outro video component. The card's Continue button is bound to `[ACKNOWLEDGE_SESSION_VIDEO(outro_key), START_BREAK(leaving_session)]`.
2. **Entering session has an unacked intro** (`is_first_phase_of_session(new_phase)` AND the session's `intro` key is non-null AND that key is NOT in `coach_state.shown_videos`): attach the intro video component. The Continue button is bound to `[ACKNOWLEDGE_SESSION_VIDEO(intro_key)]`.
3. **Neither**: no component attached; the transition message ships as plain text.

### Precedence

**Outro wins over intro** when both would apply. This is intentional — the user should see the closing video for the session they just finished before being introduced to the next one. The next session's intro card is then emitted by [`end_break`](end-break) after the user closes the break.

### What Runs the LLM, and What Doesn't

`transition_phase` runs **once per session boundary**, when the LLM emits it. The attached video card is the coach response for that turn (text + component in one `ChatMessage` row). The card's Continue click is a user-button action; whether the LLM runs on the *following* turn depends on whether that button's action chain returns a `ComponentConfig`:

- **Intro card Continue** → `[ACK]`. ACK returns nothing. LLM runs in the already-current new phase.
- **Outro card Continue** → `[ACK, START_BREAK]`. `START_BREAK` returns the `SESSION_BREAK` component, the skip-LLM rule fires, and the break card becomes the next coach message without invoking the LLM.

The LLM never decides when a video plays and has no awareness videos exist as a feature — it just sees acked/unacked-video and break narrative descriptions in serialized chat history (see the recent-messages serialization helper for the bracketed-description format).

## Related Actions

- [Select Identity Focus](select-identity-focus) - Set identity category focus for the new phase
- [Set Current Identity](set-current-identity) - Set current identity for refinement phase
- [Acknowledge Session Video](acknowledge-session-video) — bound to the Continue button on intro and outro cards this handler emits.
- [Start Break](start-break) — bound to the Continue button on outro cards (after ACK).
- [End Break](end-break) — the **other** injection point for intros (when transitioning into a session whose preceding session had no outro, the intro would already be in `shown_videos` so `transition_phase` skips it; otherwise the boundary takes the outro path and the next session's intro fires from `end_break`).
