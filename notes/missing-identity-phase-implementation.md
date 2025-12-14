# Anything Missing Phase Implementation To-Do List

## Overview
Extract the "Is there anything missing?" functionality from the Identity Commitment phase into its own dedicated phase. This phase will be inserted between Brainstorming Review and Identity Commitment.

## Phase Flow
**Current:** Brainstorming Review → Identity Commitment  
**New:** Brainstorming Review → Anything Missing → Identity Commitment

---

## 1. Backend Enum Updates

- [ ] Add new phase to `server/enums/coaching_phase.py`
  - Add `ANYTHING_MISSING = "anything_missing", "Anything Missing"` to `CoachingPhase` enum
  - Place it between `BRAINSTORMING_REVIEW` and `IDENTITY_COMMITMENT`

- [ ] Create and run Django migration for the new phase
  - Migration will update `CoachState.current_phase` choices
  - Migration will update `Prompt.coaching_phase` choices

---

## 2. Frontend Enum Updates

- [ ] Add new phase to `client/src/enums/coachingPhase.ts`
  - Add `ANYTHING_MISSING = "anything_missing"` to `CoachingPhase` enum

- [ ] Add display name to `COACHING_PHASE_DISPLAY_NAMES`
  - Add `[CoachingPhase.ANYTHING_MISSING]: "Anything Missing"`

- [ ] Add color to `COACHING_PHASE_COLORS`
  - Choose appropriate color scheme (suggest: similar to brainstorming review or commitment phase)

---

## 3. Prompt Creation

- [ ] Create initial prompt for the new phase in the database
  - Phase name: "Anything Missing"
  - Required context keys:
    - `user_name`
    - `identities` (to show what they already have)
    - `who_you_are` (for naming inspiration)
    - `who_you_want_to_be` (for naming inspiration)
    - `identity_ids` (for nesting operations)
  - Allowed actions:
    - `create_identity`
    - `update_identity_name` (for refining the name)
    - `add_identity_note` (for capturing notes about the identity)
    - `accept_identity_refinement` (to mark as refinement_complete after naming/refining)
    - `show_nest_identities` (if they want to nest under existing)
    - `transition_phase` (to move to Identity Commitment)

- [ ] Prompt content should include:
  - Instructions to ask "Is anything missing?" with full context upfront
  - Process for creating new identity (name it, refine it, add notes)
  - Default to "passions_and_talents" category unless obvious
  - Instructions to get the new identity to `refinement_complete` state
  - Transition logic (if no, move to commitment; if yes, handle creation then move to commitment)

---

## 4. Context Keys

- [ ] Verify existing context keys are sufficient
  - `identities` - shows all existing identities
  - `who_you_are` - for naming inspiration
  - `who_you_want_to_be` - for naming inspiration
  - `identity_ids` - for nesting operations
  - No new context keys needed (existing ones should cover it)

---

## 5. Actions

- [ ] Verify all needed actions exist
  - `create_identity` - exists
  - `update_identity_name` - exists
  - `add_identity_note` - exists
  - `accept_identity_refinement` - exists
  - `show_nest_identities` - exists
  - `transition_phase` - exists
  - No new actions needed

---

## 6. Phase Transition Messages

- [ ] Update transition message FROM Brainstorming Review
  - Current message transitions directly to Identity Commitment
  - New message should transition to Anything Missing phase
  - Message should ask if they're ready to check if anything is missing

- [ ] Create transition message FROM Anything Missing TO Identity Commitment
  - If user said "no" to missing anything: brief transition acknowledging they're complete
  - If user created new identity: acknowledge the new identity and transition to commitment
  - Message should prepare them for the commitment evaluation process

- [ ] Update `notes/Phase_Transition_Messages.md`
  - Add new section for Anything Missing phase
  - Document both transition messages (from and to)

---

## 7. Update Identity Commitment Prompt

- [ ] Remove "Is anything missing?" section from Identity Commitment prompt
  - Remove the "MANDATORY: Missing Identity Check (AT THE BEGINNING)" section
  - Remove related instructions about asking at the beginning
  - Update transition message handling to remove references to asking "Is anything missing?" first

- [ ] Update Identity Commitment prompt to assume identities are already complete
  - Prompt should start directly with evaluating identities for commitment
  - Remove all logic about handling missing identities

- [ ] Create new version of Identity Commitment prompt in database

---

## 8. Update Brainstorming Review Prompt

- [ ] Update transition message in Brainstorming Review prompt
  - Change transition target from `identity_commitment` to `anything_missing`
  - Update transition message text to reflect new phase

---

## 9. Documentation Updates

- [ ] Update `.cursor/rules/coach-phases.mdc`
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
  - New identity should be created with default category
  - New identity should be named and refined
  - New identity should be marked as `refinement_complete`
  - New identity should appear in Identity Commitment phase list
  - New identity should be evaluated like any other identity

- [ ] Test flow when user wants to nest new identity
  - Should use `show_nest_identities` action
  - Should not create standalone identity
  - Should transition to commitment after nesting

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

1. **New Identity State**: New identities created in this phase must be brought to `refinement_complete` state before transitioning to Identity Commitment, so they're ready for commitment evaluation.

2. **Default Category**: New identities default to "passions_and_talents" unless it's clearly obvious which category they belong to.

3. **Naming Process**: The phase needs clear instructions on how to help users name and refine new identities (similar to Identity Refinement phase process).

4. **Quick Path**: Most users will say "no" - the phase should handle this efficiently and transition quickly.

5. **Integration**: New identities created here must integrate seamlessly with the rest of the coaching flow - they should appear in commitment phase and flow through all subsequent phases normally.
