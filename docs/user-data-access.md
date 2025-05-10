# Accessing User Data in Components

This document explains how to access user data in your app using the new modular hooks and TanStack Query. With the new structure, each piece of user data is available via its own hook or query key, making your components clean, modular, and type-safe.

---

## Accessing User Data

### User Profile
```tsx
import { useQuery } from "@tanstack/react-query";

export function UserProfileComponent() {
  // Access the user profile from the cache (populated after login/register)
  const { data: profile, isLoading, isError } = useQuery({
    queryKey: ["user", "profile"],
    enabled: true, // always enabled after login
  });

  if (isLoading) return <div>Loading profile...</div>;
  if (isError || !profile) return <div>Error loading profile.</div>;

  return (
    <div>
      <h2>Welcome, {profile.first_name} {profile.last_name}</h2>
      <p>Email: {profile.email}</p>
      {/* ...other profile fields... */}
    </div>
  );
}
```

### Coach State
```tsx
import { useCoachState } from "@/hooks/use-coach-state";

export function CoachStateComponent() {
  const { coachState, isLoading, isError } = useCoachState();

  if (isLoading) return <div>Loading coach state...</div>;
  if (isError || !coachState) return <div>Error loading coach state.</div>;

  return (
    <div>
      <h3>Current State: {coachState.current_state}</h3>
      {/* ...other coach state fields... */}
    </div>
  );
}
```

### Identities
```tsx
import { useIdentities } from "@/hooks/use-identities";

export function IdentitiesComponent() {
  const { identities, isLoading, isError } = useIdentities();

  if (isLoading) return <div>Loading identities...</div>;
  if (isError || !identities) return <div>Error loading identities.</div>;

  return (
    <ul>
      {identities.map(identity => (
        <li key={identity.id}>{identity.description}</li>
      ))}
    </ul>
  );
}
```

### Chat Messages
```tsx
import { useChatMessages } from "@/hooks/use-chat-messages";

export function ChatMessagesComponent() {
  const { chatMessages, isLoading, isError } = useChatMessages();

  if (isLoading) return <div>Loading chat messages...</div>;
  if (isError || !chatMessages) return <div>Error loading chat messages.</div>;

  return (
    <div>
      {chatMessages.map(msg => (
        <div key={msg.timestamp}>
          <b>{msg.role}:</b> {msg.content}
        </div>
      ))}
    </div>
  );
}
```

---

## Summary Table

| Data Needed      | Hook/Query to Use         | Example Query Key         |
|------------------|--------------------------|--------------------------|
| User Profile     | `useQuery` (profile)      | `["user", "profile"]`    |
| Coach State      | `useCoachState`           | `["user", "coachState"]` |
| Identities       | `useIdentities`           | `["user", "identities"]` |
| Chat Messages    | `useChatMessages`         | `["user", "chatMessages"]`|

---

## Best Practices

- **Use the modular hook for each resource** in the component that needs it.
- **No need to pass user data down through props**—just call the hook where you need the data.
- **TanStack Query will keep everything in sync and up-to-date.**
- If you need the complete user object, use:
  ```tsx
  import { useQuery } from "@tanstack/react-query";
  const { data: user } = useQuery({ queryKey: ["user", "complete"], enabled: true });
  ```

---

For more details, see the individual hook files in `client/src/hooks/`. 