---
sidebar_position: 2
---

# CoachState

The CoachState model stores the current state of a coaching session for a user. It tracks the user's progress through different coaching phases, manages identity creation and refinement, and maintains session metadata.

## Overview

The CoachState model maintains a one-to-one relationship with users and tracks their progress through the coaching phases, including current and proposed identities, skipped categories, and session metadata.

## Fields

- `id` (UUIDField): Primary key, auto-generated UUID
- `user` (OneToOneField): Link to [User](./users.md) model, unique per user
- `current_phase` (CharField): Current coaching phase, max 32 characters
- `current_identity` (ForeignKey): [Identity](./identity.md) currently being refined, optional
- `proposed_identity` (ForeignKey): Currently proposed [Identity](./identity.md), optional
- `identity_focus` (CharField): Identity category focus, defaults to PASSIONS
- `skipped_identity_categories` (ArrayField): List of skipped identity categories
- `who_you_are` (ArrayField): List of "who you are" identities from user
- `who_you_want_to_be` (ArrayField): List of "who you want to be" identities from user
- `asked_questions` (ArrayField): List of questions asked during Get To Know You phase
- `metadata` (JSONField): Additional session metadata, optional
- `updated_at` (DateTimeField): Last update timestamp, auto-updated
- `test_scenario` (ForeignKey): Link to [TestScenario](./test-scenario.md) for test data isolation, optional

## Methods

- `__str__()`: Returns coach state description with user email and current phase

## Relationships

- One-to-One with [User](./users.md) (via `coach_state`)
- Many-to-One with [Identity](./identity.md) (via `current_identity` and `proposed_identity`)
- Many-to-One with [TestScenario](./test-scenario.md) (via `test_scenario`)

## Coaching Phase Choices

- `GET_TO_KNOW_YOU`: Initial phase to understand the user
- `IDENTITY_CREATION`: Creating user identities
- `IDENTITY_REFINEMENT`: Refining and improving identities
- `INTEGRATION`: Integrating identities into daily life
- `COMPLETED`: Coaching session completed

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

- Tracks user progress through coaching phases
- Manages identity creation and refinement process
- Stores user responses during Get To Know You phase
- Maintains session state for conversation continuity
- Supports test scenario isolation for development
