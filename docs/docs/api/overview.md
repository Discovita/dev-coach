---
sidebar_position: 1
---

# API Overview

The Dev Coach system provides a comprehensive REST API for managing coaching sessions, user data, and system configuration.

## Base URL

- **Local Development**: `http://localhost:8000/api/v1`
- **Development Environment**: `https://your-dev-domain.com/api/v1`
- **Production**: `https://your-production-domain.com/api/v1`

## Authentication

The API uses Django's built-in authentication system with session-based authentication for web clients and token-based authentication for mobile/desktop applications.

### Authentication Methods

1. **Session Authentication** (Web)
   - Uses Django's session framework
   - Automatic CSRF protection
   - Suitable for web applications

2. **Token Authentication** (API)
   - Uses Django REST Framework tokens
   - Include token in Authorization header: `Authorization: Token <your-token>`
   - Suitable for mobile/desktop applications

## API Structure

The API is organized into the following main areas:

### User Management
- **Authentication**: Login, logout, password reset
- **User Profiles**: User information and preferences
- **Registration**: User signup and verification

### Coaching System
- **Coach State**: Current coaching phase and progress
- **Chat Messages**: Conversation history and management
- **Identities**: User-created identities and their data

### System Administration
- **Prompts**: AI prompt management and versioning
- **Actions**: System action definitions and handlers
- **Context Keys**: Data context management

### Test Scenarios
- **Test Data**: Development and testing utilities
- **Scenario Management**: Test scenario creation and execution

## Response Format

All API responses follow a consistent JSON format:

```json
{
  "status": "success",
  "data": {
    // Response data here
  },
  "message": "Optional message",
  "timestamp": "2024-01-01T00:00:00Z"
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

Error responses include detailed information:

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Authentication endpoints**: 5 requests per minute
- **General endpoints**: 100 requests per minute
- **Admin endpoints**: 50 requests per minute

## Versioning

The API uses URL-based versioning (e.g., `/api/v1/`). Breaking changes will be introduced in new versions while maintaining backward compatibility for a reasonable period.

## SDKs and Libraries

Official SDKs and libraries are available for:

- **JavaScript/TypeScript**: For web and Node.js applications
- **Python**: For backend integrations and scripts
- **React Hooks**: Custom hooks for React applications

## Getting Started

1. **Authentication**: Start with the [Authentication Guide](./authentication.md)
2. **User Management**: Learn about [User Operations](./users.md)
3. **Coaching API**: Explore [Coach State Management](./coaching.md)
4. **Admin API**: Access [System Administration](./admin.md)

## Interactive Documentation

For interactive API exploration, you can use:

- **Swagger UI**: Available at `/api/v1/schema/swagger-ui/`
- **ReDoc**: Available at `/api/v1/schema/redoc/`
- **OpenAPI Schema**: Available at `/api/v1/schema/`

---

Next, explore the [Authentication Guide](./authentication.md) or dive into [User Management](./users.md).
