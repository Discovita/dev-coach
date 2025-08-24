---
sidebar_position: 4
---

# ChatMessage

The ChatMessage model stores individual messages in the conversation history for the coaching chatbot. It tracks both user and coach messages with timestamps and supports test scenario isolation.

## Overview

The ChatMessage model maintains conversation history with role-based message tracking, enabling conversation reconstruction, context building, and action tracking through triggered actions.

## Fields

- `id` (UUIDField): Primary key, auto-generated UUID
- `user` (ForeignKey): Link to [User](./users.md) model, indexed
- `role` (CharField): Message sender role, max 32 characters
- `content` (TextField): Message content
- `timestamp` (DateTimeField): Message timestamp, auto-set, indexed
- `test_scenario` (ForeignKey): Link to [TestScenario](./test-scenario.md) for test data isolation, optional

## Methods

- `__str__()`: Returns message format with role and content

## Relationships

- Many-to-One with [User](./users.md) (via `chat_messages`)
- One-to-Many with [Action](./action.md) (via `triggered_actions`)
- One-to-Many with [UserNote](./user-note.md) (via `source_message`)
- Many-to-One with [TestScenario](./test-scenario.md) (via `test_scenario`)

## Message Role Choices

- `USER`: Message sent by the user
- `COACH`: Message sent by the coach

## Database Indexes

- Primary key on `id`
- Index on `user` field
- Index on `timestamp` field

## Usage Context

- Stores complete conversation history for coaching sessions
- Used for conversation reconstruction and context building
- Supports prompt formatting for AI interactions
- Tracks message timing for session analysis
- Enables action tracking through triggered_actions relationship
- Supports test scenario isolation for development
- Used by UserNote system for extracting user insights
