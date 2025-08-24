---
sidebar_position: 6
---

# Action

The Action model tracks actions taken by the coach during conversations. Each action is linked to the specific coach message that triggered it, enabling conversation reconstruction, debugging, and action history tracking.

## Overview

The Action model provides an audit trail for coaching sessions, linking actions to specific coach messages for context and supporting the Action Handler System for processing coach responses.

## Fields

- `id` (UUIDField): Primary key, auto-generated UUID
- `user` (ForeignKey): Link to [User](./users.md) model, indexed
- `action_type` (CharField): Type of action performed, max 64 characters
- `parameters` (JSONField): Action parameters stored as JSON
- `result_summary` (TextField): Natural language description of action result, optional
- `timestamp` (DateTimeField): Action timestamp, auto-set, indexed
- `coach_message` (ForeignKey): Link to [ChatMessage](./chat-message.md) that triggered the action
- `test_scenario` (ForeignKey): Link to [TestScenario](./test-scenario.md) for test data isolation, optional

## Configuration

- `verbose_name`: "Action"
- `verbose_name_plural`: "Actions"
- `ordering`: ['timestamp'] - Ordered by timestamp
- Custom indexes for performance optimization

## Methods

- `__str__()`: Returns action description with action type, username, and timestamp

## Relationships

- Many-to-One with [User](./users.md) (via `actions`)
- Many-to-One with [ChatMessage](./chat-message.md) (via `triggered_actions`)
- Many-to-One with [TestScenario](./test-scenario.md) (via `test_scenario`)

## Action Type Choices

- Various action types that can be performed by the coach (specific values depend on enum definition)

## Database Indexes

- Primary key on `id`
- Index on `user` field
- Index on `timestamp` field
- Composite index on `user` and `timestamp`
- Index on `coach_message` field
- Index on `action_type` field

## Usage Context

- Tracks all actions performed by the coach during conversations
- Enables conversation reconstruction and debugging
- Provides audit trail for coaching sessions
- Supports action history analysis
- Links actions to specific coach messages for context
- Supports test scenario isolation for development
- Used by Action Handler System for processing coach responses
