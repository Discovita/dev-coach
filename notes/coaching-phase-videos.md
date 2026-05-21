# Coaching Phase Videos — Brain Dump

## Purpose

Show Leigh Ann's pre-recorded videos to clients at the **start and end of certain coaching phases**. Intro videos preview what's coming; outro videos explain the value of taking a break before the next group of phases begins.

The videos appear inline in the chat window like part of the conversation. The user can revisit any previously shown video.

## Core design decisions (locked)

### 1. "Sessions" do not exist in code

Sessions are a **developer concept** for thinking about which videos belong together. They never manifest in models, enums, config maps, or migrations.

What actually exists in code: **phases**, some of which have an intro video, an outro video, both, or neither. Whether two videos are "the same session" is only meaningful to humans writing prompts and naming files.

### 2. Video keys are `<phase>_<position>`

Every video has a unique key of the form `<phase_value>_intro` or `<phase_value>_outro`. Examples:

- `identity_brainstorming_intro`
- `identity_brainstorming_outro`
- `i_am_statement_intro`
- `i_am_statement_outro`

This string is:
- The key in the `shown_videos` array on `CoachState`
- The parameter to the action that shows / acknowledges a video
- The lookup key in the static video registry

### 3. Storage on CoachState mirrors `asked_questions`

Add a new field to `CoachState`:

```python
shown_videos = ArrayField(
    models.CharField(max_length=255),
    default=list,
    blank=True,
    help_text="List of session video keys the user has acknowledged.",
)
```

One migration. No `Video` DB model. No `Session` model.

### 4. The video registry is a static Python config

A static `dict` (or similar) maps `video_key → { name, url, phase, position }`. Lives somewhere in `server/` (likely under `enums/` or `services/` — decide during implementation).

Example shape:

```python
SESSION_VIDEOS = {
    "identity_brainstorming_intro": {
        "name": "Identity Brainstorming Intro",
        "url": "https://<bucket>.s3.amazonaws.com/...",
        "phase": CoachingPhase.IDENTITY_BRAINSTORMING,
        "position": "intro",
    },
    ...
}
```

No DB model. No admin editing. The set of coaching videos is small and fixed; if non-developers ever need to edit it, we can promote to a `Video` model later.

### 5. Video hosting: S3, same pattern as user images

Don't serve videos through Django/Gunicorn — workers streaming large files will choke the backend. Use the same S3 setup that already hosts per-user images. The frontend `<video src>` streams directly from S3 (HTTP range requests work, so basic seeking is supported). Add CloudFront later if mobile scrubbing is bad.

Files to upload are in `/Users/work/Downloads/NeoVita Video Files/`.

### 6. Two new actions

**`SHOW_SESSION_VIDEO(video_key)`**
- Returns a persistent `ComponentConfig` of type `SESSION_VIDEO`
- Looks up `name` / `url` from the registry
- Component is rendered in the chat as a **thin card**, not an inline player (see UI section below)

**`ACKNOWLEDGE_SESSION_VIDEO(video_key)`**
- Appends `video_key` to `coach_state.shown_videos`
- This is the **gate**. Recording happens on acknowledgment, NOT on display, so a refresh mid-video doesn't skip the gate.
- Idempotent (no duplicates).

### 7. The acknowledgment is what unblocks the coach

The video's "Continue" button (or auto-fire on the player's `ended` event — frontend's choice) carries the acknowledgment action.

- **Intro video** Continue button → `[ACKNOWLEDGE_SESSION_VIDEO]`. Coach then proceeds with phase content.
- **Outro video** Continue button → `[ACKNOWLEDGE_SESSION_VIDEO, transition_phase]`. Records + advances to the next phase. This is the documented multi-action persistent-component pattern — persistence-style action goes first.

### 8. Per-phase context key (NOT a generic boolean, NOT the array)

Add ONE new context key whose getter is phase-scoped. It reads `coach_state.current_phase`, consults the registry to find that phase's intro and/or outro video(s), and renders zero/one/two lines naming the specific video by name and its seen status.

Proposed key name: `session_video_status` (open to better names — pick during implementation).

Example renderings:

For Identity Brainstorming, before intro is acknowledged:
```
Identity Brainstorming intro video — seen: No
```

For a phase with no videos:
```
(no session videos for this phase)
```

The prompt author writes the gate sentence ("IMPORTANT - do not proceed until the intro video is shown") above the context key in the phase's prompt. The context key supplies only the named status.

**Critical:** the raw `shown_videos` array is never exposed to a prompt. Per-phase resolution lives in the getter.

### 9. UI: thin card + modal player

Don't put a full `<video>` player inline in the chat — it'd clog history visually.

**Active state (latest message, not yet acknowledged):**
- Renders a thin card: `<Video Name>` + `[ Watch ]` button
- Clicking opens a modal containing the `<video>` element
- On video `ended` (or modal Continue button), fires the acknowledgment action
- Modal closes; coach proceeds

**Persisted state (historical, replayable):**
- Identical thin card: `<Video Name>` + `[ Watch Again ]` button
- Same modal player, but **no backend action attached** — purely a frontend modal-opener
- The persisted `component_config` stored on `ChatMessage` only needs `{ video_name, video_url }`

**Deviation from existing convention to flag:** The current persistent-components docs say to strip ALL buttons from historical components. We're keeping a `Watch Again` button, but it's frontend-only (opens a modal; no backend interaction). Worth a one-line callout in the spec so it doesn't look like a mistake.

### 10. The "break" between sessions is purely narrative

No break screen. No timer. No state.

The outro video's *content* tells the client to pause as long as they need. Whenever they return and engage, the next phase's prompt gate fires and the next intro video plays. The pause = the user closing the app, exactly what the outro instructs.

## Rejected alternatives (do not re-propose)

| Idea | Why rejected |
|---|---|
| `current_session` field on CoachState | Sessions don't exist in code; derivable from `current_phase` if ever needed |
| `SESSIONS` map / enum | Same — sessions are a human concept, not a code one |
| Generic `INTRO_VIDEO_SEEN` / `OUTRO_VIDEO_SEEN` booleans | Confusing — "which one?" Replaced with self-describing phase-scoped status that names the video |
| Exposing the raw `shown_videos` array as a context key | Invites prompt mistakes — each prompt only cares about its own phase's videos |
| Full inline `<video>` player as the persistent component | Clogs chat history visually. Replaced with thin card + modal |
| Break screen / timer / locked state between sessions | Pause is narrative-only; user decides when to come back |
| New `Video` DB model | Set of videos is small and fixed; static registry is enough |
| Serving video through Django | Will choke backend workers. S3 direct |
| Recording video as "shown" on display | Refresh mid-video would skip the gate. Record on acknowledgment instead |

## Video inventory

Files at `/Users/work/Downloads/NeoVita Video Files/`:

| File | Likely phase | Likely position |
|---|---|---|
| `welcome video 1.mov` | Introduction | intro (part 1?) |
| `Welcome video 2.mov` | Introduction | intro (part 2?) |
| `Welcome video outro .mov` | (end of opening session) | outro |
| `identity branstorming intro .mov` | Identity Brainstorming | intro |
| `identity brainstorming outro.mov` | Identity Brainstorming | outro |
| `identity refienement intro.mov` | Identity Refinement | intro |
| `identity refinement outro.mov` | Identity Refinement | outro |
| `identity commitment intro.mov` | Identity Commitment | intro |
| `identity commitment outro.mov` | Identity Commitment | outro |
| `I am statement intro .mov` | I Am Statement | intro |
| `i am statements outro.mov` | I Am Statement | outro |
| `Movie on 5-7-26 at 5.38 PM.mov` | unknown | unknown |

Phases with **no** video (per current inventory): `get_to_know_you`, `identity_warm_up`, `brainstorming_review`, `anything_missing`, `identity_visualization`. The registry simply omits them.

## Open questions for the next agent / for Casey

1. **welcome video 1 vs welcome video 2** — sequential parts of the Introduction intro, or one is for a different phase (e.g., Get To Know You)?
2. **Welcome video outro** — which phase's *exit* does this play on? End of Introduction? End of Identity Warm-Up? (This is the boundary of the first "session".)
3. **Movie on 5-7-26 at 5.38 PM.mov** — what is this? A re-record, a test, a real phase video, or trash?
4. Are the silent phases above truly silent, or are some of those waiting on videos Leigh Ann hasn't sent yet?
5. Confirm the static registry approach is right vs. promoting to a `Video` model (likely Yes — static is enough for now).
6. Confirm the deviation from the "strip all buttons from historical components" convention (the `Watch Again` modal-opener button) is acceptable.
7. Final name for the new context key (`session_video_status` is a placeholder).
8. Modal close behavior — does the Continue button fire on `ended`, on click, or both?

## Net surface area to build

| Piece | Notes |
|---|---|
| **DB migration** | Add `shown_videos` ArrayField to `CoachState` |
| **Video registry** | Static Python dict; one module |
| **Action** | `SHOW_SESSION_VIDEO(video_key)` — returns ComponentConfig of type `SESSION_VIDEO` |
| **Action** | `ACKNOWLEDGE_SESSION_VIDEO(video_key)` — appends to `shown_videos`, idempotent |
| **Action enum** | Two new `ActionType` values |
| **Component type enum** | One new `ComponentType.SESSION_VIDEO` |
| **Context key** | One new per-phase status key (e.g., `session_video_status`) + its getter |
| **React component** | Thin card + modal player; same component drives active and persisted |
| **Persistence** | Reuses existing `component_config` on `ChatMessage` and dual-rendering detection |
| **Prompt edits** | Each phase that has an intro/outro video: a gate paragraph at top (intro) and instruction on completion (outro) |
| **S3 upload** | One-time upload of video files to the existing S3 bucket |

## Pointers to existing Procedures docs the next agent should read first

- `system / dev-coach / coach / phases` — the full phase model
- `system / dev-coach / core-systems / component-renderer / persistent-components` — the persistence pattern this feature reuses
- `system / dev-coach / core-systems / component-renderer / overview` — base component system
- `system / dev-coach / core-systems / action-handler / overview` — action registry pattern
- `system / dev-coach / core-systems / prompt-manager / context-keys / asked-questions` — the gate pattern this mirrors
- `system / dev-coach / core-systems / action-handler / actions / update-asked-questions` — the storage pattern this mirrors
- `system / dev-coach / core-systems / action-handler / actions / transition-phase` — what the outro button's second action invokes

## Next step in the workflow

Per the standard workflow: feed this brain-dump to the `/decompose` agent to break it into atomic PRs (likely: 1) DB migration + video registry, 2) actions + component type, 3) frontend component + modal, 4) context key + prompt edits, 5) S3 upload + final wiring — but decompose will decide).
