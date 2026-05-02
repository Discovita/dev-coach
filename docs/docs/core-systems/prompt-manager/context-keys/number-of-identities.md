---
sidebar_position: 5
---

# Number of Identities

The `number_of_identities` context key provides the total count of identities the user has created.

## Context Key Details

**Key Name**: `number_of_identities`  
**Enum Value**: `ContextKey.NUMBER_OF_IDENTITIES`  
**Data Source**: Identity model  
**Return Type**: `int`

## What Data It Provides

Returns the total number of non-archived identities the user has created across all categories.

## How It Gets the Data

The function excludes archived identities and uses Django's `count()` method on the filtered queryset.

## Example Data

```python
# Example return values
5  # User has 5 identities total
0  # User has no identities yet
12 # User has 12 identities across all categories
```

## Implementation

```python
def get_number_of_identites_context(coach_state: CoachState) -> int:
    """
    Get the number of identities that the User has created (excluding archived).
    """
    user = coach_state.user
    return user.identities.exclude(state=IdentityState.ARCHIVED).count()
```
