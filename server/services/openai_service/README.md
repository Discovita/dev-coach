# OpenAI Helper

A modular Python package for interacting with OpenAI's API, providing a simplified interface with support for:

- Text completions
- Image inputs (multimodal)
- JSON mode
- Structured outputs
- Streaming responses
- Automatic parsing of responses into Pydantic models

## Module Structure

The module is organized into the following directories:

```
openai_service/
├── __init__.py              # Main entry point
├── core/                    # Core functionality
│   ├── __init__.py          # Exports core components
│   ├── base.py              # Base OpenAIService class
│   ├── chat/                # Chat completion functionality
│   │   ├── generic/         # Generic chat completion handlers
│   │   └── structured/      # Structured output chat completion
│   │       ├── __init__.py
│   │       ├── mixin.py     # Structured completion functionality
│   │       ├── streaming.py # Backward compatibility for streaming
│   │       ├── stream_completion.py # Core streaming functionality
│   │       ├── stream_with_final.py # Stream with final result functionality
│   │       └── structured_completion.py # Core structured completion
│   ├── messages/            # Message handling
│   └── responses/           # Response processing
├── enums/                   # Enumerations
│   ├── __init__.py          # Exports all enums
│   ├── ai_models.py         # AIModel enum with model capabilities
│   ├── ai_providers.py      # AIProvider enum for provider identification
│   └── model_features.py    # Collections of model-specific features
├── types/                   # Type definitions
│   ├── __init__.py
│   └── response_types.py    # Response type definitions
└── utils/                   # Utility functions
    ├── __init__.py
    ├── image.py             # Image handling utilities
    └── model_utils.py       # Model-specific utilities
```

## Usage Examples

### Basic Usage

```python
from openai_service import OpenAIService

# Initialize the client
client = OpenAIService(
    api_key="YOUR_API_KEY",
    organization="YOUR_ORG_ID"
)

# Simple text completion
response = client.create_chat_completion(
    prompt="Tell me a joke about programming.",
    model="gpt-4o"
)

print(response)
```

### Working with Images (Multimodal)

```python
from openai_service import OpenAIService

client = OpenAIService(
    api_key="YOUR_API_KEY",
    organization="YOUR_ORG_ID"
)

# Multimodal input with image
response = client.create_chat_completion(
    prompt="What's in this image?",
    images=["path/to/your/image.jpg"],
    model="gpt-4o"
)

print(response)
```

### Using JSON Mode

```python
from openai_service import OpenAIService

client = OpenAIService(
    api_key="YOUR_API_KEY",
    organization="YOUR_ORG_ID"
)

# Get response in JSON format
response = client.create_chat_completion(
    prompt="Generate a list of 3 programming languages with their creator and year.",
    model="gpt-4o",
    json_mode=True
)

# response is a Python dictionary
for language in response["languages"]:
    print(f"{language['name']} - {language['creator']} ({language['year']})")
```

### Structured Outputs with Pydantic

```python
from pydantic import BaseModel
from typing import List
from openai_service import OpenAIService

# Define your response structure
class ProgrammingLanguage(BaseModel):
    name: str
    creator: str
    year: int

class LanguagesResponse(BaseModel):
    languages: List[ProgrammingLanguage]

# Initialize the client
client = OpenAIService(
    api_key="YOUR_API_KEY",
    organization="YOUR_ORG_ID"
)

# Create messages for the conversation
messages = [
    {"role": "system", "content": "You are a programming historian."},
    {"role": "user", "content": "List 3 programming languages with their creator and year."}
]

# Get a structured response
response = client.create_structured_chat_completion(
    messages=messages,
    model="gpt-4o",
    response_format=LanguagesResponse
)

# Work with the typed response
for language in response.parsed_model.languages:
    print(f"{language.name} - {language.creator} ({language.year})")
```

### Using Stream Mode

```python
from openai_service import OpenAIService

client = OpenAIService(
    api_key="YOUR_API_KEY",
    organization="YOUR_ORG_ID"
)

# Stream the response
stream = client.create_chat_completion(
    prompt="Write a short story about AI.",
    model="gpt-4o",
    stream=True
)

# Process the streaming response
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Streaming Structured Outputs

```python
from pydantic import BaseModel
from typing import List
from openai_service import OpenAIService

# Define the response format using Pydantic
class EntityExtraction(BaseModel):
    attributes: List[str]
    colors: List[str]
    animals: List[str]

# Initialize the client
client = OpenAIService(
    api_key="YOUR_API_KEY",
    organization="YOUR_ORG_ID"
)

# Create messages
system_message = "Extract entities from the input text"
prompt = "The quick brown fox jumps over the lazy dog with piercing blue eyes"
messages = client.create_messages(prompt=prompt, system_message=system_message)

# Stream the structured completion
for parsed_data, is_final in client.stream_structured_completion(
    messages=messages,
    model="gpt-4o-mini",
    response_format=EntityExtraction,
    temperature=0.7,
):
    if is_final:
        print("\nFinal completion:")
        print(parsed_data)
    else:
        # Incremental updates
        print(parsed_data)
```

## Using AIModel for Model-Specific Logic

```python
from openai_service import AIModel

# Check if a model supports structured outputs
supports_structured = AIModel.supports_structured_outputs("gpt-4o")
print(f"Does gpt-4o support structured outputs? {supports_structured}")

# Get the appropriate token parameter name for a model
token_param = AIModel.get_token_param_name("o3-mini")
print(f"Token parameter for o3-mini: {token_param}")  # Returns "max_completion_tokens"

# Get the provider for a model
provider = AIModel.get_provider("gpt-4")
print(f"Provider for gpt-4: {provider}")  # Returns AIProvider.OPENAI
```

## Compatibility

This module was developed and tested with OpenAI Python SDK version 1.68.2. If you encounter issues with other versions, you can silence the compatibility warning by setting the environment variable:

```
MUTE_OPENAI_HELPER_WARNING=True
```

## Development

To contribute to this module, please follow the modular structure. Each file should have:

1. Comprehensive docstrings
2. Type annotations
3. Proper error handling
4. Logging for important operations

When adding new functionality, consider which module it belongs in:
- `core`: For main functionality that users will interact with directly
- `utils`: For client functions and utilities
- `types`: For type definitions and parsing logic
- `enums`: For enumeration types and constants