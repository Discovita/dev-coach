---
sidebar_position: 1
---

# Database Overview

The Dev Coach system uses PostgreSQL as its primary database, with a well-structured schema designed to support the coaching workflow, user management, and system administration.

## Database Technology

- **Database**: PostgreSQL 17.1
- **ORM**: Django ORM
- **Migrations**: Django migrations for schema management
- **Backup Strategy**: Automated daily backups with point-in-time recovery

## Database Architecture

The database is organized into logical modules that correspond to Django apps:

```
dev_coach_db/
├── users/                    # User management
├── coach_states/            # Coaching session state
├── chat_messages/           # Conversation history
├── identities/              # User identities
├── prompts/                 # AI prompt management
├── actions/                 # System actions
├── test_scenario/           # Testing utilities
└── user_notes/              # User notes and annotations
```

## Core Tables

### User Management
- **users_user**: Core user accounts and profiles
- **users_userprofile**: Extended user information
- **authentication_verification**: Email verification tokens

### Coaching System
- **coach_states_coachstate**: Current coaching state and progress
- **chat_messages_chatmessage**: All conversation messages
- **identities_identity**: User-created identities
- **user_notes_usernote**: User annotations and notes

### System Administration
- **prompts_prompt**: AI prompt templates and versions
- **actions_action**: System action definitions
- **actions_actionresult**: Action execution results

### Testing
- **test_scenario_testscenario**: Test scenario definitions
- **test_scenario_testscenariouser**: Test user data
- **test_scenario_testscenariochatmessage**: Test conversation data

## Key Relationships

### User → Coach State
- One-to-one relationship
- Each user has exactly one coach state
- Tracks current phase, progress, and session data

### User → Identities
- One-to-many relationship
- Users can have multiple identities
- Each identity represents a different life area

### User → Chat Messages
- One-to-many relationship
- All conversation history is preserved
- Messages include metadata for context

### Coach State → Chat Messages
- Many-to-many relationship through sessions
- Messages are grouped by coaching sessions
- Enables conversation threading and context

## Data Integrity

### Foreign Key Constraints
- All relationships are properly constrained
- Cascade deletes where appropriate
- Referential integrity maintained

### Unique Constraints
- Email addresses are unique across users
- Username uniqueness enforced
- Business logic constraints (e.g., one active coach state per user)

### Check Constraints
- Email format validation
- Phase transition validation
- Data range validation

## Performance Considerations

### Indexing Strategy
- **Primary Keys**: Auto-incrementing integers
- **Foreign Keys**: Indexed for join performance
- **Search Fields**: Full-text search on messages and notes
- **Time-based Queries**: Indexed on created_at/updated_at

### Query Optimization
- Select_related for foreign key joins
- Prefetch_related for reverse foreign keys
- Database-level query optimization
- Connection pooling for high concurrency

## Backup and Recovery

### Backup Strategy
- **Daily Full Backups**: Complete database snapshots
- **Hourly Incremental**: Transaction log backups
- **Point-in-Time Recovery**: 30-day retention
- **Cross-Region Replication**: Disaster recovery

### Recovery Procedures
- **Automated Recovery**: Self-healing for common issues
- **Manual Recovery**: Step-by-step procedures for complex scenarios
- **Data Validation**: Integrity checks after recovery

## Security

### Data Protection
- **Encryption at Rest**: AES-256 encryption
- **Encryption in Transit**: TLS 1.3 for all connections
- **Access Control**: Role-based permissions
- **Audit Logging**: All data access logged

### Privacy Compliance
- **GDPR Compliance**: Right to be forgotten
- **Data Retention**: Configurable retention policies
- **Anonymization**: PII removal capabilities
- **Consent Management**: User consent tracking

## Development Workflow

### Local Development
- **Docker PostgreSQL**: Containerized development database
- **Migration Management**: Django migrations for schema changes
- **Seed Data**: Fixtures for development and testing
- **Database Reset**: Clean slate for development

### Testing
- **Test Database**: Isolated test environment
- **Fixtures**: Predefined test data sets
- **Factory Classes**: Dynamic test data generation
- **Transaction Rollback**: Clean test isolation

## Monitoring and Maintenance

### Health Monitoring
- **Connection Pooling**: Monitor connection usage
- **Query Performance**: Slow query detection
- **Disk Usage**: Storage monitoring and alerts
- **Replication Lag**: Monitor read replica health

### Maintenance Tasks
- **VACUUM**: Regular table maintenance
- **ANALYZE**: Statistics updates
- **Index Rebuilding**: Performance optimization
- **Log Rotation**: Archive old logs

---

Next, explore the [User Models](./models/users.md) or dive into [Coaching Models](./models/coaching.md).
