# How to Add, Replace, Move, or Remove a Session Video

The Coaching Phase Videos system is architected as **mutable data**: the set of videos and where they play live in two registries (a Python dict each) plus files on S3. The vast majority of changes need no code changes beyond editing those registries — no migrations, no enum updates, no prompt edits, no frontend work.

## Lifecycle in 5 bullets

1. **Storage** — Each video file lives in S3 under `media/session-videos/`. The same `s3_key` is uploaded to both the staging and production buckets.
2. **Registry** — `server/apps/coach_states/constants/session_videos.py` maps each `video_key` (e.g. `"welcome_session_intro"`) to `{name, s3_key}`.
3. **Placement** — `server/enums/coaching_phase.py` declares the `SESSIONS` map: each session lists its phases and points to an `intro` / `outro` `video_key` (either can be `None`).
4. **Injection** — Server-side action handlers ([`transition_phase`](/docs/core-systems/action-handler/actions/transition-phase) when the LLM transitions, [`end_break`](/docs/core-systems/action-handler/actions/end-break) after a break closes, plus a welcome seed at chat creation) consult `SESSIONS` and emit a `SESSION_VIDEO` component card. **The LLM never decides when a video plays.**
5. **Display** — The frontend's `SessionVideoCard` reads `video_name` and `video_url` straight off the persisted `component_config` — no FE registry. Click Watch → modal player → threshold-gated Continue → `ACKNOWLEDGE_SESSION_VIDEO` records the key in `coach_state.shown_videos` so it isn't re-shown.

See [`docs/coach/phases.md`](/docs/coach/phases#coaching-sessions) and [Persistent Components](/docs/core-systems/component-renderer/persistent-components#coaching-phase-videos--session_video-and-session_break) for the underlying architecture.

---

## Replace a video file (most common case)

You're swapping the actual video content for an existing `video_key` (e.g. Leigh Ann re-recorded the brainstorming intro).

1. **Drop the new file** into the local `videos/` directory at the repo root, named to match the existing `s3_key` (e.g. `04-brainstorming-session-intro.mov`). `videos/` is gitignored — files don't get committed.
2. **Upload to S3** for both environments:
   ```bash
   python scripts/upload_session_videos.py --profile dev-coach --force
   ```
   `--force` overwrites the existing S3 object. Without it the script skips keys that already exist.
3. **Done.** No registry edit, no code change. Existing chat history replays the new file because the `s3_key` is unchanged and the URL is resolved per-request from the bucket.

> **Bucket-snapshot caveat**: persisted `component_config` rows carry the *full URL* that was current when the card was first rendered. If you ever change the bucket name (not the `s3_key`), historical rows keep pointing at the old bucket until rebuilt. Not a concern for normal file swaps — only for bucket migrations.

---

## Move a video (change which session it plays in, or swap intro ↔ outro)

You're keeping the file but changing **where** in the flow it appears.

1. **Edit the `SESSIONS` map** in `server/enums/coaching_phase.py`. Reassign the `intro` or `outro` field of the relevant session entry to the `video_key` you're moving.
2. **No registry edit** — the `video_key` and `s3_key` are unchanged.
3. **Mind acked state**: `coach_state.shown_videos` records video keys the user has already watched. Moving a video to a different boundary means users who acked it at the old boundary won't see it at the new one. If you want every user to re-see the video, also change its `video_key` (which is the "Add" path below).

Example — swap which video introduces the brainstorming session:

```python
"brainstorming_session": {
    "phases": [
        CoachingPhase.IDENTITY_BRAINSTORMING,
        CoachingPhase.BRAINSTORMING_REVIEW,
    ],
    "intro": "alternate_brainstorming_intro",  # ← changed
    "outro": "brainstorming_session_outro",
},
```

---

## Add a new video

You're introducing a video at a new boundary (or under a brand-new session).

1. **Pick a `video_key`.** Convention: `<session_key>_intro` or `<session_key>_outro`. The `_session` suffix on session names keeps keys unambiguous vs. phase values.
2. **Drop the file** into `videos/` with a numeric prefix matching the play order, e.g. `13-some-new-session-intro.mov`. (The number is just for human readability when listing — the code doesn't depend on it.)
3. **Add the registry entry** in `server/apps/coach_states/constants/session_videos.py`:
   ```python
   "some_new_session_intro": {
       "name": "Some New Session Intro",
       "s3_key": "media/session-videos/13-some-new-session-intro.mov",
   },
   ```
4. **Place it in `SESSIONS`** in `server/enums/coaching_phase.py`. Either reuse an existing session and assign its `intro` / `outro`, or add a new session:
   ```python
   "some_new_session": {
       "phases": [CoachingPhase.SOME_NEW_PHASE],
       "intro": "some_new_session_intro",
       "outro": None,
   },
   ```
   > Creating a brand-new session also means adding the underlying `CoachingPhase` enum value (a backend code change, prompt content updates, etc.) — that's outside the scope of this guide. Adding videos to *existing* sessions is the no-code-change path.
5. **Upload to S3**:
   ```bash
   python scripts/upload_session_videos.py --profile dev-coach
   ```
   The script reads the registry, so the new entry is automatically picked up.
6. **Done.** Next user reaching that boundary sees the card.

---

## Remove a video

1. **Delete the entry** from `SESSIONS` (set `intro` or `outro` to `None`) — that stops future injection.
2. **Optional**: delete the entry from `SESSION_VIDEOS` and the file from S3 if no historical chat history needs to replay it. Persisted `component_config` rows from before removal will 404 the video URL once the S3 file is gone but will still render the card with the Watch button.

---

## Verification

After any change, hit the public endpoint to confirm the feature is enabled and the file is reachable:

```bash
curl https://discovita-dev-coach-staging.s3.amazonaws.com/media/session-videos/<your-key>.mov -I
# 200 expected
```

Then walk a test user through the boundary in the staging UI to confirm the card emits and plays. The [test scenario freeze button on `/chat`](/docs/core-systems/component-renderer/persistent-components#coaching-phase-videos--session_video-and-session_break) makes capturing a reproducible scenario for the new boundary easy.
