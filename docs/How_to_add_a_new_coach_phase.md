# How to add a new Coach Phase

1. Add the new phase to the `server/enums/coaching_phase.py` file.

2. Add the new phase to the `CoachingPhase` enum in `server/enums/coaching_phase.py`.

3. Create the prompt that will be used for this phase and add it to the database.

4. If any new Actions are needed for this new Coach Phase, then add those Actions.

5. If any new Context Keys are needed for this new Coach Phase, then add those Context Keys.
