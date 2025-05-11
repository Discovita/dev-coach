# Authentication API Documentation

## Overview

The Authentication API provides endpoints for user authentication, registration, and password management. It handles user authentication flows, token management, and secure access to the Coach platform.

## Authentication

Most endpoints are protected and require authentication. Requests must include a valid JWT token:

```
Authorization: Bearer <your_token>
```

## Response Format

All endpoints follow a consistent response format:

### Success Response

```json
{
  "success": true,
  "data": {
    // Response data specific to the endpoint
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": "Human readable error message"
}
```

## Endpoints

### Register

```http
POST /api/v1/auth/register/
```

Creates a new user account and returns authentication tokens.

#### Request Body

| Field    | Type   | Required | Description             | Validation                                                                                                             |
| -------- | ------ | -------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| email    | string | Yes      | User's email address    | Must be unique, valid email format                                                                                     |
| password | string | Yes      | User's desired password | - Minimum 8 characters<br>- Must contain uppercase letter<br>- Must contain number<br>- Must contain special character |

#### Success Response

```json
{
  "success": true,
  "user_id": "uuid",
  "tokens": {
    "refresh": "refresh_token_string",
    "access": "access_token_string"
  }
}
```

#### Error Responses

| Status Code | Description      | Response Body                                                                                                                    |
| ----------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 400         | Email Exists     | `{"success": false, "error": "A user with that email already exists"}`                                                           |
| 400         | Invalid Password | `{"success": false, "error": "Password must contain at least 8 characters, including uppercase, number, and special character"}` |
| 500         | Creation Failed  | `{"success": false, "error": "Unable to create new user: {error details}"}`                                                      |

#### Implementation Details

The endpoint:

1. Validates email uniqueness
2. Validates password requirements
3. Creates user account
4. Attempts to sync with PowerPath profile data (if available)
5. Creates a basic profile if PowerPath sync fails
6. Generates JWT tokens

If PowerPath sync fails, the user is still created with a basic profile, and the operation succeeds.

### Login

```http
POST /api/v1/auth/login/
```

Authenticates user credentials and returns JWT tokens.

#### Request Body

| Field    | Type   | Required | Description     |
| -------- | ------ | -------- | --------------- |
| email    | string | Yes      | User's email    |
| password | string | Yes      | User's password |

#### Success Response

```json
{
  "success": true,
  "user_id": "uuid",
  "tokens": {
    "refresh": "refresh_token_string",
    "access": "access_token_string"
  }
}
```

#### Error Responses

| Status Code | Description         | Response Body                                                         |
| ----------- | ------------------- | --------------------------------------------------------------------- |
| 400         | Invalid Credentials | `{"success": false, "error": "Invalid email or password"}`            |
| 400         | Missing Fields      | `{"success": false, "error": "Both email and password are required"}` |

#### Implementation Details

The endpoint:

1. Validates presence of email and password
2. Authenticates credentials
3. Attempts to sync with PowerPath profile data (if available)
4. Updates basic profile if PowerPath sync fails
5. Generates new JWT tokens

PowerPath sync failures do not affect login success - a basic profile update will be performed instead.

### Forgot Password

```http
POST /api/v1/auth/forgot-password/
```

Initiates password reset process by sending a reset link to user's email. The email is sent using AWS SES (Simple Email Service).

#### Request Body

| Field | Type   | Required | Description              |
| ----- | ------ | -------- | ------------------------ |
| email | string | Yes      | Email address of account |

#### Success Response

```json
{
  "success": true,
  "message": "Password reset instructions sent to email"
}
```

#### Error Responses

| Status Code | Description       | Response Body                                                                                |
| ----------- | ----------------- | -------------------------------------------------------------------------------------------- |
| 400         | User Not Found    | `{"success": false, "error": "No user found with this email address"}`                       |
| 500         | Email Send Failed | `{"success": false, "error": "Failed to send password reset email. Please try again later"}` |

#### Implementation Details

The endpoint:

1. Verifies the email exists in the system
2. Generates a secure reset token (32 bytes hex)
3. Creates a reset URL with the token
4. Sends an email via AWS SES containing:
   - HTML and text versions of the reset instructions
   - Reset URL with token
   - 24-hour expiration notice

If the email service fails (e.g., AWS SES issues), the endpoint will return a 500 error and log the failure, but the token will still be generated and stored. This means the user can retry the forgot-password request and receive the same token if within the expiration window.

### Reset Password

```http
POST /api/v1/auth/reset-password/
```

Completes the password reset process using the token from email.

#### Request Body

| Field        | Type   | Required | Description            |
| ------------ | ------ | -------- | ---------------------- |
| token        | string | Yes      | Reset token from email |
| new_password | string | Yes      | New password           |

#### Success Response

```json
{
  "success": true,
  "message": "Password successfully reset"
}
```

#### Error Responses

| Status Code | Description      | Response Body                                                                                                                    |
| ----------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 400         | Invalid Token    | `{"success": false, "error": "Invalid or expired reset token"}`                                                                  |
| 400         | Invalid Password | `{"success": false, "error": "Password must contain at least 8 characters, including uppercase, number, and special character"}` |
| 404         | Token Not Found  | `{"success": false, "error": "Reset token not found"}`                                                                           |

#### Implementation Details

The endpoint:

1. Validates token existence and expiration (24-hour window)
2. Validates new password requirements
3. Updates user's password
4. Invalidates token after successful reset

#### Error Responses

| Status Code | Description       | Response Body                                                                 |
| ----------- | ----------------- | ----------------------------------------------------------------------------- |
| 401         | Not Authenticated | `{"success": false, "error": "Authentication credentials were not provided"}` |
| 403         | Token Expired     | `{"success": false, "error": "Token has expired"}`                            |

### LTI Launch Request

```http
POST /api/v1/auth/lti-launch-request/
```

Handles LTI 1.3 launch requests from learning management systems.

#### Request Body

| Field           | Type   | Required | Description                      |
| --------------- | ------ | -------- | -------------------------------- |
| messageType     | string | Yes      | Must be "LtiResourceLinkRequest" |
| version         | string | Yes      | LTI version                      |
| resourceLink    | object | Yes      | Contains resource link ID        |
| iss             | string | Yes      | Issuer URL                       |
| deployment_id   | string | Yes      | LTI deployment ID                |
| target_link_uri | string | Yes      | Target resource URL              |
| role            | string | Yes      | User's role                      |
| sub             | string | Yes      | User's email                     |
| given_name      | string | Yes      | User's first name                |
| family_name     | string | Yes      | User's last name                 |
| nonce           | string | Yes      | Unique request identifier        |
| iat             | string | Yes      | Issued at timestamp              |
| exp             | string | Yes      | Expiration timestamp             |
| jti             | string | Yes      | JWT ID                           |

Optional StudyReel-specific fields:

| Field                    | Type   | Required | Description            |
| ------------------------ | ------ | -------- | ---------------------- |
| studyreel_grade_math     | string | No       | Math grade level       |
| studyreel_grade_language | string | No       | Language grade level   |
| studyreel_grade_science  | string | No       | Science grade level    |
| studyreel_grade_reading  | string | No       | Reading grade level    |
| age_grade                | string | No       | Student's grade level  |
| user_acquisition_source  | string | No       | How user was acquired  |
| map_rit_math             | string | No       | MAP RIT math score     |
| map_rit_language         | string | No       | MAP RIT language score |
| map_rit_science          | string | No       | MAP RIT science score  |
| map_rit_reading          | string | No       | MAP RIT reading score  |

#### Success Response

```json
{
  "success": true,
  "token": "lti_token_string",
  "redirect_url": "https://example.com/launch"
}
```

#### Error Responses

| Status Code | Description             | Response Body                                                                                             |
| ----------- | ----------------------- | --------------------------------------------------------------------------------------------------------- |
| 400         | Invalid Message Type    | `{"success": false, "error": "Expected message type LtiResourceLinkRequest but received {type}"}`         |
| 400         | Invalid Issuer          | `{"success": false, "error": "Expected issuer https://studyreel.alpha1edtech.com but received {issuer}"}` |
| 400         | Missing Fields          | `{"success": false, "error": "Required field {field_name} is missing"}`                                   |
| 500         | Token Generation Failed | `{"success": false, "error": "Failed to generate LTI token"}`                                             |

#### Implementation Details

The endpoint:

1. Validates all required LTI launch parameters
2. Verifies message type and issuer
3. Generates a short-lived LTI token (15-minute expiration)
4. Creates/updates user profile with provided data
5. Returns token and redirect URL

### Validate LTI Token

```http
POST /api/v1/auth/validate-lti-token/
```

Validates a one-time LTI token and returns user session tokens.

#### Request Body

| Field | Type   | Required | Description           |
| ----- | ------ | -------- | --------------------- |
| token | string | Yes      | LTI token to validate |

#### Success Response

```json
{
  "success": true,
  "user": {
    "id": 123,
    "email": "user@example.com"
  },
  "profile": {
    // User profile data
  },
  "tokens": {
    "refresh": "refresh_token_string",
    "access": "access_token_string"
  }
}
```
