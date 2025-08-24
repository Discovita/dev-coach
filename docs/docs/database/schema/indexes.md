---
sidebar_position: 3
---

# Indexes & Constraints

This document details the database indexes, constraints, and performance optimization strategies used in the Dev Coach database.

## Primary Key Indexes

All models use UUID primary keys with automatic indexing:

### **UUID Primary Keys**
```sql
-- All tables have UUID primary keys
CREATE TABLE users_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- other fields...
);

CREATE TABLE coach_states_coachstate (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
```sql
-- Time-based queries for all models
CREATE INDEX users_user_created_at_idx ON users_user(created_at);
CREATE INDEX users_user_updated_at_idx ON users_user(updated_at);
CREATE INDEX users_user_last_login_idx ON users_user(last_login);

CREATE INDEX coach_states_coachstate_updated_at_idx ON coach_states_coachstate(updated_at);

CREATE INDEX identities_identity_created_at_idx ON identities_identity(created_at);
CREATE INDEX identities_identity_updated_at_idx ON identities_identity(updated_at);

CREATE INDEX chat_messages_chatmessage_timestamp_idx ON chat_messages_chatmessage(timestamp);

CREATE INDEX actions_action_timestamp_idx ON actions_action(timestamp);

CREATE INDEX user_notes_usernote_created_at_idx ON user_notes_usernote(created_at);

CREATE INDEX test_scenario_testscenario_created_at_idx ON test_scenario_testscenario(created_at);
CREATE INDEX test_scenario_testscenario_updated_at_idx ON test_scenario_testscenario(updated_at);
```

### **Composite Indexes**
```sql
-- User + timestamp for chronological queries
CREATE INDEX actions_action_user_id_timestamp_idx ON actions_action(user_id, timestamp);

-- User + role for message filtering
CREATE INDEX chat_messages_chatmessage_user_id_role_idx ON chat_messages_chatmessage(user_id, role);

-- User + category for identity filtering
CREATE INDEX identities_identity_user_id_category_idx ON identities_identity(user_id, category);

-- User + state for identity state queries
CREATE INDEX identities_identity_user_id_state_idx ON identities_identity(user_id, state);
```

### **Search Indexes**
```sql
-- Full-text search on message content
CREATE INDEX chat_messages_chatmessage_content_gin_idx ON chat_messages_chatmessage USING gin(to_tsvector('english', content));

-- Full-text search on user notes
CREATE INDEX user_notes_usernote_note_gin_idx ON user_notes_usernote USING gin(to_tsvector('english', note));

-- Full-text search on identity content
CREATE INDEX identities_identity_affirmation_gin_idx ON identities_identity USING gin(to_tsvector('english', affirmation));
CREATE INDEX identities_identity_visualization_gin_idx ON identities_identity USING gin(to_tsvector('english', visualization));
```

## Unique Constraints

### **User Constraints**
```sql
-- Email uniqueness
ALTER TABLE users_user ADD CONSTRAINT users_user_email_key UNIQUE (email);

-- Username uniqueness (if used)
ALTER TABLE users_user ADD CONSTRAINT users_user_username_key UNIQUE (username);
```

### **CoachState Constraints**
```sql
-- One coach state per user
ALTER TABLE coach_states_coachstate ADD CONSTRAINT coach_states_coachstate_user_id_key UNIQUE (user_id);
```

### **Prompt Constraints**
```sql
-- Unique version per coaching phase
ALTER TABLE prompts_prompt ADD CONSTRAINT prompts_prompt_coaching_phase_version_key UNIQUE (coaching_phase, version);
```

### **TestScenario Constraints**
```sql
-- Unique scenario names
ALTER TABLE test_scenario_testscenario ADD CONSTRAINT test_scenario_testscenario_name_key UNIQUE (name);
```

## Check Constraints

### **Data Validation**
```sql
-- Email format validation
ALTER TABLE users_user ADD CONSTRAINT users_user_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Phase validation
ALTER TABLE coach_states_coachstate ADD CONSTRAINT coach_states_coachstate_current_phase_check 
CHECK (current_phase IN ('GET_TO_KNOW_YOU', 'IDENTITY_CREATION', 'IDENTITY_REFINEMENT', 'INTEGRATION', 'COMPLETED'));

-- Role validation
ALTER TABLE chat_messages_chatmessage ADD CONSTRAINT chat_messages_chatmessage_role_check 
CHECK (role IN ('USER', 'COACH'));

-- State validation
ALTER TABLE identities_identity ADD CONSTRAINT identities_identity_state_check 
CHECK (state IN ('PROPOSED', 'ACCEPTED', 'REFINEMENT_COMPLETE'));
```

### **Business Logic Constraints**
```sql
-- Version must be positive
ALTER TABLE prompts_prompt ADD CONSTRAINT prompts_prompt_version_check CHECK (version > 0);

-- Timestamps must be valid
ALTER TABLE users_user ADD CONSTRAINT users_user_created_at_updated_at_check CHECK (created_at <= updated_at);
```

## Partial Indexes

### **Active Data Indexes**
```sql
-- Only index active prompts
CREATE INDEX prompts_prompt_active_idx ON prompts_prompt(coaching_phase, version) WHERE is_active = true;

-- Only index non-test users
CREATE INDEX users_user_real_users_idx ON users_user(email, created_at) WHERE test_scenario_id IS NULL;

-- Only index recent messages
CREATE INDEX chat_messages_chatmessage_recent_idx ON chat_messages_chatmessage(user_id, timestamp) 
WHERE timestamp > NOW() - INTERVAL '30 days';
```

### **Test Scenario Indexes**
```sql
-- Separate indexes for test data
CREATE INDEX users_user_test_scenario_idx ON users_user(test_scenario_id) WHERE test_scenario_id IS NOT NULL;
CREATE INDEX chat_messages_chatmessage_test_scenario_idx ON chat_messages_chatmessage(test_scenario_id) WHERE test_scenario_id IS NOT NULL;
```

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
