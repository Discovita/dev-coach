# How to add a new Context Key

1. **Add the name of the new Context Key to the list of ContextKey in `server/enums/context_keys.py` .**
2. **Add a corresponding entry to the PromptContext model in `server/services/prompt_manager/models/prompt_context.py`.**
3. **Add the code needed to retrieve your new context key to `get_context_value` in `server/services/prompt_manager/utils/context_gathering.py`.**
   - You may need to update `gather_prompt_context` as well.
4. **Update the `log_context_stats` function in `server/services/prompt_manager/utils/context_logging.py` so that your new key's debug logging is set up.**
5. **Make sure that one of the prompts in the Coach uses this ContextKey to see it in action.**
