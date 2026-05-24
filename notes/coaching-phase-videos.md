# Coaching Phase Videos — Feature Spec

## Purpose

Show Leigh Ann's pre-recorded videos at the **start and end of each coaching session** (a session = one or more consecutive phases that belong together). Videos are **server-injected** based on phase transitions — the LLM never decides when a video plays.

Videos appear inline in chat as thin cards. The user can revisit any previously shown video.

## Reframe: pattern first, mapping second

The deliverable is the **architecture pattern + a reusable procedure for adding a video at a determined point in time** — not a one-time wiring of these specific 12 videos.

When Leigh Ann delivers or swaps a video:

1. Upload the file to S3.
2. Edit the `intro` / `outro` key for the relevant session in the `SESSIONS` map.
3. Edit the entry in the video registry (`video_key → { name, url }`).

No code changes, no migrations, no enum updates, no frontend work, **no prompt edits**.

The implementation plan **must include** a Procedures MCP doc — `procedure / dev-coach / coach / add-session-video` — walking through the procedure. First-class deliverable.

## Core design decisions

### 1. Sessions are codified as metadata on `CoachingPhase`

A `SESSIONS` map lives next to the `CoachingPhase` enum in `server/enums/coaching_phase.py`. Session keys carry the `_session` suffix so they're never confused with phase values.

```python
SESSIONS = {
    "welcome_session":        {"phases": [CoachingPhase.INTRODUCTION],                                               "intro": "welcome_session_intro",       "outro": None},
    "get_to_know_session":    {"phases": [CoachingPhase.GET_TO_KNOW_YOU, CoachingPhase.IDENTITY_WARMUP],             "intro": "get_to_know_session_intro",   "outro": "get_to_know_session_outro"},
    "brainstorming_session":  {"phases": [CoachingPhase.IDENTITY_BRAINSTORMING, CoachingPhase.BRAINSTORMING_REVIEW], "intro": "brainstorming_session_intro", "outro": "brainstorming_session_outro"},
    "refinement_session":     {"phases": [CoachingPhase.IDENTITY_REFINEMENT, CoachingPhase.ANYTHING_MISSING],        "intro": "refinement_session_intro",    "outro": "refinement_session_outro"},
    "commitment_session":     {"phases": [CoachingPhase.IDENTITY_COMMITMENT],                                        "intro": "commitment_session_intro",    "outro": "commitment_session_outro"},
    "i_am_session":           {"phases": [CoachingPhase.I_AM_STATEMENT],                                             "intro": "i_am_session_intro",          "outro": "i_am_session_outro"},
    "visualization_session":  {"phases": [CoachingPhase.IDENTITY_VISUALIZATION],                                     "intro": "visualization_session_intro", "outro": None},
}
```

Helpers in the same module:
- `session_of(phase) → session_key`
- `is_first_phase_of_session(phase) → bool` (intro trigger)
- `is_last_phase_of_session(phase) → bool` (outro / break trigger)

`welcome_session` and `visualization_session` are intro-only by design — no break after welcome, no break after the final session.

### 2. Video keys are `<session_key>_intro` or `<session_key>_outro`

Examples: `brainstorming_session_intro`, `i_am_session_outro`. This string is:
- The entry stored in `coach_state.shown_videos`
- The `video_key` parameter to `ACKNOWLEDGE_SESSION_VIDEO` (set by the server when building the card, never by the LLM)
- The lookup key in the video registry

### 3. Storage on CoachState mirrors `asked_questions`

```python
shown_videos = ArrayField(
    models.CharField(max_length=255),
    default=list,
    blank=True,
    help_text="List of session video keys the user has acknowledged.",
)
```

One migration. No `Video` DB model.

### 4. Video registry is a static Python config

`video_key → { name, url }`. The `SESSIONS` map already encodes which video belongs where; the registry just resolves keys to display data.

```python
SESSION_VIDEOS = {
    "brainstorming_session_intro": {
        "name": "Brainstorming Intro",
        "url": "https://<bucket>.s3.amazonaws.com/...",
    },
    ...
}
```

### 5. Video hosting: S3, same pattern as user images

Frontend `<video src>` streams directly from S3. HTTP range requests work, so basic seeking is supported. CloudFront later if mobile scrubbing is bad. Source files at `dev-coach/videos/`.

### 6. Videos are server-injected via action handlers — the LLM never decides when

This is the heart of the design. Videos are **not** an LLM tool. The server emits video cards deterministically by enriching the action handlers that already mark session boundaries (`transition_phase`, `END_BREAK`) and by seeding the very first one at chat creation. The LLM has no awareness videos exist as a feature.

**Three injection points — all in action handlers:**

**A) Welcome injection — `ensure_initial_message_exists`:**

Instead of seeding the hardcoded `INITIAL_MESSAGE` text, seed a coach message carrying a `SESSION_VIDEO` ComponentConfig for `welcome_session_intro`, with `text=""` (no greeting text on the card itself). The greeting ("Hi, I'm Leigh-Ann...") is produced by the LLM the first time it runs — which is after the user clicks Continue on the welcome video. The old `INITIAL_MESSAGE` constant is deleted.

**B) `transition_phase` handler enrichment:**

After the phase transition runs, consult the `SESSIONS` map. The handler returns at most one component, which is **attached as the `component_config` of the LLM's coach response message** (existing message-with-component pattern — no new message row is created).

Precedence: outro wins over intro when both would apply.

```python
# pseudocode — inside transition_phase action handler, after phase change applied
leaving_session  = session_of(old_phase)
entering_session = session_of(new_phase)

if is_last_phase_of_session(old_phase) and SESSIONS[leaving_session]["outro"]:
    outro_key = SESSIONS[leaving_session]["outro"]
    return SessionVideoComponent(
        video_key=outro_key,
        continue_actions=[
            ACKNOWLEDGE_SESSION_VIDEO(outro_key),
            START_BREAK(leaving_session),
        ],
    )

if (is_first_phase_of_session(new_phase)
    and SESSIONS[entering_session]["intro"]
    and SESSIONS[entering_session]["intro"] not in coach_state.shown_videos):
    intro_key = SESSIONS[entering_session]["intro"]
    return SessionVideoComponent(
        video_key=intro_key,
        continue_actions=[ACKNOWLEDGE_SESSION_VIDEO(intro_key)],
    )

return None
```

The LLM's transition text and the video card live in the same `ChatMessage` row. The frontend renders them together in one bubble.

**C) `END_BREAK` handler enrichment:**

After stamping `ended_at`, check whether the user is now at the start of a new session whose intro hasn't been acked. If so, return the intro video component. The skip-LLM-on-component rule then fires — the LLM doesn't run this turn. The user acks the intro; the LLM speaks in the new session on the next turn.

```python
# pseudocode — inside END_BREAK action handler, after ended_at stamped
current_session = session_of(coach_state.current_phase)
intro_key       = SESSIONS[current_session]["intro"]

if (is_first_phase_of_session(coach_state.current_phase)
    and intro_key
    and intro_key not in coach_state.shown_videos):
    return SessionVideoComponent(
        video_key=intro_key,
        continue_actions=[ACKNOWLEDGE_SESSION_VIDEO(intro_key)],
    )

return None
```

**`process_message` null-message contract:**
- `message=None` (programmatic-only, from action-only button clicks like video Continue): no user ChatMessage is saved; user actions still apply; LLM is called only if no component_config was returned by user actions.
- `message=""` (empty string): treated as a real user message — saved as a ChatMessage with empty content. The user shouldn't be able to send this through the UI, but if they do it's handled normally.
- `message="any text"`: normal user message, saved as ChatMessage.

**Skip-LLM rule** (after `apply_user_component_actions`): skip the LLM call iff a `component_config` was returned by any user action (e.g., `END_BREAK` returning a `SESSION_VIDEO`, or `START_BREAK` returning a `SESSION_BREAK`). Otherwise call the LLM — even if no user message was added this turn. The LLM responds based on chat history alone, which works because of component serialization (see Decision 10).

**What's NOT in this design:**
- No `SHOW_SESSION_INTRO_VIDEO` / `SHOW_SESSION_OUTRO_VIDEO` actions
- No per-session context key
- No prompt edits, no gate paragraphs
- **No pre-LLM intro gate or post-LLM outro hook in `process_message`** — handlers carry the logic
- **No multi-message coach response shape** — coach responses remain a single coach message with optional component_config
- The LLM has zero involvement with videos (it neither triggers them nor knows they exist as a feature — it just sees acknowledged-video markers in serialized chat history, see Decision 10)

### 7. Three user-button actions

Only the user's button clicks invoke actions. The server emits the components; the user closes the loop. **All parameters are baked into the buttons by the server when constructing each card — the LLM never sets any of them.**

- `ACKNOWLEDGE_SESSION_VIDEO(video_key: str)` — appends `video_key` to `shown_videos`. Idempotent. Fires on the video modal's Continue button (see Decision 8 for button timing).
- `START_BREAK(session_key: str)` — creates a `Break` row with `triggered_by_session = session_key`, returns a `SESSION_BREAK` ComponentConfig. Fires as the second action on the outro video's Continue button. The `session_key` identifies the session being left (NOT the user's current session, which has already advanced by this point — see Decision 6.B).
- `END_BREAK()` — zero-param. Stamps `ended_at` on the user's single open `Break`. May return a `SESSION_VIDEO` ComponentConfig for the new session's intro (see Decision 6.C). Fires as the only action on the break card's "I'm Ready" button.

**Two dispatch patterns — distinct on purpose:**

- **Video Continue button**: action-only. Frontend dispatches `{message: null, actions: [...]}`. No user ChatMessage is saved. The video is the coach's content; clicking Continue is acknowledgment, not conversation. This means there is no user-message bubble between the video card and whatever comes next.
- **Break "I'm Ready" button**: canned-response pattern (same as the existing `IntroCannedResponseComponent`). Frontend dispatches `{message: "I'm ready", actions: [END_BREAK()]}`. The button's label becomes a real user ChatMessage that appears in chat history. This is the *only* place in the video flow where a user message is auto-fired by a button click.

**Button action chains:**

- **Intro video** Continue → `{message: null, actions: [ACKNOWLEDGE_SESSION_VIDEO(video_key)]}`. ACK runs, returns no component, no skip-LLM trigger. The LLM runs in the (already-current) phase and produces the session's first prompt as the next coach message.
- **Outro video** Continue → `{message: null, actions: [ACKNOWLEDGE_SESSION_VIDEO(video_key), START_BREAK(session_key)]}`. ACK runs. `START_BREAK` returns the `SESSION_BREAK` component config; the skip-LLM rule fires; the break card is saved as the next coach message.
- **Break card "I'm Ready"** → `{message: "I'm ready", actions: [END_BREAK()]}`. Saves "I'm ready" as a user message. `END_BREAK` closes the break and returns the next session's intro video component. The skip-LLM rule fires; the intro card is saved as the next coach message.

**Important: `transition_phase` runs ONCE per session boundary — when the LLM emits it.** It does not appear in any of the user-button chains. The handler attaches the outro card (when leaving a session that has one) or the intro card (when leaving a session without an outro and entering one with an intro) to the LLM's transition coach message. By the time the user is interacting with the outro or break card, `current_phase` already reflects the next session. This is what makes `START_BREAK` need an explicit `session_key` parameter (the session being left, not the current one).

### 8. UI: thin card + modal player with threshold-gated Continue button

**Active state (unacknowledged):**
- Thin card: `<Video Name>` + `[ Watch ]` button
- Click opens a modal containing the `<video>` element
- The modal renders a **Continue button** that is disabled until the video reaches a threshold: 20 seconds before the end, OR the 50% mark for videos shorter than 30 seconds. This prevents users from skipping past the content while still letting them dismiss the modal once they've watched it.
- Clicking Continue fires the bundled actions (`ACKNOWLEDGE_SESSION_VIDEO` and, for outros, also `START_BREAK`) and closes the modal.
- Closing the modal early (Esc / backdrop click) is allowed — no actions fire, the card stays in active state, they can re-open via Watch.
- **Composer disabled rule**: while an unacknowledged video card is the latest coach message, the chat composer is disabled. Frontend derives this from `latestMessage.component?.type === SESSION_VIDEO && !shownVideos.includes(latestMessage.component.video_key)`. The user must watch the video (to the threshold) and click Continue before they can type.

**Persisted state (historical, replayable):**
- Same thin card; `[ Watch ]` button is replaced by `[ Watch Again ]` (label change only — derived from `video_key in shown_videos`)
- Modal opens, no Continue button rendered, **no backend action on close**
- Same `component_config` row in the DB — only the frontend rendering differs

**Convention deviation to flag in the spec:** persistent-component docs say to strip all buttons from historical components. We keep `Watch Again` because it's frontend-only and doesn't dispatch any action.

### 9. Break is a backend-tracked, soft-blocking persistent component

After an outro is acknowledged, a `Break` row opens, a `SESSION_BREAK` persistent component renders, and the chat composer is disabled until the user clicks "I'm Ready."

**Soft block:** no timer, no enforcement. "I'm Ready" is available immediately. The block exists to make pausing the *default* action.

**State (backend only — frontend computes nothing):**

```python
class Break(models.Model):
    user = FK(User)
    started_at = DateTimeField(auto_now_add=True)
    ended_at = DateTimeField(null=True, blank=True)
    triggered_by_session = CharField(max_length=255)  # e.g., "brainstorming_session"
    coach_message = FK(ChatMessage, null=True)
```

"On a break?" → `Break.objects.filter(user=u, ended_at__isnull=True).exists()`. Duration computed, not stored.

**API:** `on_break: bool` is derived from `Break.objects.filter(user=u, ended_at__isnull=True).exists()` and exposed on **both** the coach response AND the user-state endpoint (so the composer is correctly disabled on initial chat load / refresh, not only after a message round-trip). Frontend disables composer when true.

### 10. LLM continuity via component serialization

Because videos and breaks are server-injected and the LLM has no awareness of them, the chat history must carry enough narrative signal that the LLM can pick up the thread after a session boundary. Without this, the LLM is blind: it sees an unexplained "I'm ready" with no preceding question.

**`get_recent_chat_messages_for_prompt` is updated to render `component_config` into bracketed textual descriptions when serializing for the LLM.** The DB row is unchanged; only the LLM-facing string representation changes. Coach messages that have both text AND a `component_config` (the common case for transition turns) are serialized with both: the LLM's text first, then the bracketed component description on a new line.

Suggested formats:

- Acked video: `[Showed user the "<video_name>" video. User watched it.]`
- Unacked video: `[Showed user the "<video_name>" video. User has not watched it yet.]`
- Closed break: `[Offered user a break. User took it and returned when ready.]`
- Open break: `[Offered user a break. User has not returned yet.]`

`shown_videos` and the Break table are the sources of truth for acked/closed state at serialization time.

**Also bump the default history `count` from 5 to 10.** A single session boundary can fill several slots with video/break/intro bubbles, leaving zero room for actual session content. 10 is a defensive minimum.

This is the only piece of "LLM-aware" code in the design, and it's deliberately confined to a serialization helper. The LLM still has no actions, no context keys, and no awareness that videos exist as a feature — it just reads narration in chat history.

## Lifecycle walkthrough (single session boundary, end-to-end)

For Get-to-Know → Brainstorming. Other boundaries follow the same pattern.

| # | Trigger | What happens | ChatMessage rows written | CoachState / Break delta |
|---|---|---|---|---|
| 0 | First-ever app open | `ensure_initial_message_exists` seeds welcome video card | COACH: `text=""`, component=`SESSION_VIDEO(welcome_session_intro)` | — |
| 1 | User clicks Continue on welcome | Frontend `{message: null, actions: [ACK(welcome_session_intro)]}`. No user msg. ACK runs, returns no component. LLM runs in INTRODUCTION. | COACH: "Hi, I'm Leigh-Ann..." | `shown_videos += welcome_session_intro` |
| ~ | Normal back-and-forth in INTRODUCTION | LLM converses with user | (many USER/COACH rows) | — |
| 2 | LLM transition turn (INTRODUCTION → GET_TO_KNOW_YOU) | LLM emits text "Let's move on to getting to know you" + `transition_phase(GET_TO_KNOW_YOU)`. Handler: leaving `welcome_session` has no outro; entering `get_to_know_session` has unacked intro → **attaches** `SESSION_VIDEO(get_to_know_session_intro)` to the LLM's message. | COACH: `text="Let's move on..."`, component=`SESSION_VIDEO(get_to_know_session_intro)` | `current_phase = GET_TO_KNOW_YOU` |
| 3 | User clicks Continue on get-to-know intro | `{message: null, actions: [ACK]}`. No user msg. ACK runs, returns no component. LLM runs in GET_TO_KNOW_YOU. | COACH: "Now let me ask you about..." | `shown_videos += get_to_know_session_intro` |
| ~ | Normal back-and-forth through GET_TO_KNOW_YOU + IDENTITY_WARMUP | LLM converses | (many USER/COACH rows) | — |
| 4 | LLM transition turn (IDENTITY_WARMUP → IDENTITY_BRAINSTORMING) | LLM emits text "Beautiful work, take a moment" + `transition_phase(IDENTITY_BRAINSTORMING)`. Handler: leaving `get_to_know_session` has outro → **attaches** `SESSION_VIDEO(get_to_know_session_outro)` to the LLM's message. | COACH: `text="Beautiful work..."`, component=`SESSION_VIDEO(get_to_know_session_outro)` | `current_phase = IDENTITY_BRAINSTORMING` |
| 5 | User clicks Continue on outro | `{message: null, actions: [ACK(outro_key), START_BREAK("get_to_know_session")]}`. No user msg. ACK runs. START_BREAK returns SESSION_BREAK component → skip-LLM rule fires. | COACH: component=`SESSION_BREAK` | `shown_videos += outro`; Break row opens; `on_break = true`; composer disabled |
| 6 | User clicks "I'm Ready" on break (maybe hours later) | `{message: "I'm ready", actions: [END_BREAK()]}`. User msg saved. END_BREAK closes break, sees `current_phase` is first phase of `brainstorming_session` with unacked intro → returns `SESSION_VIDEO(brainstorming_session_intro)`. Skip-LLM rule fires. | USER: "I'm ready"; COACH: component=`SESSION_VIDEO(brainstorming_session_intro)` | Break `ended_at` stamped; `on_break = false`; composer disabled (unacked video latest) |
| 7 | User clicks Continue on brainstorming intro | `{message: null, actions: [ACK(brainstorming_session_intro)]}`. No user msg. ACK runs, returns no component. LLM runs in IDENTITY_BRAINSTORMING. | COACH: "Welcome to brainstorming!..." | `shown_videos += brainstorming intro`; composer re-enabled |
| 8+ | Normal IDENTITY_BRAINSTORMING conversation | ... | ... | ... |

**Key invariants:**
- **At most one coach message per server response.** Coach messages may carry text + component together in a single row (steps 2, 4) — there is no multi-message response shape.
- One user-message bubble per boundary ("I'm ready" at step 6). Everything else is coach-driven.
- LLM is called at steps 1, 2, 3, 4, 7 (and during normal conversation). LLM is *not* called at steps 0, 5, 6.
- Multiple consecutive coach messages between user-typed inputs is normal (steps 4 → 5; step 6 user msg → step 6 coach component → step 7 coach text).
- The video DB rows never change after the ACK — only `shown_videos` updates, and the frontend re-derives Watch vs Watch Again from that.

## Sessions & videos

Files at `dev-coach/videos/` (renamed to match session keys). Number prefix = play order; remainder of the filename = the video key (dashes → underscores).

| # | File | Session | Position | Phases in session |
|---|---|---|---|---|
| 01 | `01-welcome-session-intro.mov`            | `welcome_session`        | intro | INTRODUCTION |
| 02 | `02-get-to-know-session-intro.mov`        | `get_to_know_session`    | intro | GET_TO_KNOW_YOU → IDENTITY_WARMUP |
| 03 | `03-get-to-know-session-outro.mov`        | `get_to_know_session`    | outro | (fires after IDENTITY_WARMUP) |
| 04 | `04-brainstorming-session-intro.mov`      | `brainstorming_session`  | intro | IDENTITY_BRAINSTORMING → BRAINSTORMING_REVIEW |
| 05 | `05-brainstorming-session-outro.mov`      | `brainstorming_session`  | outro | (fires after BRAINSTORMING_REVIEW) |
| 06 | `06-refinement-session-intro.mov`         | `refinement_session`     | intro | IDENTITY_REFINEMENT → ANYTHING_MISSING |
| 07 | `07-refinement-session-outro.mov`         | `refinement_session`     | outro | (fires after ANYTHING_MISSING) |
| 08 | `08-commitment-session-intro.mov`         | `commitment_session`     | intro | IDENTITY_COMMITMENT |
| 09 | `09-commitment-session-outro.mov`         | `commitment_session`     | outro | (fires after IDENTITY_COMMITMENT) |
| 10 | `10-i-am-session-intro.mov`               | `i_am_session`           | intro | I_AM_STATEMENT |
| 11 | `11-i-am-session-outro.mov`               | `i_am_session`           | outro | (fires after I_AM_STATEMENT) |
| 12 | `12-visualization-session-intro.mov`      | `visualization_session`  | intro | IDENTITY_VISUALIZATION |

**Asymmetry (intentional):** `welcome_session` and `visualization_session` are intro-only — no outro, no break.

**Caveat:** the mapping is mutable. The architecture treats the `SESSIONS` map and registry as data.

## Rejected alternatives (do not re-propose)

| Idea | Why rejected |
|---|---|
| LLM-driven `SHOW_SESSION_INTRO/OUTRO_VIDEO` actions | Server can derive video timing deterministically from phase transitions. Removes prompt-engineering surface and eliminates the hallucination risk entirely |
| Pre-LLM intro gate / post-LLM outro hook in `process_message` | Earlier draft of this spec. Replaced by handler enrichment (`transition_phase`, `END_BREAK`) because handlers already own the deterministic boundary signal and avoid surgery on `process_message`'s core flow |
| Multi-message coach response shape (response carries a list of coach messages) | Earlier draft of this spec. Not needed once the outro/intro card rides on the same `ChatMessage` row as the LLM's transition text via `component_config` |
| Per-session context key + prompt gates | Not needed once videos are server-injected. The LLM never sees video state |
| Narrative-only break / no break state | Break is a real, backend-tracked, soft-blocking concept |
| `current_session` field on `CoachState` | Derivable from `current_phase` + `SESSIONS` map |
| Parallel `SessionType` enum | Sessions live as metadata next to `CoachingPhase`, not as a parallel enum |
| Exposing the raw `shown_videos` array as a context key | Moot — no context key at all in current design |
| Full inline `<video>` player as the persistent component | Clogs chat history. Thin card + modal instead |
| New `Video` DB model | Set is small and fixed; static registry is enough |
| Serving video through Django | Will choke backend workers. S3 direct |
| Recording video as "shown" on display | Refresh mid-video would skip the gate. Record on acknowledgment |

## Resolved questions (previously open)

1. **Modal close behavior** — modal renders a Continue button that's disabled until 20s before the video ends (or the 50% mark for videos shorter than 30s). ACK fires on Continue click. Closing the modal early via Esc/backdrop is allowed and fires no action.
2. **Video file naming** — files renamed on disk to match session keys (see Sessions & videos table above). Registry maps `video_key → {name, url}`; filename and key are kept in sync as a convention.
3. **Outro turn response shape** — the outro card rides on the same `ChatMessage` as the LLM's transition text via `component_config`. The `transition_phase` action handler attaches the component when it runs; no new message row is created and no multi-message response shape is needed. See Decision 6.B and the lifecycle walkthrough.

## Edge cases explicitly out of scope for v1

- Mid-watch chat reload showing an "unacked" video in serialized history (rare; serialization helper just renders "User has not watched it yet" — no special UX).
- Modal early-close + retry flow optimization.
- Anything beyond the threshold-Continue / Watch-Again / composer-disable behavior.

## Net surface area to build

| Piece | Notes |
|---|---|
| **`SESSIONS` map + helpers** | In `server/enums/coaching_phase.py` |
| **Migration: `shown_videos`** | ArrayField on `CoachState` |
| **Migration: `Break` model** | `user`, `started_at`, `ended_at`, `triggered_by_session`, `coach_message` |
| **Video registry** | Static dict `video_key → { name, url }` |
| **`transition_phase` handler enrichment** | After phase change, consult `SESSIONS` map and return outro component (if leaving a session with an outro) or intro component (if leaving a session without an outro and entering one with an unacked intro). Outro wins over intro on precedence. Component attaches to the LLM's coach response message via existing `component_config` field. |
| **`END_BREAK` handler enrichment** | After closing break, if `current_phase` is first phase of a session with an unacked intro, return the intro component. Triggers skip-LLM rule. |
| **`ensure_initial_message_exists` rewrite** | Seed welcome video card (text="", no greeting) instead of `INITIAL_MESSAGE` text. Delete the `INITIAL_MESSAGE` constant. |
| **`process_message` null-message contract** | Accept `message: None` programmatically (no user ChatMessage saved; user actions still apply). `message=""` still treated as a real user message. Skip-LLM rule: skip iff a user action returned a `component_config`. |
| **`get_recent_chat_messages_for_prompt` rewrite** | Serialize `component_config` into bracketed descriptions for the LLM (including coach messages that have both text and a component). Bump default count from 5 → 10. |
| **Action: `ACKNOWLEDGE_SESSION_VIDEO(video_key)`** | Appends to `shown_videos`; key set by server, not LLM |
| **Action: `START_BREAK(session_key)`** | Creates Break row (`triggered_by_session = session_key`), returns SESSION_BREAK component. `session_key` is set by the server when building the outro card's button. |
| **Action: `END_BREAK()`** | Stamps `ended_at` on open Break, optionally returns intro video component (Decision 6.C) |
| **ActionType enum** | 3 new values |
| **ComponentType enum** | 2 new: `SESSION_VIDEO`, `SESSION_BREAK` |
| **API field** | `on_break: bool` on coach response AND user-state endpoint |
| **React: video card** | Thin card + modal player with threshold-gated Continue button (20s before end, or 50% for short videos); same component drives active (Watch) and persisted (Watch Again) state |
| **React: break card** | "I'm Ready" button (canned-response pattern: dispatches `{message: "I'm ready", actions: [END_BREAK()]}`); composer disabled while open via `on_break` |
| **React: composer disable rule** | Disable composer when latest coach message is an unacked SESSION_VIDEO, OR when `on_break === true` |
| **S3 upload** | One-time upload of the 12 video files |
| **Docs update** | Update `docs/docs/coach/phases.md`, `docs/docs/core-systems/action-handler/actions/transition-phase.md`, `docs/docs/core-systems/component-renderer/persistent-components.md`, plus new action docs for ACK / START_BREAK / END_BREAK. |
| **Procedure doc** | NOP-style "Add a Session Video" Procedures MCP doc. First-class deliverable. |

**Explicitly NOT in scope:** prompt edits, per-session context key, SHOW actions, pre-LLM gate / post-LLM hook in `process_message`, multi-message response shape. The LLM is untouched (the serialization helper is a *read-side* shim, not a prompt edit).

## Pointers to existing Procedures docs the next agent should read first

- `system / dev-coach / coach / phases`
- `system / dev-coach / core-systems / component-renderer / persistent-components`
- `system / dev-coach / core-systems / component-renderer / overview`
- `system / dev-coach / core-systems / action-handler / overview`
- `system / dev-coach / core-systems / action-handler / actions / transition-phase`

## Next step in the workflow

The PR breakdown lives at [`notes/coaching-phase-videos-prs.md`](./coaching-phase-videos-prs.md). The lifecycle walkthrough above is the ground truth for the runtime flow; the Net surface area table is the ground truth for what to build.

Non-negotiable instructions for implementation:

1. Treat the session/video mapping as mutable data. Nothing outside the `SESSIONS` map / video registry should name specific videos or sessions.
2. The plan must produce the "Add a Session Video" Procedures MCP doc alongside the code PRs.
3. The break is part of the flow — not a stretch goal.
4. **Do not add SHOW video actions, context keys, prompt edits, pre/post-LLM injection hooks in `process_message`, or multi-message response shapes.** Videos are server-injected via action handlers. The only LLM-facing change is the read-side serialization helper in `get_recent_chat_messages_for_prompt`.
5. Preserve the `message: None` vs `message: ""` distinction in `process_message` — `None` is programmatic-only, `""` is treated as a real user message.
6. The outro/intro card rides on the same `ChatMessage` row as the LLM's transition text via `component_config`. Do not introduce a list-of-coach-messages response shape.
