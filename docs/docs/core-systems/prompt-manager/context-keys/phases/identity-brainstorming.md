---
sidebar_position: 1
---

# Identity Brainstorming Context

The `brainstorming_category_context` context key provides phase-specific information during the Identity Brainstorming coaching phase. This context helps the AI understand what category of identities the user is currently working on and provides relevant guidance.

## Context Key Details

**Key Name**: `brainstorming_category_context`  
**Enum Value**: `ContextKey.BRAINSTORMING_CATEGORY_CONTEXT`  
**Data Source**: Markdown files on disk, keyed by `CoachState.identity_focus` (an `IdentityCategory` value)  
**Phase**: Identity Brainstorming (`IDENTITY_BRAINSTORMING`)

## What Data It Provides

The brainstorming category context provides the full markdown content for the currently focused identity category. Each category has a dedicated markdown file containing:

- Category type (single or multiple identity)
- Key distinctions for this category
- Category-specific coaching approach
- Key questions to explore
- Language elevation techniques
- Natural resistance responses and how to handle them
- Transition guidance to the next category
- Special considerations (e.g., skipping options)

## How It Works

The implementation reads the `identity_focus` value from the user's `CoachState` (which is an `IdentityCategory` enum value like `passions_and_talents`, `maker_of_money`, etc.) and loads the corresponding markdown file from disk. There is **no database field** for this context — it is loaded directly from the filesystem.

## Implementation

```python
CATEGORY_CONTEXT_FILES = {
    IdentityCategory.PASSIONS: "services/prompt_manager/utils/context/identity_category_context/passions_and_talents.md",
    IdentityCategory.MONEY_MAKER: "services/prompt_manager/utils/context/identity_category_context/maker_of_money.md",
    IdentityCategory.MONEY_KEEPER: "services/prompt_manager/utils/context/identity_category_context/keeper_of_money.md",
    IdentityCategory.SPIRITUAL: "services/prompt_manager/utils/context/identity_category_context/spiritual.md",
    IdentityCategory.APPEARANCE: "services/prompt_manager/utils/context/identity_category_context/personal_appearance.md",
    IdentityCategory.HEALTH: "services/prompt_manager/utils/context/identity_category_context/physical_expression.md",
    IdentityCategory.FAMILY: "services/prompt_manager/utils/context/identity_category_context/familial_relations.md",
    IdentityCategory.ROMANTIC: "services/prompt_manager/utils/context/identity_category_context/romantic_relation.md",
    IdentityCategory.ACTION: "services/prompt_manager/utils/context/identity_category_context/doer_of_things.md",
}


def get_brainstorming_category_context(coach_state: CoachState) -> str:
    """
    Returns the markdown content for the currently focused identity category
    for the brainstorming prompt.
    """
    category = coach_state.identity_focus
    file_path = CATEGORY_CONTEXT_FILES.get(category)
    if not file_path:
        return f"No context file mapped for category: {category}"
    abs_path = os.path.abspath(file_path)
    try:
        with open(abs_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Could not load context for {category}: {str(e)}"
```

## The 9 Identity Categories

Each `IdentityCategory` enum value maps to a markdown file:

| IdentityCategory Enum | Value | Markdown File |
| --- | --- | --- |
| `PASSIONS` | `passions_and_talents` | `passions_and_talents.md` |
| `MONEY_MAKER` | `maker_of_money` | `maker_of_money.md` |
| `MONEY_KEEPER` | `keeper_of_money` | `keeper_of_money.md` |
| `SPIRITUAL` | `spiritual` | `spiritual.md` |
| `APPEARANCE` | `personal_appearance` | `personal_appearance.md` |
| `HEALTH` | `physical_expression` | `physical_expression.md` |
| `FAMILY` | `familial_relations` | `familial_relations.md` |
| `ROMANTIC` | `romantic_relation` | `romantic_relation.md` |
| `ACTION` | `doer_of_things` | `doer_of_things.md` |

## Usage in Prompts

### Template Example

```markdown
You are helping {user_name} brainstorm identities in the {current_phase} phase.

{brainstorming_category_context}

Based on this context, help them explore potential identities that align with their values and goals.
```

### Prompt Integration

The context is automatically included when a prompt specifies the `brainstorming_category_context` key:

```python
prompt.required_context_keys = [
    ContextKey.USER_NAME,
    ContextKey.CURRENT_PHASE,
    ContextKey.BRAINSTORMING_CATEGORY_CONTEXT
]
```

## Error Handling

- **No file mapped**: Returns `"No context file mapped for category: {category}"`
- **File read failure**: Returns `"Could not load context for {category}: {error}"`

## Related Context Keys

- `identity_focus`: Determines which category file to load
- `current_phase`: Confirms the user is in the brainstorming phase
- `identities`: Shows existing identities for context
- `focused_identities`: Shows identities within the current focus category
