# How to add a new Coach Action

1. **Add the action name to the `ActionType` enum in `server/enums/action_type.py`.**

2. **Create a Pydantic model for the actions parameters in `server/models/params.py`.**

   - The model should inherit from `BaseModel`.
   - Should consist of key/value pairs
   - Cannot use `List` or `Dict` as a type. OpenAI will throw an error if you do.
   - You can limit string choices to a set of values using Django TextChoices (see `server/enums/` for an example).

3. **Create the Pydantic model for the action in `server/models/actions.py`.**

   - The model should inherit from `BaseModel`.
   - The model should only have `params` for the only parameter which should be of the type of the model created in step 2.
   - Ensure you add the same class config as the other models in this file. OpenAI will throw an error if you do not.

4. **Add your new action to the list of `ACTION_PARAMS` in `server/services/action_handler/utils/action_instructions.py`.**

   - Make sure you import your new action model at the top of the file.

5. **Add your new ActionType and associated Action Pydantic model to the `ACTION_TYPE_TO_MODEL` dictionary in `server/services/action_handler/utils/dynamic_schema.py`.**

   - Make sure you import your new action model at the top of the file.

6. **Create the actual function that will get run when the action is called.**

   - Add your action in a new file titled `<your_function_name>.py`
   - Write your function in the file manipulating the database or whatever else you need to do.

7. **Update the `server/services/action_handler/actions/__init__.py` file to export your new action function from the directory.**

8. **Add your new action function to the Action Handler in `server/services/action_handler/handler.py`.**
   - Import it at the top
   - Add an entry to the `ACTION_HANDLERS` map for your new action
   - Add a case in the `apply_actions` function to handle your new action.
9. **Update the `client/src/enums/actionType.ts` file on the front end to reflect this addition.**
10. **Finally, ensure that one of the Coaching State prompts actually calls this action.**
