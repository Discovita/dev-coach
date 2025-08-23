---
sidebar_position: 1
---

# Authentication

The Dev Coach API provides comprehensive authentication capabilities for both web and mobile applications.

## Authentication Methods

### Session Authentication (Web)

Used for web applications that maintain user sessions.

#### Login

**Endpoint**: `POST /api/v1/auth/login/`

**Request Body**:
```json
{
  "username": "user@example.com",
  "password": "securepassword"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": 1,
      "username": "user@example.com",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "date_joined": "2024-01-01T00:00:00Z"
    },
    "session_id": "abc123def456"
  },
  "message": "Login successful"
}
```

#### Logout

**Endpoint**: `POST /api/v1/auth/logout/`

**Response**:
```json
{
  "status": "success",
  "message": "Logout successful"
}
```

### Token Authentication (API)

Used for mobile applications and API clients.

#### Get Token

**Endpoint**: `POST /api/v1/auth/token/`

**Request Body**:
```json
{
  "username": "user@example.com",
  "password": "securepassword"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": {
      "id": 1,
      "username": "user@example.com",
      "email": "user@example.com"
    }
  }
}
```

#### Using Token

Include the token in the Authorization header:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Registration

### User Registration

**Endpoint**: `POST /api/v1/auth/register/`

**Request Body**:
```json
{
  "username": "newuser@example.com",
  "email": "newuser@example.com",
  "password": "securepassword",
  "password_confirm": "securepassword",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": 2,
      "username": "newuser@example.com",
      "email": "newuser@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "is_active": false,
      "date_joined": "2024-01-01T00:00:00Z"
    }
  },
  "message": "Registration successful. Please check your email for verification."
}
```

### Email Verification

**Endpoint**: `POST /api/v1/auth/verify-email/`

**Request Body**:
```json
{
  "token": "verification_token_from_email"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Email verified successfully"
}
```

## Password Management

### Password Reset Request

**Endpoint**: `POST /api/v1/auth/password-reset/`

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Password reset email sent"
}
```

### Password Reset Confirm

**Endpoint**: `POST /api/v1/auth/password-reset-confirm/`

**Request Body**:
```json
{
  "token": "reset_token_from_email",
  "new_password": "newsecurepassword",
  "new_password_confirm": "newsecurepassword"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Password reset successful"
}
```

## User Profile

### Get Current User

**Endpoint**: `GET /api/v1/auth/user/`

**Headers**:
```
Authorization: Token your_token_here
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": 1,
      "username": "user@example.com",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "date_joined": "2024-01-01T00:00:00Z",
      "profile": {
        "bio": "Life coach enthusiast",
        "timezone": "America/New_York",
        "preferences": {
          "notifications": true,
          "theme": "dark"
        }
      }
    }
  }
}
```

### Update User Profile

**Endpoint**: `PUT /api/v1/auth/user/`

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "profile": {
    "bio": "Updated bio",
    "timezone": "America/Los_Angeles",
    "preferences": {
      "notifications": false,
      "theme": "light"
    }
  }
}
```

## Security Features

### CSRF Protection

For session-based authentication, CSRF tokens are required for state-changing operations.

**Get CSRF Token**:
```
GET /api/v1/auth/csrf/
```

**Using CSRF Token**:
```
X-CSRFToken: your_csrf_token_here
```

### Rate Limiting

Authentication endpoints are rate-limited:

- **Login**: 5 attempts per minute
- **Registration**: 3 attempts per hour
- **Password Reset**: 3 attempts per hour

### Session Management

- **Session Timeout**: 24 hours of inactivity
- **Concurrent Sessions**: Up to 5 active sessions per user
- **Session Invalidation**: Automatic on password change

## Error Responses

### Invalid Credentials

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid username or password"
  }
}
```

### Account Locked

```json
{
  "status": "error",
  "error": {
    "code": "ACCOUNT_LOCKED",
    "message": "Account temporarily locked due to too many failed attempts"
  }
}
```

### Email Not Verified

```json
{
  "status": "error",
  "error": {
    "code": "EMAIL_NOT_VERIFIED",
    "message": "Please verify your email address before logging in"
  }
}
```

## Best Practices

### Token Security

1. **Store tokens securely** in mobile apps
2. **Rotate tokens regularly** for long-lived applications
3. **Never expose tokens** in client-side code
4. **Use HTTPS** for all authentication requests

### Session Security

1. **Use secure cookies** for session storage
2. **Implement session timeout** for inactive users
3. **Log authentication events** for security monitoring
4. **Validate session integrity** on each request

### Password Security

1. **Enforce strong passwords** (minimum 8 characters, mixed case, numbers)
2. **Implement password history** to prevent reuse
3. **Use secure password reset** with time-limited tokens
4. **Hash passwords** using bcrypt or similar

---

Next, explore [User Management](./../endpoints/users.md) or learn about [API Error Handling](./../errors.md).
