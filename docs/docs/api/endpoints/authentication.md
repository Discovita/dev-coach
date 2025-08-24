# Authentication API Documentation

## Base URL

`/auth/`

---

## Endpoints

### 1. Register User

- **URL:** `/auth/register/`
- **Method:** `POST`
- **Description:** Create a new user account and return JWT tokens.
- **Authentication:** Not required
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```
- **Response:**
  - `200 OK`: User created successfully with tokens.
  - `400 Bad Request`: Validation errors.

#### Example Response

```json
{
  "success": true,
  "user_id": "uuid-string",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

#### Example Error Response

```json
{
  "success": false,
  "error": "A user with that email already exists."
}
```

---

### 2. Login User

- **URL:** `/auth/login/`
- **Method:** `POST`
- **Description:** Authenticate existing user and return JWT tokens.
- **Authentication:** Not required
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```
- **Response:**
  - `200 OK`: Authentication successful with tokens.
  - `400 Bad Request`: Invalid credentials or validation errors.

#### Example Response

```json
{
  "success": true,
  "user_id": "uuid-string",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

#### Example Error Response

```json
{
  "success": false,
  "error": "No active account found with the given credentials."
}
```

---

### 3. Forgot Password

- **URL:** `/auth/forgot-password/`
- **Method:** `POST`
- **Description:** Initiate password reset process by sending a reset email.
- **Authentication:** Not required
- **Request Body:**
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response:**
  - `200 OK`: Password reset email sent (or message indicating no account found).
  - `400 Bad Request`: Invalid email format.

#### Example Response

```json
{
  "success": true,
  "message": "If an account exists, a password reset email will be sent"
}
```

#### Example Error Response

```json
{
  "success": false,
  "error": "Invalid email format"
}
```

---

### 4. Reset Password

- **URL:** `/auth/reset-password/`
- **Method:** `POST`
- **Description:** Complete password reset using the token from the reset email.
- **Authentication:** Not required
- **Request Body:**
  ```json
  {
    "token": "reset-token-from-email",
    "password": "newsecurepassword123"
  }
  ```
- **Response:**
  - `200 OK`: Password updated successfully.
  - `400 Bad Request`: Invalid token, expired token, or missing fields.

#### Example Response

```json
{
  "success": true,
  "message": "Password updated successfully"
}
```

#### Example Error Response

```json
{
  "success": false,
  "error": "Invalid or expired verification token"
}
```

---

## Field Reference

For detailed field information on models used in these endpoints, see:

- **[User Fields](../models/user.md)** - User model fields and structure

---

## Notes

- All endpoints return responses with a `success` boolean field indicating operation status.
- JWT tokens are returned for successful authentication operations.
- Password reset tokens have expiration times for security.
- Email verification is handled through the password reset flow.
- Error messages are user-friendly and don't reveal sensitive information.
- The system uses atomic transactions for user creation to ensure data consistency.
