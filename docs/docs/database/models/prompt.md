---
sidebar_position: 5
---

# Prompt

The Prompt model stores prompts used by the coaching system, including their versions, associated coaching phases, required context keys, and allowed actions. It supports the Prompt Manager System for dynamic prompt selection and management.

## Overview

The Prompt model enables version control for prompts, supports dynamic prompt selection based on coaching phase, and controls which actions are allowed in each prompt context through the Prompt Manager System.

## Fields

- `id` (UUIDField): Primary key, auto-generated UUID
- `coaching_phase` (CharField): Associated coaching phase, max 32 characters, optional
- `version` (IntegerField): Version number, defaults to 1
- `name` (CharField): Prompt name, max 255 characters, optional
- `description` (TextField): Prompt description, optional
- `body` (TextField): Prompt body content
- `required_context_keys` (ArrayField): List of required context keys
- `allowed_actions` (ArrayField): List of allowed action types
- `prompt_type` (CharField): Type of prompt, max 32 characters, defaults to COACH
- `is_active` (BooleanField): Whether prompt is active, defaults to True
- `created_at` (DateTimeField): Creation timestamp, auto-set
- `updated_at` (DateTimeField): Last update timestamp, auto-updated

## Configuration

- `unique_together`: ("prompt_type", "coaching_phase", "version") - Ensures unique version per combination of prompt type, coaching phase, and version

## Relationships

- No direct foreign key relationships defined

## Coaching Phase Choices

- `GET_TO_KNOW_YOU`: Initial phase to understand the user
- `IDENTITY_CREATION`: Creating user identities
- `IDENTITY_REFINEMENT`: Refining and improving identities
- `INTEGRATION`: Integrating identities into daily life
- `COMPLETED`: Coaching session completed

## Prompt Type Choices

- `COACH`: Standard coaching prompts (have `coaching_phase`)
- `SENTINEL`: Sentinel agent prompts (no `coaching_phase`)
- `SYSTEM`: System-level prompts (no `coaching_phase`)
- `IMAGE_GENERATION`: Image generation prompts (no `coaching_phase`)

## Context Key Choices

- Various context keys for prompt customization (specific values depend on enum definition)

## Action Type Choices

- Various action types that can be performed (specific values depend on enum definition)

## Database Constraints

- Unique constraint on combination of `prompt_type`, `coaching_phase`, and `version`
  - For prompts with `coaching_phase`: versions are unique per (`prompt_type`, `coaching_phase`)
  - For prompts without `coaching_phase` (e.g., `image_generation`, `sentinel`): versions are unique per `prompt_type`
- Primary key on `id`

## Usage Context

- Core component of the Prompt Manager System
- Enables version control for prompts
- Supports dynamic prompt selection based on coaching phase
- Controls which actions are allowed in each prompt context
- Manages prompt lifecycle through active/inactive status
- Supports different prompt types for various system components
