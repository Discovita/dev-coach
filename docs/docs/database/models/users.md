---
sidebar_position: 1
---

# User Models

The user management system in Dev Coach is built around Django's built-in User model with custom extensions for coaching-specific functionality.

## Core User Model

### User (Django Built-in)

The base user model extends Django's AbstractUser with additional fields for coaching functionality.

```python
class User(AbstractUser):
    # Inherited from AbstractUser:
    # username, email, first_name, last_name, password, is_active, etc.
    
    # Custom fields
    email_verified = models.BooleanField(default=False)
    coaching_start_date = models.DateTimeField(null=True, blank=True)
    last_coaching_session = models.DateTimeField(null=True, blank=True)
    
    # Meta
    class Meta:
        db_table = 'users_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
```

**Fields**:
- `id` (AutoField): Primary key
- `username` (CharField): Unique username, max 150 characters
- `email` (EmailField): Unique email address
- `first_name` (CharField): User's first name, max 150 characters
- `last_name` (CharField): User's last name, max 150 characters
- `password` (CharField): Hashed password
- `is_active` (BooleanField): Whether the user account is active
- `is_staff` (BooleanField): Whether the user can access admin
- `is_superuser` (BooleanField): Whether the user has all permissions
- `date_joined` (DateTimeField): When the user account was created
- `last_login` (DateTimeField): When the user last logged in
- `email_verified` (BooleanField): Whether email has been verified
- `coaching_start_date` (DateTimeField): When user started coaching
- `last_coaching_session` (DateTimeField): Last coaching session timestamp

**Indexes**:
- Primary key on `id`
- Unique index on `username`
- Unique index on `email`
- Index on `is_active`
- Index on `date_joined`

## User Profile Model

### UserProfile

Extended user information specific to coaching functionality.

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    bio = models.TextField(blank=True, max_length=500)
    timezone = models.CharField(max_length=50, default='UTC')
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Coaching Preferences
    coaching_goals = models.JSONField(default=dict)
    preferred_coaching_style = models.CharField(max_length=50, choices=COACHING_STYLE_CHOICES)
    session_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    
    # Notification Settings
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    notification_frequency = models.CharField(max_length=20, default='daily')
    
    # UI Preferences
    theme = models.CharField(max_length=20, default='light')
    language = models.CharField(max_length=10, default='en')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_userprofile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
```

**Fields**:
- `id` (AutoField): Primary key
- `user` (OneToOneField): Link to User model
- `bio` (TextField): User biography, max 500 characters
- `timezone` (CharField): User's timezone, max 50 characters
- `date_of_birth` (DateField): User's date of birth (optional)
- `coaching_goals` (JSONField): User's coaching goals and objectives
- `preferred_coaching_style` (CharField): Preferred coaching approach
- `session_frequency` (CharField): How often user wants coaching sessions
- `email_notifications` (BooleanField): Whether to send email notifications
- `push_notifications` (BooleanField): Whether to send push notifications
- `notification_frequency` (CharField): How often to send notifications
- `theme` (CharField): UI theme preference
- `language` (CharField): Preferred language
- `created_at` (DateTimeField): When profile was created
- `updated_at` (DateTimeField): When profile was last updated

**Choices**:
```python
COACHING_STYLE_CHOICES = [
    ('directive', 'Directive'),
    ('supportive', 'Supportive'),
    ('collaborative', 'Collaborative'),
    ('challenging', 'Challenging'),
]

FREQUENCY_CHOICES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('biweekly', 'Bi-weekly'),
    ('monthly', 'Monthly'),
]
```

## Email Verification Model

### EmailVerification

Manages email verification tokens for user registration and password reset.

```python
class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'authentication_emailverification'
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'
```

**Fields**:
- `id` (AutoField): Primary key
- `user` (ForeignKey): Link to User model
- `token` (CharField): Unique verification token
- `email` (EmailField): Email address to verify
- `verification_type` (CharField): Type of verification
- `is_used` (BooleanField): Whether token has been used
- `expires_at` (DateTimeField): When token expires
- `created_at` (DateTimeField): When token was created

**Choices**:
```python
VERIFICATION_TYPES = [
    ('email_verification', 'Email Verification'),
    ('password_reset', 'Password Reset'),
    ('email_change', 'Email Change'),
]
```

## Relationships

### User → UserProfile
- **Type**: One-to-One
- **Related Name**: `profile`
- **Cascade**: Delete profile when user is deleted

### User → EmailVerification
- **Type**: One-to-Many
- **Related Name**: `email_verifications`
- **Cascade**: Delete verifications when user is deleted

### User → CoachState
- **Type**: One-to-One
- **Related Name**: `coach_state`
- **Cascade**: Delete coach state when user is deleted

### User → ChatMessage
- **Type**: One-to-Many
- **Related Name**: `chat_messages`
- **Cascade**: Delete messages when user is deleted

### User → Identity
- **Type**: One-to-Many
- **Related Name**: `identities`
- **Cascade**: Delete identities when user is deleted

## Database Schema

### users_user Table

```sql
CREATE TABLE users_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    coaching_start_date TIMESTAMP WITH TIME ZONE,
    last_coaching_session TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX users_user_is_active_idx ON users_user(is_active);
CREATE INDEX users_user_date_joined_idx ON users_user(date_joined);
CREATE INDEX users_user_email_verified_idx ON users_user(email_verified);
```

### users_userprofile Table

```sql
CREATE TABLE users_userprofile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    bio TEXT,
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    date_of_birth DATE,
    coaching_goals JSONB NOT NULL DEFAULT '{}',
    preferred_coaching_style VARCHAR(50),
    session_frequency VARCHAR(20),
    email_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    push_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    notification_frequency VARCHAR(20) NOT NULL DEFAULT 'daily',
    theme VARCHAR(20) NOT NULL DEFAULT 'light',
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX users_userprofile_timezone_idx ON users_userprofile(timezone);
CREATE INDEX users_userprofile_created_at_idx ON users_userprofile(created_at);
```

### authentication_emailverification Table

```sql
CREATE TABLE authentication_emailverification (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    token VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    verification_type VARCHAR(20) NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX authentication_emailverification_token_idx ON authentication_emailverification(token);
CREATE INDEX authentication_emailverification_user_id_idx ON authentication_emailverification(user_id);
CREATE INDEX authentication_emailverification_expires_at_idx ON authentication_emailverification(expires_at);
```

## Query Examples

### Get User with Profile

```python
# Using select_related for efficient querying
user = User.objects.select_related('profile').get(id=1)
print(user.profile.bio)
```

### Get Users by Coaching Start Date

```python
# Users who started coaching in the last 30 days
recent_users = User.objects.filter(
    coaching_start_date__gte=timezone.now() - timedelta(days=30)
)
```

### Get Email Verifications by Type

```python
# Get all unused email verification tokens
unused_tokens = EmailVerification.objects.filter(
    is_used=False,
    expires_at__gt=timezone.now()
)
```

### Update User Profile

```python
# Update user preferences
user.profile.coaching_goals = {
    'career': 'Get promoted to senior developer',
    'health': 'Exercise 3 times per week'
}
user.profile.save()
```

## Data Validation

### User Model Validation

- **Username**: Must be unique, alphanumeric with underscores
- **Email**: Must be unique and valid email format
- **Password**: Minimum 8 characters, complexity requirements
- **Email Verification**: Required before account activation

### UserProfile Validation

- **Timezone**: Must be valid IANA timezone identifier
- **Date of Birth**: Must be in the past, reasonable age range
- **Coaching Goals**: Must be valid JSON structure
- **Notification Frequency**: Must be one of predefined choices

## Security Considerations

### Password Security

- Passwords are hashed using Django's password hashers
- Default uses PBKDF2 with SHA256
- Configurable password complexity requirements
- Password history to prevent reuse

### Email Verification

- Tokens are cryptographically secure random strings
- Tokens expire after 24 hours
- One-time use only
- Rate limiting on token generation

### Data Privacy

- Personal data is encrypted at rest
- GDPR compliance with right to be forgotten
- Data retention policies for inactive accounts
- Audit logging for data access

---

Next, explore [Coaching Models](./coaching.md) or learn about [Database Schema](./../schema/tables.md).
