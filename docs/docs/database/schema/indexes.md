---
sidebar_position: 3
---

# Indexes & Constraints

This document details the database indexes, constraints, and performance optimization strategies used in the Dev Coach database.

## Primary Key Indexes

All models use UUID primary keys with automatic indexing:

### **UUID Primary Keys**

All tables use UUID primary keys. UUIDs are generated in Django application code (via `uuid.uuid4`), not by PostgreSQL's `gen_random_uuid()`.

```sql
-- All tables have UUID primary keys
CREATE TABLE users_user (
    id UUID PRIMARY KEY,
    -- other fields...
);

-- Pattern repeated for all models
```

**Benefits**:
- Globally unique identifiers
- No sequential numbering conflicts
- Better for distributed systems
- Built-in indexing by PostgreSQL

## Foreign Key Indexes

### **User Relationships**
```sql
-- User foreign keys are automatically indexed
CREATE INDEX users_user_test_scenario_id_idx ON users_user(test_scenario_id);

-- CoachState user relationship (OneToOne)
CREATE INDEX coach_states_coachstate_user_id_idx ON coach_states_coachstate(user_id);

-- Identity user relationship
CREATE INDEX identities_identity_user_id_idx ON identities_identity(user_id);

-- ChatMessage user relationship
CREATE INDEX chat_messages_chatmessage_user_id_idx ON chat_messages_chatmessage(user_id);

-- Action user relationship
CREATE INDEX actions_action_user_id_idx ON actions_action(user_id);

-- UserNote user relationship
CREATE INDEX user_notes_usernote_user_id_idx ON user_notes_usernote(user_id);
```

### **Identity Relationships**
```sql
-- CoachState identity relationships
CREATE INDEX coach_states_coachstate_current_identity_id_idx ON coach_states_coachstate(current_identity_id);
CREATE INDEX coach_states_coachstate_proposed_identity_id_idx ON coach_states_coachstate(proposed_identity_id);

-- Identity test scenario relationship
CREATE INDEX identities_identity_test_scenario_id_idx ON identities_identity(test_scenario_id);
```

### **ChatMessage Relationships**
```sql
-- ChatMessage test scenario relationship
CREATE INDEX chat_messages_chatmessage_test_scenario_id_idx ON chat_messages_chatmessage(test_scenario_id);

-- Action coach_message relationship
CREATE INDEX actions_action_coach_message_id_idx ON actions_action(coach_message_id);

-- UserNote source_message relationship
CREATE INDEX user_notes_usernote_source_message_id_idx ON user_notes_usernote(source_message_id);
```

### **Test Scenario Relationships**
```sql
-- TestScenario created_by relationship
CREATE INDEX test_scenario_testscenario_created_by_id_idx ON test_scenario_testscenario(created_by_id);
```

## Performance Indexes

### **Timestamp Indexes**

Only fields with explicit `db_index=True` in Django models have dedicated timestamp indexes:

```sql
-- ChatMessage timestamp (db_index=True)
CREATE INDEX chat_messages_chatmessage_timestamp_idx ON chat_messages_chatmessage(timestamp);

-- Action timestamp (db_index=True)
CREATE INDEX actions_action_timestamp_idx ON actions_action(timestamp);

-- Action updated_at (db_index=True)
CREATE INDEX actions_action_updated_at_idx ON actions_action(updated_at);
```

Note: Other models have `created_at`/`updated_at` fields with `auto_now_add`/`auto_now`, but these do NOT have explicit `db_index=True` and therefore have no dedicated indexes.

### **Action-Specific Indexes**

The Action model has the most explicit indexes due to its query patterns:

```sql
-- Composite index on user + timestamp
CREATE INDEX actions_action_user_id_timestamp_idx ON actions_action(user_id, timestamp);

-- Index on coach_message for join performance
CREATE INDEX actions_action_coach_message_id_idx ON actions_action(coach_message_id);

-- Index on action_type for filtering
CREATE INDEX actions_action_action_type_idx ON actions_action(action_type);

-- Index on updated_at for time-based queries
CREATE INDEX actions_action_updated_at_idx ON actions_action(updated_at);
```

## Unique Constraints

### **User Constraints**
```sql
-- Email uniqueness (User has no username field)
ALTER TABLE users_user ADD CONSTRAINT users_user_email_key UNIQUE (email);
```

### **CoachState Constraints**
```sql
-- One coach state per user
ALTER TABLE coach_states_coachstate ADD CONSTRAINT coach_states_coachstate_user_id_key UNIQUE (user_id);
```

### **Prompt Constraints**
```sql
-- Unique version per combination of prompt_type, coaching_phase, and version
ALTER TABLE prompts_prompt ADD CONSTRAINT prompts_prompt_prompt_type_coaching_phase_version_key UNIQUE (prompt_type, coaching_phase, version);
```

### **TestScenario Constraints**
```sql
-- Unique scenario names
ALTER TABLE test_scenario_testscenario ADD CONSTRAINT test_scenario_testscenario_name_key UNIQUE (name);
```

### **ReferenceImage Constraints**
```sql
-- One image per order slot per user
ALTER TABLE reference_images_referenceimage ADD CONSTRAINT reference_images_referenceimage_user_id_order_key UNIQUE (user_id, "order");
```

## Note on Constraints

Django uses `choices` on CharField/IntegerField for validation at the application level. These do **not** create PostgreSQL `CHECK` constraints in the database. Validation of phases, roles, states, and categories is enforced by Django, not by database-level constraints.

No partial indexes or GIN/full-text search indexes exist in this schema.

## Query Optimization

### **Common Query Patterns**

#### **User Session Data**
```sql
-- Optimized query for user session data
SELECT u.*, cs.*, ci.*, pi.*
FROM users_user u
LEFT JOIN coach_states_coachstate cs ON u.id = cs.user_id
LEFT JOIN identities_identity ci ON cs.current_identity_id = ci.id
LEFT JOIN identities_identity pi ON cs.proposed_identity_id = pi.id
WHERE u.id = $1;
```

#### **Conversation History**
```sql
-- Optimized conversation query
SELECT cm.*, a.*
FROM chat_messages_chatmessage cm
LEFT JOIN actions_action a ON cm.id = a.coach_message_id
WHERE cm.user_id = $1
ORDER BY cm.timestamp;
```

#### **Identity Progress**
```sql
-- Optimized identity progress query
SELECT i.*
FROM identities_identity i
WHERE i.user_id = $1
ORDER BY i.created_at;
```

### **Index Usage Monitoring**
```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Check table statistics
SELECT schemaname, tablename, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY seq_scan DESC;
```

## Maintenance

### **Index Maintenance**
```sql
-- Reindex tables periodically
REINDEX TABLE users_user;
REINDEX TABLE chat_messages_chatmessage;
REINDEX TABLE actions_action;

-- Analyze tables for statistics
ANALYZE users_user;
ANALYZE chat_messages_chatmessage;
ANALYZE actions_action;
```

### **Vacuum Operations**
```sql
-- Regular vacuum for cleanup
VACUUM ANALYZE users_user;
VACUUM ANALYZE chat_messages_chatmessage;
VACUUM ANALYZE actions_action;
```

## Performance Monitoring

### **Slow Query Detection**
```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000; -- 1 second
ALTER SYSTEM SET log_statement = 'all';
SELECT pg_reload_conf();
```

### **Connection Monitoring**
```sql
-- Monitor active connections
SELECT count(*) as active_connections 
FROM pg_stat_activity 
WHERE state = 'active';

-- Monitor connection by database
SELECT datname, count(*) as connections
FROM pg_stat_activity
GROUP BY datname;
```
