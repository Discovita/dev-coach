---
sidebar_position: 2
---

# Relationships

This document details the relationships between all models in the Dev Coach database, including foreign keys, related names, and common query patterns.

## Relationship Types

### **One-to-One Relationships**
Used when each instance of one model is associated with exactly one instance of another model.

### **One-to-Many Relationships**
Used when one instance of a model can be associated with multiple instances of another model.

### **Many-to-Many Relationships**
Used when multiple instances of one model can be associated with multiple instances of another model.

## Core Model Relationships

### **User → CoachState (One-to-One)**

**Purpose**: Each user has exactly one coaching session state.

**Implementation**:
```python
# User model
class User(AbstractUser):
    # No direct field - reverse relationship

# CoachState model  
class CoachState(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="coach_state"
    )
```

**Query Patterns**:
```python
# Get user's coach state
coach_state = user.coach_state

# Get user from coach state
user = coach_state.user

# Check if user has coach state
if hasattr(user, 'coach_state'):
    # User has coach state
```

**Usage Context**: Tracks the user's current coaching phase, progress, and session metadata.

---

### **User → Identity (One-to-Many)**

**Purpose**: Each user can have multiple identities across different life areas.

**Implementation**:
```python
# User model
class User(AbstractUser):
    # No direct field - reverse relationship

# Identity model
class Identity(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="identities"
    )
```

**Query Patterns**:
```python
# Get all user identities
identities = user.identities.all()

# Get identities by category
career_identities = user.identities.filter(category='CAREER')

# Get accepted identities
accepted_identities = user.identities.filter(state='ACCEPTED')
```

**Usage Context**: Stores user-created identities for different life areas (career, health, relationships, etc.).

---

### **User → ChatMessage (One-to-Many)**

**Purpose**: Each user has multiple chat messages in their conversation history.

**Implementation**:
```python
# User model
class User(AbstractUser):
    # No direct field - reverse relationship

# ChatMessage model
class ChatMessage(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_messages"
    )
```

**Query Patterns**:
```python
# Get all user messages
messages = user.chat_messages.all()

# Get recent messages
recent_messages = user.chat_messages.order_by('-timestamp')[:10]

# Get coach messages only
coach_messages = user.chat_messages.filter(role='COACH')
```

**Usage Context**: Maintains complete conversation history for context building and conversation reconstruction.

---

### **User → Action (One-to-Many)**

**Purpose**: Each user has multiple actions performed by the coach during their sessions.

**Implementation**:
```python
# User model
class User(AbstractUser):
    # No direct field - reverse relationship

# Action model
class Action(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="actions"
    )
```

**Query Patterns**:
```python
# Get all user actions
actions = user.actions.all()

# Get recent actions
recent_actions = user.actions.order_by('-timestamp')[:5]

# Get actions by type
identity_actions = user.actions.filter(action_type='CREATE_IDENTITY')
```

**Usage Context**: Tracks all actions performed by the coach for audit trails and debugging.

---

### **User → UserNote (One-to-Many)**

**Purpose**: Each user has multiple notes extracted by the Sentinel agent.

**Implementation**:
```python
# User model
class User(AbstractUser):
    # No direct field - reverse relationship

# UserNote model
class UserNote(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_notes"
    )
```

**Query Patterns**:
```python
# Get all user notes
notes = user.user_notes.all()

# Get recent notes
recent_notes = user.user_notes.order_by('-created_at')[:10]
```

**Usage Context**: Stores long-term memory about the user for future coaching sessions.

---

### **User → TestScenario (Many-to-One)**

**Purpose**: Users can be associated with test scenarios for development and testing.

**Implementation**:
```python
# User model
class User(AbstractUser):
    test_scenario = models.ForeignKey(
        'test_scenario.TestScenario',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

# TestScenario model
class TestScenario(models.Model):
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
```

**Query Patterns**:
```python
# Get test scenario for user
test_scenario = user.test_scenario

# Get all users in test scenario
test_users = test_scenario.user_set.all()

# Get users not in test scenarios
real_users = User.objects.filter(test_scenario__isnull=True)
```

**Usage Context**: Enables test data isolation for development and comprehensive testing.

---

## Identity Relationships

### **Identity → CoachState (One-to-Many via current_identity)**

**Purpose**: Identities can be the current focus of coaching sessions.

**Implementation**:
```python
# Identity model
class Identity(models.Model):
    # No direct field - reverse relationship

# CoachState model
class CoachState(models.Model):
    current_identity = models.ForeignKey(
        Identity,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="current_coach_states"
    )
```

**Query Patterns**:
```python
# Get coach states where this identity is current
coach_states = identity.current_coach_states.all()

# Get current identity for user
current_identity = user.coach_state.current_identity
```

**Usage Context**: Tracks which identity is currently being refined in the coaching session.

---

### **Identity → CoachState (One-to-Many via proposed_identity)**

**Purpose**: Identities can be proposed for user consideration.

**Implementation**:
```python
# Identity model
class Identity(models.Model):
    # No direct field - reverse relationship

# CoachState model
class CoachState(models.Model):
    proposed_identity = models.ForeignKey(
        Identity,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="proposed_coach_states"
    )
```

**Query Patterns**:
```python
# Get coach states where this identity is proposed
coach_states = identity.proposed_coach_states.all()

# Get proposed identity for user
proposed_identity = user.coach_state.proposed_identity
```

**Usage Context**: Tracks which identity is currently proposed to the user for acceptance.

---

## ChatMessage Relationships

### **ChatMessage → Action (One-to-Many)**

**Purpose**: Chat messages can trigger multiple actions.

**Implementation**:
```python
# ChatMessage model
class ChatMessage(models.Model):
    # No direct field - reverse relationship

# Action model
class Action(models.Model):
    coach_message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="triggered_actions"
    )
```

**Query Patterns**:
```python
# Get actions triggered by this message
actions = chat_message.triggered_actions.all()

# Get messages that triggered actions
action_messages = ChatMessage.objects.filter(triggered_actions__isnull=False)
```

**Usage Context**: Links actions to the specific coach messages that triggered them for context and debugging.

---

### **ChatMessage → UserNote (One-to-Many)**

**Purpose**: Chat messages can be the source of user notes.

**Implementation**:
```python
# ChatMessage model
class ChatMessage(models.Model):
    # No direct field - reverse relationship

# UserNote model
class UserNote(models.Model):
    source_message = models.ForeignKey(
        ChatMessage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generated_notes"
    )
```

**Query Patterns**:
```python
# Get notes generated from this message
notes = chat_message.generated_notes.all()

# Get messages that generated notes
note_messages = ChatMessage.objects.filter(generated_notes__isnull=False)
```

**Usage Context**: Tracks which chat messages led to the extraction of user notes by the Sentinel agent.

---

## Test Scenario Relationships

### **TestScenario → All Models (One-to-Many)**

**Purpose**: Test scenarios can contain instances of all other models.

**Implementation**:
```python
# TestScenario model
class TestScenario(models.Model):
    # No direct fields - reverse relationships

# All other models have:
test_scenario = models.ForeignKey(
    'test_scenario.TestScenario',
    null=True,
    blank=True,
    on_delete=models.SET_NULL
)
```

**Query Patterns**:
```python
# Get all test data for a scenario
test_users = test_scenario.user_set.all()
test_coach_states = test_scenario.coachstate_set.all()
test_identities = test_scenario.identity_set.all()
test_messages = test_scenario.chatmessage_set.all()
test_actions = test_scenario.action_set.all()
test_notes = test_scenario.usernote_set.all()
```

**Usage Context**: Enables complete test scenario isolation for development and testing.

---

## Common Query Patterns

### **User Session Data**
```python
# Get complete user session data
user_data = User.objects.select_related(
    'coach_state',
    'coach_state__current_identity',
    'coach_state__proposed_identity'
).prefetch_related(
    'identities',
    'chat_messages',
    'actions',
    'user_notes'
).get(id=user_id)
```

### **Conversation with Actions**
```python
# Get conversation with triggered actions
conversation = ChatMessage.objects.select_related('user').prefetch_related(
    'triggered_actions'
).filter(user=user).order_by('timestamp')
```

### **Identity Progress**
```python
# Get user's identity progress
identity_progress = Identity.objects.filter(user=user).select_related(
    'user'
).order_by('created_at')
```

### **Test Scenario Data**
```python
# Get complete test scenario data
scenario_data = TestScenario.objects.prefetch_related(
    'user_set',
    'coachstate_set',
    'identity_set',
    'chatmessage_set',
    'action_set',
    'usernote_set'
).get(id=scenario_id)
```

## Relationship Constraints

### **Cascade Deletes**
- User deletion cascades to all related data
- ChatMessage deletion cascades to triggered actions
- TestScenario deletion cascades to all test data

### **SET NULL**
- Optional relationships use SET NULL
- Allows data preservation when parent is deleted
- Used for test scenario isolation

### **Unique Constraints**
- One coach state per user
- Unique email per user
- Unique version per coaching phase
