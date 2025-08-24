---
sidebar_position: 1
---

# Overview

The Dev Coach system uses PostgreSQL as its primary database, with a well-structured schema designed to support the coaching workflow, user management, conversation tracking, and test scenario isolation.

## Database Technology

- **Database**: PostgreSQL 17.1
- **ORM**: Django ORM with custom managers
- **Migrations**: Django migrations for schema management
- **Extensions**: PostgreSQL ArrayField for list storage

## Database Architecture

The database is organized into logical modules that correspond to Django apps:

```
dev_coach_db/
├── users/                    # User management and authentication
├── coach_states/            # Coaching session state and progress
├── chat_messages/           # Conversation history and message tracking
├── identities/              # User identity creation and management
├── prompts/                 # AI prompt templates and versioning
├── actions/                 # System action tracking and audit trails
├── test_scenario/           # Test scenario isolation and management
└── user_notes/              # User notes extracted by Sentinel agent
```

## Core Models

### User Management

- **[User](./models/users.md)**: Core user accounts with email-based authentication
- **[CoachState](./models/coach-state.md)**: Current coaching session state and progress tracking

### Coaching System

- **[Identity](./models/identity.md)**: User-created identities with affirmations and visualizations
- **[ChatMessage](./models/chat-message.md)**: Complete conversation history with role tracking
- **[Action](./models/action.md)**: System actions with parameters and result tracking
- **[UserNote](./models/user-note.md)**: Long-term user memory extracted by Sentinel agent

### System Administration

- **[Prompt](./models/prompt.md)**: AI prompt templates with version control and action permissions
- **[TestScenario](./models/test-scenario.md)**: Test scenario templates for development and testing

## Key Relationships

### User-Centric Design

- **User → CoachState**: One-to-one relationship for session state
- **User → Identity**: One-to-many relationship for multiple life area identities
- **User → ChatMessage**: One-to-many relationship for conversation history
- **User → Action**: One-to-many relationship for action audit trails
- **User → UserNote**: One-to-many relationship for long-term memory

### Identity Management

- **Identity → CoachState**: Current and proposed identity tracking
- **Identity Categories**: 10 life areas (career, health, relationships, etc.)
- **Identity States**: Proposed, accepted, refinement complete

### Conversation Flow

- **ChatMessage → Action**: Messages trigger specific actions
- **ChatMessage → UserNote**: Messages generate user insights
- **Message Roles**: User and coach message differentiation

### Test Scenario Isolation

- **TestScenario → All Models**: Complete test data isolation
- **Optional Foreign Keys**: All models support test scenario linking

## Data Integrity

### Foreign Key Constraints

- All relationships are properly constrained with appropriate cascade rules
- Cascade deletes for dependent data (user deletion removes all related data)
- SET NULL for optional relationships (test scenario isolation)

### Unique Constraints

- Email addresses are unique across users
- One coach state per user
- Unique version per coaching phase for prompts
- Unique scenario names for test scenarios

### Business Logic Constraints

- Email format validation
- Phase transition validation (coaching phases)
- Role validation (user/coach messages)
- State validation (identity states)

## Performance Considerations

### Indexing Strategy

- **Primary Keys**: UUID primary keys with automatic indexing
- **Foreign Keys**: Indexed for join performance
- **Timestamp Indexes**: Time-based queries for all models
- **Composite Indexes**: User + timestamp, user + category, user + role
- **Search Indexes**: Full-text search on message content and user notes

### Query Optimization

- Select_related for foreign key joins
- Prefetch_related for reverse relationships
- Database-level constraints for data integrity
- Efficient array field operations for PostgreSQL

## Schema Design Principles

### 1. **User-Centric Design**

- All data is organized around the User model
- One-to-one relationships for user state management
- One-to-many relationships for user-generated content

### 2. **Coaching Workflow Support**

- Phase-based progression tracking
- Identity creation and refinement workflow
- Conversation history preservation
- Action tracking for audit trails

### 3. **Test Scenario Isolation**

- All models support test scenario isolation
- Optional foreign key to TestScenario model

### 4. **Extensibility**

- JSON fields for flexible metadata storage
- Array fields for list-based data
- Version control for prompts and configurations

---

Next, explore the [Database Models](./models/users.md) or dive into the [Schema Documentation](./schema/overview.md).
