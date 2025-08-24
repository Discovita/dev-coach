# How to Add a New Coach Action

1. **Add the action name to the `ActionType` enum in `server/enums/action_type.py`.**

2. **Create a Pydantic model for the actions parameters in `server/services/action_handler/models/params.py`.**

   - The model should inherit from `BaseModel`.
   - Should consist of key/value pairs
   - Cannot use `List` or `Dict` as a type. OpenAI will throw an error if you do.
   - You can limit string choices to a set of values using Django TextChoices (see `server/enums/` for an example).
   - Ensure you update the `__init__.py` file in the `server/services/action_handler/models/params.py` directory to export your new model.

3. **Create the Pydantic model for the action in `server/services/action_handler/models/actions.py`.**

   - The model should inherit from `BaseModel`.
   - The model should only have `params` for the only parameter which should be of the type of the model created in step 2.
   - Ensure you add the same class config as the other models in this file. OpenAI will throw an error if you do not.
   - Ensure you update the `__init__.py` file in the `server/services/action_handler/models/actions.py` directory to export your new model.

4. **Update the `server/services/action_handler/models/__init__.py` file to export your new parameter and action models.**

   - Add your new parameter model to the imports from `.params`
   - Add your new action model to the imports from `.actions`
   - Add both to the `__all__` list

5. **Add your new action to the list of `ACTION_PARAMS` in `server/services/action_handler/utils/action_instructions.py`.**

   - Make sure you import your new action model at the top of the file.

6. **Add your new ActionType and associated Action Pydantic model to the `ACTION_TYPE_TO_MODEL` dictionary in `server/services/action_handler/utils/dynamic_schema.py`.**

   - Make sure you import your new action model at the top of the file.

7. **Create the actual function that will get run when the action is called.**

   - Add your action in a new file titled `<your_function_name>.py`
   - Write your function in the file manipulating the database or whatever else you need to do.
   - **IMPORTANT**: Your action function must log the action to the Action table. Follow this pattern:
     ```python
     from apps.actions.models import Action
     from enums.action_type import ActionType
     
     # After performing your action, log it:
     Action.objects.create(
         user=coach_state.user,
         action_type=ActionType.YOUR_ACTION_TYPE.value,
         parameters=params.model_dump(),
         result_summary="Description of what was accomplished",
         coach_message=coach_message,
         test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
     )
     ```
   - Make sure to make the result_summary a natural language description of what was done. Use f strings if need be to ensure the most accurate description possible.

8. **Update the `server/services/action_handler/actions/__init__.py` file to export your new action function from the directory.**

9. **Add your new action function to the Action Handler in `server/services/action_handler/handler.py`.**

   - Import it at the top
   - Add an entry to the `ACTION_HANDLERS` map for your new action
   - Add a case in the `apply_actions` function to handle your new action.

10. **Update the CoachChatResponse model to contain your new action.**

11. **Update the `client/src/enums/actionType.ts` file on the front end to reflect this addition.**

12. **Finally, ensure that one of the Coaching State prompts actually calls this action.**

13. **Create documentation for your new action following the existing pattern:**

    - Create a new file: `docs/docs/core-systems/action-handler/actions/your-action-name.md`
    - Use the same structure as existing action docs
    - Update `docs/sidebars.ts` to include your new action in the "Action Handler" -> "Actions" section
    - Update `docs/docs/core-systems/action-handler/overview.md` to include your new action in the actions table
