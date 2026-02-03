---
sidebar_position: 21
---

# Scene Context

The `scene_context` provides structured scene details from identity fields for image generation prompts.

## Context Details

**Function Name**: `get_scene_context`  
**Data Source**: Identity model scene fields  
**Return Type**: `str`  
**Usage**: Image generation prompts only

## What Data It Provides

Returns a structured description of the scene for an identity visualization, including clothing, mood/feeling, and setting/environment. Each element is labeled and formatted for clarity in image generation prompts.

## How It Gets the Data

The function reads scene-specific fields from the Identity model:
- `clothing`: What the person is wearing (e.g., "linen button-down shirt")
- `mood`: Emotional state/feeling (e.g., "proud and calm")
- `setting`: Environment/location (e.g., "on a hill overlooking Hawaiian agricultural land")

The function formats these fields into a structured string with labels for each element.

## Example Data

```python
# Example return values
"CLOTHING: linen button-down shirt
MOOD/FEELING: proud and calm
SETTING: on a hill overlooking Hawaiian agricultural land"

"CLOTHING: formal conductor's attire
MOOD/FEELING: passionate and focused
SETTING: grand concert hall"

""  # Empty string if no scene fields are set
```

## Implementation

```python
def get_scene_context(identity: Identity) -> str:
    """
    Build scene description from identity's clothing, mood, and setting fields.
    
    Takes the scene-specific fields from the Identity model and formats them into
    a structured string suitable for image generation prompts.
    
    Args:
        identity: The Identity model instance with scene fields
        
    Returns:
        String describing the scene elements in format:
        "CLOTHING: <clothing>
        MOOD/FEELING: <mood>
        SETTING: <setting>"
        Returns empty string if no scene fields are set.
    """
    # ... implementation details ...
```

## Usage in Image Generation

This context is used specifically for image generation prompts via `PromptManager.create_image_generation_prompt()`. It is injected into the prompt template using the `{scene_context}` placeholder.

The scene context allows the image generation system to create identity-specific visualizations that include the appropriate clothing, emotional state, and environment for each identity.

## Related Context

- **Appearance Context**: Provides user appearance preferences (height, build, skin tone, etc.)
- **Identity Context**: Provides identity details (name, category, I Am statement, visualization)
