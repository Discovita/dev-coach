---
sidebar_position: 8
---

# UserNote

The UserNote model stores notes about users extracted by the Sentinel agent. Each note is associated with a user and may reference the chat message that prompted its creation, providing long-term memory for the coach.

## Overview

The UserNote model enables the coach to remember important information about users, extracts insights from chat conversations automatically, and provides context for future coaching sessions.

## Fields

- `id` (UUIDField): Primary key, auto-generated UUID
- `user` (ForeignKey): Link to [User](./users.md) model
- `note` (TextField): Note content about the user
- `source_message` (ForeignKey): Link to [ChatMessage](./chat-message.md) that prompted the note, optional
- `created_at` (DateTimeField): Creation timestamp, auto-set
- `test_scenario` (ForeignKey): Link to [TestScenario](./test-scenario.md) for test data isolation, optional

## Methods

- `__str__()`: Returns note preview with user email and truncated note content

## Relationships

- Many-to-One with [User](./users.md) (via `user_notes`)
- Many-to-One with [ChatMessage](./chat-message.md) (via `source_message`)
- Many-to-One with [TestScenario](./test-scenario.md) (via `test_scenario`)

## Usage Context

- Part of the Sentinel User Notes system for long-term memory
- Enables the coach to remember important information about users
- Extracts insights from chat conversations automatically
- Provides context for future coaching sessions
- Supports test scenario isolation for development
- Used by the Sentinel agent for note extraction and management
