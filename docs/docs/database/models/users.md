---
sidebar_position: 1
---

# User

The User model is the core authentication and user management model in the Dev Coach system. It extends Django's AbstractUser with custom fields for coaching functionality and test scenario isolation.

## Overview

The User model uses email-based authentication (no username field) and includes fields for email verification, test scenario isolation, and standard Django user functionality.

## Fields

- `id` (UUIDField): Primary key, auto-generated UUID
- `email` (EmailField): Unique email address used as username
- `password` (CharField): Hashed password, max 128 characters
- `first_name` (CharField): User's first name, max 150 characters, optional
- `last_name` (CharField): User's last name, max 150 characters, optional
- `is_staff` (BooleanField): Whether user can access admin site, defaults to False
- `is_active` (BooleanField): Whether user account is active, defaults to True
- `is_superuser` (BooleanField): Whether user has all permissions, defaults to False
- `groups` (ManyToManyField): Django groups the user belongs to
- `user_permissions` (ManyToManyField): Specific permissions for this user
- `verification_token` (CharField): Token for email verification, max 100 characters, optional
- `email_verification_sent_at` (DateTimeField): When last verification email was sent, optional
- `last_login` (DateTimeField): When user last logged in, optional
- `created_at` (DateTimeField): When user account was created, auto-set
- `updated_at` (DateTimeField): When user account was last updated, auto-updated
- `test_scenario` (ForeignKey): Link to [TestScenario](./test-scenario.md) for test data isolation, optional

## Configuration

- **Username Field**: `email`
- **Required Fields**: None (email-based auth)
- **Custom Manager**: `UserManager` with email-based user creation

## Methods

- `get_full_name()`: Returns first_name + last_name
- `get_short_name()`: Returns first_name
- `email_user(subject, message, from_email=None, **kwargs)`: Sends email to user

## Relationships

- One-to-One with [CoachState](./coach-state.md) (via `coach_state`)
- One-to-Many with [Identity](./identity.md) (via `identities`)
- One-to-Many with [ChatMessage](./chat-message.md) (via `chat_messages`)
- One-to-Many with [Action](./action.md) (via `actions`)
- One-to-Many with [UserNote](./user-note.md) (via `user_notes`)
- Many-to-One with [TestScenario](./test-scenario.md) (via `test_scenario`)

## Usage Context

- Primary authentication model for the application
- Used throughout the coaching system as the main user reference
- Supports test scenario isolation for development and testing
- Email-based authentication (no username field)
