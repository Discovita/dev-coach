# How to add a new Context Key

1. **Add the name of the new Context Key to the list of ContextKey in `server/enums/context_keys.py` .**

2. **Add a corresponding entry to the PromptContext model in `server/services/prompt_manager/models/prompt_context.py`.**

3. **Add the code needed to retrieve your new context key to `get_context_value` in `server/services/prompt_manager/utils/context/get_context_value.py`.**

   - Create any additional function you deem necessary here to assemble your context. If a new function is needed, add it to its own file in `server/services/prompt_manager/utils/context/func`
   - **If you created a new function file, update the `__init__.py` file in `server/services/prompt_manager/utils/context/func/__init__.py` to import your new function.**

4. **Update the `log_context_stats` function in `server/services/prompt_manager/utils/context_logging.py` so that your new key's debug logging is set up.**

5. **Create documentation for your new context key following the existing pattern:**

   - Create a new file: `docs/docs/core-systems/prompt-manager/context-keys/your-context-key-name.md`
   - Use the same structure as existing context key docs:
     ```markdown
     # Context Key Name
     
     Brief description of what this context key provides.
     
     ## What it gets
     
     Describe the specific data this context key retrieves.
     
     ## How it gets it
     
     Explain the database queries or logic used to gather this data.
     
     ## Example
     
     Show an example of what this context key returns:
     
     ```json
     {
       "your_context_key": "example value"
     }
     ```
     ```
   - Update `docs/sidebars.ts` to include your new context key in the "Context Keys" section:
     ```typescript
     "core-systems/prompt-manager/context-keys/your-context-key-name",
     ```
   - Update `docs/docs/core-systems/prompt-manager/context-keys/overview.md` to include your new context key in the appropriate category table.

6. **Make sure that one of the prompts in the Coach uses this ContextKey to see it in action.**
