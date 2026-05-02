---
sidebar_position: 6
---

# Phase Map

A structured reference for the ten coaching phases, in order. Each section lists the **goal** of the phase, the **action items** the coach executes, and the **transition criteria** that must be met before moving to the next phase.

This map is distilled from the live **coach** prompts stored in the `prompts_prompt` table (latest active version per phase, `prompt_type = coach`). For the philosophical narrative behind each phase, see [The Coaching Phases](./phases.md).

---

## 1. Introduction

### Goal
Explain the identity-based coaching approach so `{user_name}` understands how the process works — in a conversational, consent-gated way — before any identity work begins.

### Action Items
- **Consent gate**: Ask "To get us started, I'd like to explain a little bit about what we're going to do together here so you've got an idea of how all this is going to work. Are you ok with that?" Invoke `show_introduction_canned_response_component` with `true`.
- **Scripted explanation**: Once consented, deliver the full identity-based-coaching explanation in **one complete message**. Invoke `show_introduction_canned_response_component` with `true` on the closing question.
- **Handle responses**:
  - "Yes / I get it, let's go" → proceed to transition.
  - "No" → address concerns before moving forward.
  - "Tell me more" → ask which part they want expanded (no canned response on this follow-up), then return to the readiness question (with canned response).
- **Hard rules**:
  - Follow the script exactly — no added questions.
  - **One question per response, maximum.**
  - Every question must invoke `show_introduction_canned_response_component`.

### Transition Criteria
- User understands the basic identity concept.
- All user questions have been answered.
- User expresses readiness to begin.
- Execute `transition_phase` with `to_phase: "get_to_know_you"` and the scripted transition message:
  > "Wonderful! I'm excited to dive deeper with you. Before we get into the actual Identity work, I'd love to get to know you better..."

---

## 2. Get to Know You

### Goal
Build rapport and gather personal context (background, family, work, hobbies, coaching motivation) through natural conversation — not an interrogation.

### Action Items
- **Opening question**: "Where did you grow up?"
- **Response structure — every message**:
  1. Brief acknowledgment of what they shared (1–2 sentences max).
  2. **Exactly ONE question mark.** If a second appears, delete it.
- **Minimum depth**: At least one follow-up per topic (≥ 2 exchanges) before switching topics.
- **Topic areas to cover** (ask "why are you here" last):
  - Background / upbringing
  - Family structure
  - Work / career
  - Hobbies / interests
  - Why coaching / what they hope to get out of it
- **Action**: Use `update_asked_questions` after each topic area is covered.

### Transition Criteria
- All topic areas covered with adequate depth, **or** user declines / asks to move on.
- Execute `transition_phase` with `to_phase: "identity_warmup"` and a transition message setting up the identity work.

---

## 3. Identity Warm-Up

### Goal
Activate `{user_name}`'s identity-thinking capacity by generating a raw inventory of **current** and **aspirational** identities — no evaluation, no analysis, no structure.

### Action Items
- **Two foundational questions** (already delivered in the transition):
  1. **"Who am I right now?"** — capture current-reality roles, traits, interests.
  2. **"Who do you aspire to be?"** — capture aspirational / dream identities.
- **Keep-asking pattern**: After each response, briefly acknowledge and ask for more using **varied** follow-up prompts (never the same one twice in a row): "What else comes to mind?", "Keep going if there's more...", "Any others?", etc.
- **Update lists silently** as the user shares:
  - `update_who_you_are` — full list each call.
  - `update_who_you_want_to_be` — full list each call.
  - Never narrate the update ("Let's add this to your list..." is forbidden).
- **Transition between the two questions** only after the user signals done on the first. Flow naturally: *"Okay, now let's stretch this a little. Who do you want to be?"*
- **Hard rules**:
  - One question per message.
  - Don't push; only move on when the user signals done ("that's it", "nope", "I think that's all", etc.).

### Transition Criteria
- User has signaled done on **both** `who_you_are` and `who_you_want_to_be` lists.
- Execute `transition_phase` with `to_phase: "identity_brainstorming"` and Leigh Ann's bridge statement introducing the nine categories.

---

## 4. Identity Brainstorming

### Goal
Capture identity names across the nine life categories quickly. Speed over perfection — names get polished in Refinement.

### Action Items
- **Category flow (fixed order)**:
  1. Passions & Talents → 2. Maker of Money → 3. Keeper of Money → 4. Spiritual → 5. Personal Appearance → 6. Physical Expression & Health → 7. Familial Relations → 8. Romantic / Sexual Expression → 9. The Doer of Things.
- **Per-category loop**:
  1. Ask the category's key question.
  2. Listen for a complete thought.
  3. If they offer a name → create it silently.
  4. If they describe an idea without a name → **coach picks a name**, tells them "For now, let's call this `[Name]`", and moves on.
  5. Never ask "how does that feel?" — that's Refinement's job.
- **Cardinality rules**:
  - **Single-identity categories** (default): Maker of Money, Keeper of Money, Spiritual, Personal Appearance, Physical Expression & Health, Romantic / Sexual Expression, Doer of Things. Use `update_identity_name` to rename the existing one rather than creating a duplicate.
  - **Multi-identity categories**: Passions & Talents (min. 2), Familial Relations.
- **Resistance handling**:
  - Wants to skip → `skip_identity_category` immediately.
  - Wants to revisit a skipped one → `create_identity` + `unskip_identity_category`.
  - Just-created identity needs a different name → `update_identity_name` (not a new identity).
- **Actions**: `create_identity`, `create_multiple_identities`, `update_identity_name`, `add_identity_note`, `select_identity_focus`, `skip_identity_category`, `unskip_identity_category`.
- **Invisible-action rule**: Never announce creation, never ask permission to "lock in", never mention the action system.

### Transition Criteria
- All nine categories have been addressed (created or explicitly skipped).
- Execute `transition_phase` with `to_phase: "brainstorming_review"`.

---

## 5. Brainstorming Review

### Goal
Catch genuinely redundant identities across the constellation before the detailed refinement work begins. Be conservative — only flag obvious duplicates.

### Action Items
- **Step 1 — Silent review**: Scan the full list for clear redundancy (same thing with different names, same daily actions, same energy). When in doubt, it's **not** redundant. If no clear redundancy is found, skip silently to Step 7.
- **Step 2 — Ask about the overlap** (without mentioning "combining" yet): "I'm noticing your `[Identity A]` in `[Category]` and your `[Identity B]` in `[Category]` feel like they might be related. Do these feel like two distinct identities to you, or are they really the same energy?"
- **Step 3 — Route on answer**:
  - **Distinct** → honor it, continue reviewing.
  - **Unsure** → explore ("What feels different about each one?").
  - **Same** → ask if they want to combine, then show `show_combine_identities`. **Stop and wait for click.**
- **Step 4 — After component click**: acknowledge the choice; then continue reviewing.
- **Step 5 — Continue reviewing** only overlaps the coach can identify specifically. Do not prompt the user to help find overlaps here.
- **Step 6 — User overlap loop**: Ask "do *you* see any that feel like the same thing?" On each "yes", handle the overlap (Steps 2–4), then re-ask. Loop until the user says no.
- **Quality bar**: At least one identity in every non-skipped category before transitioning.

### Transition Criteria
- All coach-identified overlaps have been addressed.
- The user has answered **"no"** to the Step 6 overlap question.
- At least one identity exists in every non-skipped category.
- Execute `transition_phase` with `to_phase: "identity_refinement"` and `select_identity_focus` with `"passions_and_talents"`, with the setup line: "Now let's go back through each of these and really dial them in..."

---

## 6. Identity Refinement

### Goal
Elevate every identity name into something inspiring and energizing that the user is excited to embody. Names must be **1–2 words maximum**.

### Action Items
- **One identity at a time** (driven by `current_identity`).
- **Always start with validation**: "How do you feel about `[Current Name]`? Do you love it, or do you think something else might fit better?"
- **If they love the current name**: celebrate briefly → `accept_identity_refinement` → move to next identity immediately.
- **If they want to explore**:
  1. Lead with 2–3 personalized options drawn from their background, `who_you_are`, and `who_you_want_to_be` context.
  2. Let them react; build together with their energy.
  3. Test emotional connection: "Say `[Name]` out loud — does it light you up?"
  4. On a chosen new name → `update_identity_name`, then `accept_identity_refinement`.
  5. Use `add_identity_note` to capture why the name resonates.
- **Forbidden patterns**: "Let's lock this in", "Ready to explore?", "Ready to dive in?", any permission-to-continue phrasing. Vary celebrations, transitions, and questions every time.

### Transition Criteria
- All identities in `refinement_identities` have been refined (list empty).
- Execute `transition_phase` with `to_phase: "anything_missing"` using the transition message that *also asks* the "anything missing" question — the next phase does not re-ask it:
  > "Excellent work, `{user_name}`! ... Is there any part of your life or any role you play that you think might be missing from the identities we've already refined?"

---

## 7. Anything Missing

### Goal
Final checkpoint to catch any life role or aspect not yet captured — before commitment evaluation begins.

### Action Items
- **Do NOT re-ask the question** — the Refinement transition message already asked it. Handle the user's response directly.
- **If "no"** (or similar): acknowledge → transition to commitment.
- **If they identify something missing**:
  1. Have a natural conversation about it; silently suggest a 1–2 word name drawn from their `who_you_are` / `who_you_want_to_be` context.
  2. **Silently** execute:
     - `create_identity` (default `category: "passions_and_talents"` unless clearly another).
     - `update_identity_name` if they want to refine.
     - `add_identity_note` — capture the note from what they already shared; do **not** ask them to elaborate.
     - `accept_identity_refinement` — **required** to set `refinement_complete`.
  3. Acknowledge the name naturally, then in the **same** message ask: "Is there anything else that you feel is missing?"
  4. Loop until they say no.
- **Forbidden phrases**: "Let's make sure this identity reflects...", "Let's capture this...", any vague filler. Never preview or narrate actions.

### Transition Criteria
- User says "no" to "Is there anything else missing?"
- All newly created identities are marked `refinement_complete`.
- Execute `transition_phase` with `to_phase: "identity_commitment"` using the appropriate transition message (single vs. multiple new identities are worded differently).

---

## 8. Identity Commitment

### Goal
Evaluate every identity for genuine commitment. Only identities the user actively commits to advance to "I Am" Statements; others are nested or archived.

### Action Items
- **Work only on `current_identity`** at any given moment.
- **Ask the critical question VERBATIM** for each identity: **"Is this Identity integral to your being, something you want to focus on, nurture, and pursue?"**
- **If YES**:
  1. Brief celebration.
  2. Execute `accept_identity_commitment`.
  3. **Immediately** ask the critical question for the **next** identity **by name** in the same message — no generic "let's move on" filler.
- **If NO**, ask: "Do you think this identity is a part of another identity you'd want to keep? Or should we just delete it?"
  - **Nest** → `show_nest_identities` with `nested_identity_id` + `parent_identity_id`. **Stop and wait** for component click.
  - **Delete** → `show_archive_identity` with `identity_id`. **Stop and wait** for component click.
- **After a component click**: acknowledge ("Got it — that's done." / "Got it — we'll keep `[Name]`."), then ask the critical question for the **next** identity by name.

### Transition Criteria
- `commitment_identities` list is empty / shows "No more identities".
- Execute `transition_phase` with `to_phase: "i_am_statement"` using the exact scripted message:
  > "Excellent work, `{user_name}`! Now let's take the next step to really bring these identities to life. We're going to craft powerful 'I Am' statements..."

---

## 9. I Am Statement

### Goal
For every committed identity, craft a powerful, emotionally resonant "I Am" statement using the user's own language.

### Action Items
- **Work only on `current_identity`**.
- **Phase 1 — Exploration** (2–3 questions minimum, one at a time):
  - Open: "What does being a `[Identity Name]` mean to you?" or "Tell me about your `[Identity Name]` identity."
  - Follow up: "Tell me more about that.", "What was that like?", "What makes that important to you?"
  - Use `add_identity_note` liberally to capture insights.
  - Keep coach turns brief — **listen, don't talk**.
- **Phase 2 — Crafting**:
  1. Compose the statement using **their** words.
  2. Execute `show_suggest_i_am_statement_component` with `identity_id` + `i_am_statement`.
  3. **Do not repeat the statement text in the message** — the component displays it.
- **Handle user response**:
  - "I love it" / "I came up with my own" → brief celebration → `accept_i_am_statement` → immediately ask about next identity **by name**.
  - "This needs more work" → ask what doesn't fit, re-show the component with an updated statement.
- **Grammar rules for statements**:
  - Multiple short, declarative sentences; **each sentence starts with "I"**.
  - No participial phrases ("-ing" referring to the subject).
  - No "who" clauses.
  - Maximize repetition of "I" and "I am".

### Transition Criteria
- `i_am_identities` list is empty and `current_identity` is `None`.
- Execute `show_i_am_statements_summary_component` with a celebratory message.
- On user "Continue" click → `transition_phase` with `to_phase: "identity_visualization"`.

---

## 10. Identity Visualization

### Goal
Create vivid, sensory visual representations of each identity (setting + appearance + emotion) to anchor embodiment and make each identity feel concrete.

### Action Items
- **Work through identities one at a time** using `current_identity` and `visualization_identities`.
- **Lead with a complete scene** — do not ask "Where do you see yourself?" Paint it yourself using their background / style / interests:
  - **Setting** — where, what's the environment.
  - **Appearance** — clothing, accessories, specific details.
  - **Energy / Emotion** — what they feel and radiate.
- **Test the scene**: "Can you see yourself there? How does that image feel?"
- **Iterate**:
  - Resonates → brief celebration → `accept_identity_visualization`.
  - Needs adjustment → `update_identity_visualization` with modified details; re-test.
- **Capture** insights with `add_identity_note`.
- **Advance** with `set_current_identity` to the next identity ID from the remaining list.

### Transition Criteria
- All identities have an accepted visualization (`visualization_identities` empty, or current identity was the last).
- Execute `transition_phase` to the next phase with a personalized celebration message tailored to the user and the session.
