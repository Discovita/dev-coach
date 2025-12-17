# Identity Progression System

This document explains how to keep the coach synchronized when working through multiple identities in a phase. This pattern is used in Identity Refinement, Identity Commitment, I Am Statements, and Identity Visualization phases.

## The Problem

When a phase needs to process each identity one-by-one, we need:
1. The coach to know which identity is **currently** being worked on
2. The coach to know which identities are **remaining** (in order)
3. The system to automatically advance to the next identity when one is completed
4. The coach's message to correctly name the next identity when transitioning

Without proper synchronization, the coach might say "Let's work on your Maker identity" while the system sets `current_identity` to a different identity.

## The Solution: Three Components

### 1. The `current_identity` Context Key

The `current_identity` field on `CoachState` tracks which specific identity is being worked on RIGHT NOW. This is:
- Set automatically when entering a phase (via `transition_phase` action)
- Updated automatically when completing an identity (via `accept_*` actions)
- Displayed to the user on the frontend
- Included in the prompt via the `current_identity` context key

### 2. The Phase-Specific Pending List Context Key

Each phase has a context key that returns an **ordered list** of identities that still need processing:

| Phase | Context Key | Function |
|-------|-------------|----------|
| Identity Refinement | `refinement_identities` | `get_refinement_identities_context()` |
| Identity Commitment | `commitment_identities` | `get_commitment_identities_context()` |
| I Am Statements | `i_am_identities` | `get_i_am_identities_context()` |
| Identity Visualization | `visualization_identities` | `get_visualization_identities_context()` |

**CRITICAL:** These functions MUST include `.order_by('created_at')` to ensure consistent ordering with the automatic advancement logic.

### 3. The Automatic Advancement Utility

The `set_current_identity_to_next_pending()` function automatically sets `current_identity` to the next identity that needs processing. It:
- Excludes identities that have reached the "complete" state for that phase
- Excludes archived identities
- Orders by `created_at` (oldest first)
- Sets `current_identity` to `None` when no identities remain

This function is called inside the `accept_*` action handlers:

```python
# In accept_i_am_statement.py
def accept_i_am_statement(coach_state, params, coach_message):
    # Mark identity as complete
    Identity.objects.filter(id=params.id).update(state=IdentityState.I_AM_COMPLETE)
    
    # Automatically advance to next pending identity
    set_current_identity_to_next_pending(coach_state, IdentityState.I_AM_COMPLETE)
```

## How It Works Together

### Prompt Structure

The prompt includes both context keys:

```markdown
## Identities Needing [Phase Name]
{phase_specific_identities}

## Current Identity
{current_identity}
```

This gives the LLM:
1. The ordered list of remaining identities (so it knows what's next)
2. The current identity to work on (so it stays focused)

### Transition Flow

When the user completes an identity:

1. **Prompt is built** with `current_identity = A` and pending list `[A, B, C]`
2. **LLM generates response** - it can see B is next in the list
3. **LLM includes action** (e.g., `accept_i_am_statement`) for identity A
4. **Action handler runs**, which:
   - Marks A as complete
   - Calls `set_current_identity_to_next_pending()` → sets `current_identity = B`
5. **LLM's message** should say "Perfect! What does being a **B** mean to you?"

### The Critical Prompt Instruction

The prompt MUST explicitly instruct the LLM to look at the pending list for the next identity:

```markdown
## 🚨 CRITICAL TRANSITION RULE 🚨

**When the user accepts/completes an identity:**

1. Brief celebration: "Perfect!" / "Fantastic!"
2. Execute the accept action
3. **IMMEDIATELY ask about the NEXT identity from the pending list BY NAME**

**Example (CORRECT):**
"Perfect! What does being a **Philosopher** mean to you?"

**Example (WRONG):**
❌ "Fantastic! Let's move on to the next identity."
❌ Any generic statement that doesn't name the next identity
```

## Implementation Checklist

When adding a new phase that processes identities one-by-one:

### 1. Create the Context Function

```python
# get_[phase]_identities_context.py
def get_[phase]_identities_context(coach_state: CoachState) -> str:
    user = coach_state.user
    identities = user.identities.exclude(
        state=IdentityState.[PHASE]_COMPLETE
    ).exclude(
        state=IdentityState.ARCHIVED
    ).order_by('created_at')  # <-- CRITICAL: Must include ordering!
    
    if identities.count() == 0:
        return "No more identities left - time to move to the next phase!"
    
    return format_identities(identities)
```

### 2. Register the Context Key

Add to `enums/context_keys.py`:
```python
[PHASE]_IDENTITIES = "[phase]_identities", "[Phase] Identities"
```

Add to `get_context_value.py`:
```python
elif key == ContextKey.[PHASE]_IDENTITIES:
    return get_[phase]_identities_context(coach_state)
```

### 3. Create the Accept Action

```python
# accept_[phase].py
def accept_[phase](coach_state, params, coach_message):
    Identity.objects.filter(id=params.id).update(state=IdentityState.[PHASE]_COMPLETE)
    
    # Automatically advance to next pending identity
    set_current_identity_to_next_pending(coach_state, IdentityState.[PHASE]_COMPLETE)
```

### 4. Update the Prompt

Add both context keys to `required_context_keys`:
```
["user_name", "current_identity", "[phase]_identities", "identity_ids"]
```

Include both in the prompt body:
```markdown
## Identities Needing [Phase]
{[phase]_identities}

## Current Identity
{current_identity}
```

Add the critical transition rule to the prompt.

### 5. Update transition_phase Action

In `transition_phase.py`, add logic to set the initial `current_identity` when entering the phase:

```python
if CoachingPhase.[PHASE].value == params.to_phase:
    set_current_identity_to_next_pending(coach_state, IdentityState.[PHASE]_COMPLETE)
```

## Common Pitfalls

1. **Missing `.order_by('created_at')`** - The pending list and `set_current_identity_to_next_pending()` must use the same ordering, or the coach will mention one identity while the system sets a different one.

2. **Generic transition messages** - The prompt must explicitly forbid generic messages like "let's move on" and require naming the next identity.

3. **Forgetting to call `set_current_identity_to_next_pending()`** - The accept action must call this to advance automatically.

4. **Not including the pending list in the prompt** - Without seeing the list, the LLM can't know which identity comes next.

## Related Files

- `server/services/action_handler/utils/set_current_identity_to_next_pending.py`
- `server/services/prompt_manager/utils/context/func/get_*_identities_context.py`
- `server/services/action_handler/actions/accept_*.py`
- `server/services/action_handler/actions/transition_phase.py`
