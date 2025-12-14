# Anything Missing Phase Implementation To-Do List

## Overview
Extract the "Is there anything missing?" functionality from the Identity Commitment phase into its own dedicated phase. This phase will be inserted between Identity Refinement and Identity Commitment.

## Phase Flow
**Current:** Identity Refinement → Identity Commitment  
**New:** Identity Refinement → Anything Missing → Identity Commitment

## Progress Summary
- ✅ Backend enum added
- ✅ Frontend enum added (with display name and color)
- ✅ Prompt created in database
- ✅ Transition messages documented in Phase_Transition_Messages.md
- ✅ Coach phases documentation updated
- ✅ Django migrations created and applied
- ⏳ Identity Refinement prompt needs update (change transition target to anything_missing)
- ⏳ Identity Commitment prompt needs update (remove "Is anything missing?" section)
- ⏳ Additional documentation updates
- ⏳ Testing

---

## 1. Backend Enum Updates

- [x] Add new phase to `server/enums/coaching_phase.py`
  - Add `ANYTHING_MISSING = "anything_missing", "Anything Missing"` to `CoachingPhase` enum
  - Place it between `IDENTITY_REFINEMENT` and `IDENTITY_COMMITMENT`

- [x] Create and run Django migration for the new phase
  - Migration will update `CoachState.current_phase` choices
  - Migration will update `Prompt.coaching_phase` choices
  - ✅ Migrations created: `0016_alter_coachstate_current_phase.py` and `0017_alter_prompt_coaching_phase.py`
  - ✅ Migrations applied successfully to local database

---

## 2. Frontend Enum Updates

- [x] Add new phase to `client/src/enums/coachingPhase.ts`
  - Add `ANYTHING_MISSING = "anything_missing"` to `CoachingPhase` enum

- [x] Add display name to `COACHING_PHASE_DISPLAY_NAMES`
  - Add `[CoachingPhase.ANYTHING_MISSING]: "Anything Missing"`

- [x] Add color to `COACHING_PHASE_COLORS`
  - Choose appropriate color scheme (suggest: similar to brainstorming review or commitment phase)
  - Added: `bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200`

---

## 3. Prompt Creation

- [x] Create initial prompt for the new phase in the database using Dev Coach MCP server
  - **IMPORTANT**: Prompts are NOT file-based - they must be created directly in the database using the `create_new_coach_prompt` MCP tool
  - Use the Dev Coach MCP server to create the prompt with:
    - `coaching_phase`: "anything_missing"
    - `name`: "Anything Missing"
    - `description`: Brief description of the phase purpose
    - `body`: Full prompt content (see below)
    - `required_context_keys`: Array of context keys needed
    - `allowed_actions`: Array of action types allowed
  - Required context keys:
    - `user_name`
    - `identities` (to show what they already have)
    - `who_you_are` (for naming inspiration)
    - `who_you_want_to_be` (for naming inspiration)
  - Allowed actions:
    - `create_identity` (with category: "passions_and_talents" as default)
    - `update_identity_name` (for refining/updating the name if needed)
    - `add_identity_note` (for capturing notes about why this identity matters)
    - `accept_identity_refinement` (to mark as refinement_complete - REQUIRED before transition)
    - `transition_phase` (to move to Identity Commitment phase)

- [ ] Prompt content should include:
  - Instructions to ask "Is anything missing?" - **NOTE**: If context explanation is in transition message, prompt may just ask the question directly (coordinate with step 6)
  - Process for creating new identity:
    1. Create identity with `create_identity` (category: "passions_and_talents" as default)
    2. Help user name it (may need `update_identity_name` if they want to refine)
    3. Add notes with `add_identity_note` about why this identity matters
    4. Mark as `refinement_complete` with `accept_identity_refinement` (REQUIRED - identity must be at same state as others before transition)
    5. Transition to Identity Commitment phase
  - **CRITICAL**: New identity MUST be marked as `refinement_complete` before transitioning - this ensures it's ready for commitment phase along with all other identities
  - Default to "passions_and_talents" category unless it's clearly obvious which category it belongs to
  - Transition logic:
    - If user says "no" to missing anything: transition immediately to Identity Commitment
    - If user creates new identity: complete the process above, then transition to Identity Commitment
  - **Consideration**: If transition message includes full context explanation, the prompt's first message may be simpler since context was already provided

---

## 4. Context Keys

- [x] Required context keys for Anything Missing phase:
  - `user_name` - user's name for personalization
  - `identities` - shows all existing identities (so user can see what they already have)
  - `who_you_are` - for naming inspiration when creating new identity
  - `who_you_want_to_be` - for naming inspiration when creating new identity
  - No new context keys needed (existing ones are sufficient)
  - **Note**: All required context keys are included in the prompt

---

## 5. Actions

- [x] Required actions for Anything Missing phase:
  - `create_identity` - to create the new identity (with category: "passions_and_talents" as default)
  - `update_identity_name` - to refine/update the name if needed (similar to refinement phase)
  - `add_identity_note` - to capture notes about why this identity matters and what it represents
  - `accept_identity_refinement` - to mark the identity as `refinement_complete` (required before transitioning to commitment)
  - `transition_phase` - to move to Identity Commitment phase when done
  - **Note**: All required actions are included in the prompt

- [x] Process flow for new identity:
  1. User says something is missing
  2. Use `create_identity` with category: "passions_and_talents" (unless clearly obvious it belongs elsewhere)
  3. Help user name it (may need `update_identity_name` if they want to refine the name)
  4. Use `add_identity_note` to capture why this identity matters
  5. Use `accept_identity_refinement` to mark as `refinement_complete` (critical - must be done before transition)
  6. Use `transition_phase` to move to Identity Commitment phase
  - **Note**: Process flow is documented in the prompt

- [x] All required actions exist - no new actions needed

---

## 6. Phase Transition Messages

- [x] Get latest Identity Commitment prompt to review context explanation
  - Use Dev Coach MCP server `get_latest_prompt` with `coaching_phase: "identity_commitment"`
  - Review the explanation that provides context about what "Is anything missing?" means
  - The explanation includes: "Sometimes, as we go through this process, we might realize there's an important aspect of our lives that hasn't been captured in the identities we've created. This could be a role or a part of yourself that you feel is significant but hasn't been named yet."

- [ ] Update transition message FROM Identity Refinement
  - Current message transitions directly to Identity Commitment
  - New message should transition to Anything Missing phase
  - **IMPORTANT**: Incorporate the context explanation into the transition message itself
  - The transition message should explain what we mean by "anything missing" before asking the question
  - Example structure: Explain the concept, then ask if they're ready to check if anything is missing
  - This ensures smooth experience - user understands the question before the phase begins
  - **Note**: Transition message documented in `notes/Phase_Transition_Messages.md`, but Identity Refinement prompt not yet updated

- [x] Create transition message FROM Anything Missing TO Identity Commitment
  - If user said "no" to missing anything: brief transition acknowledging they're complete
  - If user created new identity: acknowledge the new identity and transition to commitment
  - Message should prepare them for the commitment evaluation process
  - **Completed**: Transition messages documented in `notes/Phase_Transition_Messages.md`

- [x] Update `notes/Phase_Transition_Messages.md`
  - Add new section for Anything Missing phase
  - Document both transition messages (from and to)
  - Include the context explanation in the transition FROM Identity Refinement

---

## 7. Update Identity Refinement Prompt

- [ ] Get latest Identity Refinement prompt using Dev Coach MCP server
  - Use `get_latest_prompt` MCP tool with `coaching_phase: "identity_refinement"`

- [ ] Create new version of Identity Refinement prompt in database using Dev Coach MCP server
  - Use `create_new_coach_prompt` MCP tool to create a new version
  - Update transition target from `identity_commitment` to `anything_missing`
  - Update transition message to match what's documented in `notes/Phase_Transition_Messages.md`
  - Keep all existing context keys and allowed actions the same

---

## 8. Update Identity Commitment Prompt

- [ ] Get latest Identity Commitment prompt using Dev Coach MCP server
  - Use `get_latest_prompt` MCP tool with `coaching_phase: "identity_commitment"`

- [ ] Create new version of Identity Commitment prompt in database using Dev Coach MCP server
  - Use `create_new_coach_prompt` MCP tool to create a new version
  - Remove "Is anything missing?" section from the prompt
    - Remove the "MANDATORY: Missing Identity Check (AT THE BEGINNING)" section
    - Remove related instructions about asking at the beginning
    - Update transition message handling to remove references to asking "Is anything missing?" first
  - Update prompt to assume identities are already complete
    - Prompt should start directly with evaluating identities for commitment
    - Remove all logic about handling missing identities
  - Keep all existing context keys and allowed actions the same

---

## 9. Documentation Updates

- [x] Update `.cursor/rules/coach-phases.mdc`
  - Add summary section for Anything Missing phase
  - Describe its purpose: catch any missing identities before commitment phase

- [ ] Update `docs/docs/coach/phases.md`
  - Add Anything Missing to the phases table
  - Document the phase's purpose and process

- [ ] Update `docs/sidebars.ts` (if phase-specific docs are created)
  - Add any new phase documentation files to sidebar structure

- [ ] Create phase documentation file (optional)
  - `docs/docs/coach/phases/anything-missing.md` (if following pattern of other phases)

---

## 10. Testing Considerations

- [ ] Test flow when user says "no" to missing anything
  - Should transition quickly to Identity Commitment
  - New identity should not appear in commitment list

- [ ] Test flow when user says "yes" and creates new identity
  - New identity should be created with category: "passions_and_talents" (default)
  - New identity should be named (may be refined with `update_identity_name` if needed)
  - Notes should be added with `add_identity_note` about why it matters
  - New identity MUST be marked as `refinement_complete` with `accept_identity_refinement`
  - New identity should appear in Identity Commitment phase list (via `commitment_identities` context)
  - New identity should be evaluated like any other identity in commitment phase
  - New identity should flow through I Am Statements and Visualization phases normally

- [ ] Verify new identities created in this phase integrate properly
  - Should appear in commitment identities context
  - Should flow through I Am Statements and Visualization phases
  - Should be treated identically to identities created in brainstorming

---

## 11. Code Updates (Frontend)

- [ ] Update any frontend components that check for specific phases
  - Check `IdentitiesBulletin.tsx` and similar components
  - Ensure new phase is handled appropriately in UI

- [ ] Verify phase display in admin/test interfaces
  - Ensure new phase shows up correctly in any phase selectors
  - Verify phase colors and display names work

---

## 12. Migration Strategy

- [ ] Consider existing users in Brainstorming Review or Identity Commitment
  - Determine if any migration needed for users mid-flow
  - Decide if existing users should skip new phase or go through it

- [ ] Update any test scenarios that reference phase transitions
  - Update test data if needed
  - Verify test scenarios still work with new phase

---

## Key Implementation Notes

1. **New Identity State**: New identities created in this phase MUST be brought to `refinement_complete` state before transitioning to Identity Commitment. This is critical - use `accept_identity_refinement` action to mark the identity as complete so it's ready for commitment evaluation along with all other identities.

2. **Default Category**: New identities automatically default to "passions_and_talents" category. Only use a different category if it's clearly obvious which category the identity belongs to.

3. **No Nesting or Combining**: This phase does NOT support nesting or combining operations. All new identities created here are standalone identities. Do not offer `show_nest_identities` or `show_combine_identities` actions.

4. **Simplified Process**: This phase is a streamlined combination of brainstorming, naming, and refinement:
   - Create identity (with default category)
   - Name it (may refine name if needed)
   - Add notes about why it matters
   - Mark as `refinement_complete`
   - Transition to commitment

5. **Quick Path**: Most users will say "no" - the phase should handle this efficiently and transition immediately to Identity Commitment.

6. **Integration**: New identities created here must integrate seamlessly with the rest of the coaching flow - they should appear in commitment phase and flow through all subsequent phases (I Am Statements, Visualization) normally, just like identities created in brainstorming.

