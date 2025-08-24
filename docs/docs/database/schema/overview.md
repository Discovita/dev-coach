---
sidebar_position: 1
---

# Schema Overview

The Dev Coach database schema is designed around a coaching workflow that guides users through identity creation, refinement, and integration. The schema supports user management, conversation tracking, action logging, and test scenario isolation.

## Database Technology

- **Database**: PostgreSQL 17.1
- **ORM**: Django ORM with custom managers
- **Migrations**: Django migrations for schema management
- **Extensions**: PostgreSQL ArrayField for list storage
- **Backup Strategy**: Automated daily backups with point-in-time recovery

## Core Design Principles

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
- Enables comprehensive testing without data pollution

### 4. **Extensibility**
- JSON fields for flexible metadata storage
- Array fields for list-based data
- Version control for prompts and configurations

## Schema Architecture

```
User (Core)
├── CoachState (One-to-One)
│   ├── current_identity → Identity
│   └── proposed_identity → Identity
├── Identities (One-to-Many)
├── ChatMessages (One-to-Many)
├── Actions (One-to-Many)
├── UserNotes (One-to-Many)
└── TestScenario (Many-to-One, optional)

Identity (Core)
├── User (Many-to-One)
└── CoachState (One-to-Many via current/proposed)

ChatMessage (Core)
├── User (Many-to-One)
├── Actions (One-to-Many via triggered_actions)
└── UserNotes (One-to-Many via source_message)

Prompt (Standalone)
├── No direct relationships
└── Version control via coaching_phase + version

TestScenario (Standalone)
├── User (One-to-Many via created_by)
└── All models (One-to-Many via test_scenario)
```

## Key Relationships

### **User Relationships**
- **One-to-One**: CoachState (session state)
- **One-to-Many**: Identities, ChatMessages, Actions, UserNotes
- **Many-to-One**: TestScenario (optional, for testing)

### **Identity Relationships**
- **Many-to-One**: User (owner)
- **One-to-Many**: CoachState (as current_identity or proposed_identity)
- **Many-to-One**: TestScenario (optional)

### **ChatMessage Relationships**
- **Many-to-One**: User (sender/recipient)
- **One-to-Many**: Actions (triggered actions)
- **One-to-Many**: UserNotes (source messages)
- **Many-to-One**: TestScenario (optional)

### **Action Relationships**
- **Many-to-One**: User (performer)
- **Many-to-One**: ChatMessage (trigger)
- **Many-to-One**: TestScenario (optional)

## Data Flow Patterns

### **Coaching Session Flow**
1. User creates account → User record
2. CoachState created → Session tracking begins
3. ChatMessages recorded → Conversation history
4. Actions logged → Audit trail
5. Identities created → User progress
6. UserNotes extracted → Long-term memory

### **Test Scenario Flow**
1. TestScenario created → Template definition
2. Test data populated → Isolated test environment
3. All models linked → Complete test state
4. Testing performed → Scenario validation
5. Cleanup → Test data isolation

## Schema Constraints

### **Referential Integrity**
- All foreign keys have proper constraints
- Cascade deletes for dependent data
- SET NULL for optional relationships

### **Business Logic Constraints**
- Unique email per user
- One coach state per user
- Version uniqueness per coaching phase
- Test scenario isolation enforcement

### **Data Validation**
- Email format validation
- UUID primary keys
- Timestamp auto-management
- JSON field validation

## Performance Considerations

### **Indexing Strategy**
- Primary keys on all tables (UUID)
- Foreign key indexes for join performance
- Composite indexes for common queries
- Time-based indexes for chronological queries

### **Query Optimization**
- Select_related for foreign key joins
- Prefetch_related for reverse relationships
- Database-level constraints for data integrity
- Efficient array field operations

## Migration Strategy

### **Schema Evolution**
- Django migrations for all changes
- Backward compatibility maintained
- Data migration scripts when needed
- Zero-downtime deployment support

### **Version Control**
- Migration files in version control
- Rollback procedures documented
- Test data migration validation
- Production migration testing
