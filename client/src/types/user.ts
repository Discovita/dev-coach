/**
 * User Interface
 * Represents a user in the system, matching the backend User model (users/models.py)
 * and the fields exposed by UserSerializer (users/serializer.py).
 * Used in: AuthContext.ts, UserProfile.tsx, Header.tsx, AboutMe.tsx
 */
export interface User {
  /**
   * Unique user ID (primary key)
   * Backend: users/models.py > User.id
   */
  id: string;
  /**
   * User's email address (primary identifier)
   * Backend: users/models.py > User.email
   */
  email: string;
  /**
   * User's first name
   * Backend: users/models.py > User.first_name
   */
  first_name?: string;
  /**
   * User's last name
   * Backend: users/models.py > User.last_name
   */
  last_name?: string;
  /**
   * Whether the user is active
   * Backend: users/models.py > User.is_active
   */
  is_active?: boolean;
  /**
   * Whether the user is a superuser (Django superuser)
   * Backend: users/models.py > User.is_superuser
   */
  is_superuser?: boolean;
  /**
   * Whether the user can access the admin page
   * Backend: users/models.py > User.is_staff
   */
  is_staff?: boolean;
  /**
   * Whether the user is an admin
   * Backend: users/models.py > User.is_admin
   */
  is_admin: boolean;
  /**
   * Token for email verification
   * Backend: users/models.py > User.verification_token
   */
  verification_token?: string;
  /**
   * When the last verification email was sent
   * Backend: users/models.py > User.email_verification_sent_at
   */
  email_verification_sent_at?: string | null;
  /**
   * Last login timestamp
   * Backend: users/models.py > User.last_login
   */
  last_login?: string | null;
  /**
   * Date the user joined
   * Backend: users/models.py > User.date_joined
   */
  date_joined?: string;
  /**
   * Timestamp when the user was created
   * Backend: users/models.py > User.created_at
   */
  created_at: string;
  /**
   * Timestamp when the user was last updated
   * Backend: users/models.py > User.updated_at
   */
  updated_at: string;
  /**
   * User's group memberships (Django groups)
   * Backend: users/models.py > User.groups
   * Not typically exposed to frontend, but included for completeness
   */
  groups?: number[];
  /**
   * User's permissions (Django permissions)
   * Backend: users/models.py > User.user_permissions
   * Not typically exposed to frontend, but included for completeness
   */
  user_permissions?: number[];
}
