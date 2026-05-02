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
- `state` (CharField): Current identity state, max 32 characters, defaults to PROPOSED
- `notes` (ArrayField): List of notes about the identity
- `category` (CharField): Identity category, max 32 characters
- `created_at` (DateTimeField): Creation timestamp, auto-set
- `updated_at` (DateTimeField): Last update timestamp, auto-updated
- `image` (VersatileImageField): Identity image file, stored in S3 (inherited from ImageMixin), optional
- `image_ppoi` (PPOIField): Primary Point of Interest for smart cropping (inherited from ImageMixin)
- `test_scenario` (ForeignKey): Link to [TestScenario](./test-scenario.md) for test data isolation, optional

## Inheritance

Identity inherits from:
- `ImageMixin`: Provides VersatileImageField with automatic S3 storage and size variant generation

## Configuration

- `verbose_name`: "Identity"
- `verbose_name_plural`: "Identities"

## Methods

- `__str__()`: Returns name truncated to 30 characters, category, and state

## Relationships

- Many-to-One with [User](./users.md) (via `identities`)
- One-to-Many with [CoachState](./coach-state.md) (via `current_coach_states` and `proposed_coach_states`)
- One-to-Many with IdentityImageChat (via `image_chats`)
- Many-to-One with [TestScenario](./test-scenario.md) (via `test_scenario`)

## Identity State Choices

- `PROPOSED` (stored: `proposed`): Identity has been proposed but not yet accepted (default)
- `ACCEPTED` (stored: `accepted`): Identity has been accepted by the user
- `REFINEMENT_COMPLETE` (stored: `refinement_complete`): Identity refinement process is complete
- `COMMITMENT_COMPLETE` (stored: `commitment_complete`): Identity commitment process is complete
- `I_AM_COMPLETE` (stored: `i_am_complete`): "I Am" statement has been created
- `VISUALIZATION_COMPLETE` (stored: `visualization_complete`): Identity visualization is complete
- `ARCHIVED` (stored: `archived`): Identity has been archived

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

## Related Models

The IdentityImageChat model also exists in the same app, tracking image generation chat sessions for identities.

## Usage Context

- Core model for storing user identities in the coaching system
- Tracks identity progression through different states
- Stores identity components ("I Am" Statement, visualization, notes)
- Categorized by life areas for organized coaching approach
- Supports test scenario isolation for development
- Referenced by CoachState for current and proposed identities
