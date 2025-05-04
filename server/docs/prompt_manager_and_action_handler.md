# How the Prompt Manager and Action Handler Work Together

This document explains the workflow and integration between the **Prompt Manager** and **Action Handler** in the question generation pipeline, specifically how they interact to process and update questions based on LLM (Large Language Model) responses.

---

## Overview

The question generation process is orchestrated by the `QuestionGenerator` class (`generation/question_generators/base.py`). For each step in the generation workflow, the following sequence occurs:

1. **Prompt Creation:** The `PromptManager` constructs the prompt and system message for the current step.
2. **LLM Call:** The AI service generates a response using the constructed prompt.
3. **Action Application:** The `apply_actions` function (Action Handler) processes the LLM response and updates the question accordingly.

---

## Step-by-Step Workflow

### 1. Prompt Creation (`PromptManager`)

- **File:** `prompts/prompt_manager/manager.py`
- **Role:** Responsible for generating the system message, prompt, and expected response format for each generation step.
- **Usage:**  
  ```python
  prompt_manager = PromptManager(self.services)
  system_message, prompt, response_format = await prompt_manager.create_generation_prompt()
  ```
- **Details:**  
  - The `PromptManager` uses the current state of the `services` context (which includes the question and other metadata) to tailor the prompt for the LLM.
  - It ensures that the LLM receives all necessary context and instructions for the current step.

### 2. LLM Call (`ai_service.generate`)

- **File:** `services/ai/base.py` and implementations like `openai_service.py`, `anthropic_service.py`
- **Role:** Handles communication with the LLM, sending the prompt and receiving the response.
- **Usage:**  
  ```python
  response = await self.services.ai_service.generate(
      prompt=prompt,
      system_message=system_message,
      response_format=response_format,
  )
  ```
- **Details:**  
  - The AI service abstracts away the details of the LLM provider.
  - The response is expected to be in a format that the Action Handler can process.

### 3. Action Application (`apply_actions` - Action Handler)

- **File:** `services/actions/handler.py`
- **Role:** Applies the actions described in the LLM response to the current question object.
- **Usage:**  
  ```python
  updated_question = apply_actions(
      question=self.services.context.generated_question.question,
      response=response,
  )
  ```
- **Details:**  
  - The `apply_actions` function interprets the LLM's response, which may include instructions or modifications for the question.
  - It updates the question object accordingly (e.g., setting the correct answer, adding explanations, etc.).
  - The updated question is then saved back into the service context.

---

## Example: How They Work Together in `QuestionGenerator`

**File:** `generation/question_generators/base.py`

```python
for step in self.steps:
    # 1. Update the current step in the context
    self.services.update_generated_question(step=step)
    # 2. Create prompt and system message
    prompt_manager = PromptManager(self.services)
    system_message, prompt, response_format = await prompt_manager.create_generation_prompt()
    # 3. Call the LLM
    response = await self.services.ai_service.generate(
        prompt=prompt,
        system_message=system_message,
        response_format=response_format,
    )
    # 4. Apply actions from the LLM response to the question
    updated_question = apply_actions(
        question=self.services.context.generated_question.question,
        response=response,
    )
    # 5. Update the question in the context
    self.services.update_generated_question(question=updated_question)
```

---

## File References

- **Prompt Manager:**  
  - `prompts/prompt_manager/manager.py`  
    - Responsible for prompt and system message creation.
- **Action Handler:**  
  - `services/actions/handler.py`  
    - Contains `apply_actions`, which updates the question based on LLM output.
- **Question Generator:**  
  - `generation/question_generators/base.py`  
    - Orchestrates the workflow, calling both the Prompt Manager and Action Handler.

---

## Summary Table

| Step                | Responsible Component      | Key Function/Method                | File Location                              |
|---------------------|---------------------------|-------------------------------------|--------------------------------------------|
| Prompt Creation     | Prompt Manager            | `create_generation_prompt`          | `prompts/prompt_manager/manager.py`        |
| LLM Call            | AI Service                | `generate`                          | `services/ai/base.py` (and implementations)|
| Action Application  | Action Handler            | `apply_actions`                     | `services/actions/handler.py`              |

---

## Comments and Documentation

- All handlers and models should have step-by-step comments and docstrings.
- Types and interfaces should be documented with usage references.
- The workflow is designed for extensibility: new steps or actions can be added by updating the prompt manager and action handler logic.

---

## Conclusion

The **Prompt Manager** and **Action Handler** are tightly integrated in the question generation pipeline. The Prompt Manager ensures the LLM receives the right instructions, and the Action Handler ensures the LLM's output is correctly applied to the question object, enabling a flexible and robust question generation system.

---

**For further details, refer to the code and comments in the files listed above.** 