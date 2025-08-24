---
sidebar_position: 7
---

# TestScenario

The TestScenario model represents a template-based test scenario for the Discovita Dev Coach. It stores declarative JSON templates describing initial states for all relevant models, enabling comprehensive chatbot testing and development.

## Overview

The TestScenario model enables creation of predefined user states for testing, supports scenario management through admin interface, and provides test data isolation for development and testing.

## Fields

- `id` (UUIDField): Primary key, auto-generated UUID
- `name` (CharField): Unique scenario name, max 255 characters
- `description` (TextField): Scenario description for UI display, optional
- `template` (JSONField): Declarative template for initial model states
- `created_at` (DateTimeField): Creation timestamp, auto-set
- `updated_at` (DateTimeField): Last update timestamp, auto-updated
- `created_by` (ForeignKey): [User](./users.md) who created the scenario, optional

## Configuration

- `verbose_name`: "Test Scenario"
- `verbose_name_plural`: "Test Scenarios"
- `ordering`: ["-created_at"] - Ordered by creation date (newest first)

## Methods

- `__str__()`: Returns the scenario name

## Relationships

- Many-to-One with [User](./users.md) (via `created_by`)
- One-to-Many with [User](./users.md) (via `test_scenario`)
- One-to-Many with [CoachState](./coach-state.md) (via `test_scenario`)
- One-to-Many with [Identity](./identity.md) (via `test_scenario`)
- One-to-Many with [ChatMessage](./chat-message.md) (via `test_scenario`)
- One-to-Many with [Action](./action.md) (via `test_scenario`)
- One-to-Many with [UserNote](./user-note.md) (via `test_scenario`)

## Database Constraints

- Primary key on `id`
- Unique constraint on `name` field

## Usage Context

- Core component of the test scenario system for comprehensive chatbot testing
- Enables creation of predefined user states for testing
- Supports scenario management through admin interface
- Provides test data isolation for development and testing
- Used for creating, editing, resetting, and managing test user states
- Referenced in Testing Implementation Plan documentation
- Enables reproducible testing scenarios across different environments
