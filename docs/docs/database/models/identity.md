---
sidebar_position: 3
---

# Identity

The Identity model represents a single identity with its state for a user in the coaching system. It stores the core components of user identities including "I Am" Statements, visualizations, and progress tracking through different states.

## Overview

The Identity model stores user identities with their components (name, "I Am" Statement, visualization), tracks progression through different states, and categorizes identities by life areas for organized coaching.

## Fields

- `id` (UUIDField): Primary key, auto-generated UUID
- `user` (ForeignKey): Link to [User](./users.md) model
- `name` (CharField): Concise identity label, max 255 characters, optional
- `i_am_statement` (TextField): "I am" statement with description, optional
- `visualization` (TextField): Vivid mental image, optional
- `clothing` (TextField): What the person is wearing in this identity visualization, optional
- `mood` (TextField): Emotional state/feeling in this identity visualization, optional
- `setting` (TextField): Environment/location for this identity visualization, optional
- `state` (CharField): Current identity state, max 32 characters, defaults to ACCEPTED
- `notes` (ArrayField): List of notes about the identity
- `category` (CharField): Identity category, max 32 characters
- `created_at` (DateTimeField): Creation timestamp, auto-set
- `updated_at` (DateTimeField): Last update timestamp, auto-updated
- `test_scenario` (ForeignKey): Link to [TestScenario](./test-scenario.md) for test data isolation, optional

## Configuration

- `verbose_name`: "Identity"
- `verbose_name_plural`: "Identities"

## Methods

- `__str__()`: Returns name truncated to 30 characters, category, and state

## Relationships

- Many-to-One with [User](./users.md) (via `identities`)
- One-to-Many with [CoachState](./coach-state.md) (via `current_coach_states` and `proposed_coach_states`)
- Many-to-One with [TestScenario](./test-scenario.md) (via `test_scenario`)

## Identity State Choices

- `PROPOSED`: Identity has been proposed but not yet accepted
- `ACCEPTED`: Identity has been accepted by the user
- `REFINEMENT_COMPLETE`: Identity refinement process is complete

## Identity Category Choices

- `PASSIONS`: Passion-based identities
- `VALUES`: Value-based identities
- `STRENGTHS`: Strength-based identities
- `GOALS`: Goal-based identities
- `RELATIONSHIPS`: Relationship-based identities
- `CAREER`: Career-based identities
- `HEALTH`: Health-based identities
- `FINANCE`: Finance-based identities
- `SPIRITUALITY`: Spirituality-based identities
- `CREATIVITY`: Creativity-based identities

## Usage Context

- Core model for storing user identities in the coaching system
- Tracks identity progression through different states
- Stores identity components ("I Am" Statement, visualization, notes)
- Categorized by life areas for organized coaching approach
- Supports test scenario isolation for development
- Referenced by CoachState for current and proposed identities
