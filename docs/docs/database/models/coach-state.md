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
- `proposed_identity` (ForeignKey): Currently proposed [Identity](./identity.md), optional. **Deprecated** (TODO: remove)
- `identity_focus` (CharField): Identity category focus, max 255 characters, defaults to PASSIONS (`passions_and_talents`)
- `skipped_identity_categories` (ArrayField): List of skipped identity categories
- `who_you_are` (ArrayField): List of "who you are" identities from user
- `who_you_want_to_be` (ArrayField): List of "who you want to be" identities from user
- `asked_questions` (ArrayField): List of questions asked during Get To Know You phase. Contains `GetToKnowYouQuestions` enum values: `background_upbringing`, `family_structure`, `work_living`, `hobbies_interests`, `why_here_hopes`
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

- `SYSTEM_CONTEXT` (stored: `system_context`): System context initialization
- `INTRODUCTION` (stored: `introduction`): Introduction to the coaching process
- `GET_TO_KNOW_YOU` (stored: `get_to_know_you`): Initial phase to understand the user
- `IDENTITY_WARM_UP` (stored: `identity_warm_up`): Warming up to identity concepts
- `IDENTITY_BRAINSTORMING` (stored: `identity_brainstorming`): Brainstorming identities
- `BRAINSTORMING_REVIEW` (stored: `brainstorming_review`): Reviewing brainstormed identities
- `IDENTITY_REFINEMENT` (stored: `identity_refinement`): Refining and improving identities
- `ANYTHING_MISSING` (stored: `anything_missing`): Check for missing identities
- `IDENTITY_COMMITMENT` (stored: `identity_commitment`): Committing to identities
- `I_AM_STATEMENT` (stored: `i_am_statement`): Creating "I Am" statements
- `IDENTITY_VISUALIZATION` (stored: `identity_visualization`): Visualizing identities

## Identity Category Choices

- `PASSIONS` (stored: `passions_and_talents`): "Passions and Talents"
- `MONEY_MAKER` (stored: `maker_of_money`): "Maker of Money"
- `MONEY_KEEPER` (stored: `keeper_of_money`): "Keeper of Money"
- `SPIRITUAL` (stored: `spiritual`): "Spiritual"
- `APPEARANCE` (stored: `personal_appearance`): "Personal Appearance"
- `HEALTH` (stored: `physical_expression`): "Physical Expression"
- `FAMILY` (stored: `familial_relations`): "Familial Relations"
- `ROMANTIC` (stored: `romantic_relation`): "Romantic Relation"
- `ACTION` (stored: `doer_of_things`): "Doer of Things"

## Usage Context

- Tracks user progress through coaching phases
- Manages identity creation and refinement process
- Stores user responses during Get To Know You phase
- Maintains session state for conversation continuity
- Supports test scenario isolation for development
