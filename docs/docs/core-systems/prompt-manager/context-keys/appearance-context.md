---
sidebar_position: 20
---

# Appearance Context

The `appearance_context` provides a natural language description of the user's appearance preferences for image generation prompts.

## Context Details

**Function Name**: `get_appearance_context`  
**Data Source**: User model appearance fields  
**Return Type**: `str`  
**Usage**: Image generation prompts only

## What Data It Provides

Returns a natural language description of the user's appearance preferences, formatted as a single descriptive phrase. The description includes height, build, skin tone, gender, age range, hair color, and eye color when available.

## How It Gets the Data

The function reads appearance preference fields from the User model:
- `height`: Height preference (short, below_average, average, above_average, tall)
- `build`: Body type (slim, athletic, average, stocky, large)
- `skin_tone`: Skin tone (light, medium_light, medium, medium_dark, dark)
- `gender`: Gender preference (man, woman, person)
- `age_range`: Age range (twenties, thirties, forties, fifties, sixty_plus)
- `hair_color`: Hair color (black, brown, blonde, red, auburn, gray, white, bald)
- `eye_color`: Eye color (brown, blue, green, hazel, gray, amber)

The function formats these values into a natural language description suitable for image generation prompts.

## Example Data

```python
# Example return values
"a tall athletic man with medium skin tone, brown hair, and blue eyes in their 30s"

"a slim woman with light skin tone, blonde hair, and green eyes in their 20s"

""  # Empty string if no appearance preferences are set
```

## Implementation

```python
def get_appearance_context(user: User) -> str:
    """
    Build a natural language body description from user appearance preferences.
    
    Takes appearance fields from the User model and formats them into a descriptive
    string suitable for image generation prompts.
    
    Args:
        user: The User model instance with appearance preferences
        
    Returns:
        String describing the appearance, e.g., 
        "a tall athletic man with medium skin tone, brown hair, and blue eyes in their 30s"
        Returns empty string if no appearance preferences are set.
    """
    # ... implementation details ...
```

## Usage in Image Generation

This context is used specifically for image generation prompts via `PromptManager.create_image_generation_prompt()`. It is injected into the prompt template using the `{appearance_context}` placeholder.

The appearance context allows the image generation system to create personalized identity images that match the user's preferred visualization of themselves, which may differ from their actual appearance.

## Related Context

- **Scene Context**: Provides identity-specific scene details (clothing, mood, setting)
- **Identity Context**: Provides identity details (name, category, I Am statement, visualization)
