---
sidebar_position: 1
---

# API Overview

The Dev Coach system provides a comprehensive REST API for managing coaching sessions, user data, and system administration. The API is built with Django REST Framework and uses JWT token-based authentication.

## Authentication

The API uses JWT (JSON Web Token) authentication via `djangorestframework-simplejwt`. All authenticated requests must include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Token Configuration

- **Access Token Lifetime**: 1 day
- **Refresh Token Lifetime**: 30 days
- **Token Type**: JWT (JSON Web Token)

## API Structure

The API is organized into the following main areas:

### Core Functionality

- **[Authentication](./endpoints/authentication.md)** - User registration, login, and password management
- **[Users](./endpoints/users.md)** - User profile management and data access
- **[Coach](./endpoints/coach.md)** - Main coaching conversation processing and state management

### System Administration

- **[Core](./endpoints/core.md)** - System enums and configuration data
- **[Prompts](./endpoints/prompts.md)** - AI prompt management and versioning
- **[Actions](./endpoints/actions.md)** - Action tracking and history

### Testing and Development

- **[Test Users](./endpoints/test-users.md)** - Admin access to user data for testing
- **[Test Scenarios](./endpoints/test-scenarios.md)** - Test scenario creation and management

## Response Format

API responses follow a consistent format, though the exact structure varies by endpoint:

### Success Responses

Most endpoints return data directly or with a `success` field:

```json
{
  "success": true,
  "data": {
    // Response data here
  }
}
```

### Error Responses

Error responses include detailed information:

```json
{
  "success": false,
  "error": "Error message describing the issue"
}
```

## Error Handling

The API uses standard HTTP status codes:

- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **500**: Internal Server Error

## Getting Started

1. **Authentication**: Start with [User Registration and Login](./endpoints/authentication.md)
2. **User Management**: Access [User Profile Data](./endpoints/users.md)
3. **Coaching**: Begin [Coaching Conversations](./endpoints/coach.md)
4. **System Admin**: Manage [Prompts and Configuration](./endpoints/prompts.md)

## Interactive Documentation

For interactive API exploration, you can use:

- **Swagger UI**: Available at `/api/v1/schema/swagger-ui/`
- **ReDoc**: Available at `/api/v1/schema/redoc/`
- **OpenAPI Schema**: Available at `/api/v1/schema/`

---

Next, explore the [Authentication Guide](./endpoints/authentication.md) or dive into [User Management](./endpoints/users.md).
