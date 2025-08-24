# How to Add a New Coach Phase

1. **Add the new phase to the `server/enums/coaching_phase.py` file.**

2. **Add the new phase to the `CoachingPhase` enum in `server/enums/coaching_phase.py`.**

3. **Create the prompt that will be used for this phase and add it to the database.**

4. **If any new Actions are needed for this new Coach Phase, then add those Actions.**

5. **If any new Context Keys are needed for this new Coach Phase, then add those Context Keys.**

6. **Update the `.cursor/rules/coach-phases.mdc` document**

7. **Come up with a phase transition message and update the `docs/Phase_Transition_Messages.md` document with the new message**

8. **Create documentation for your new phase following the existing pattern:**

   - Create a new file: `docs/docs/coach/phases/your-new-phase.md`
   - Use the same structure as existing phase docs
   - Update `docs/sidebars.ts` to include your new phase in the "Coach" -> "Phases" section
   - Update `docs/docs/coach/phases.md` to include your new phase in the phases table
