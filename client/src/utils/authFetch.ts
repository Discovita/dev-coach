import { COACH_BASE_URL, REFRESH } from "@/constants/api";
import { RequestOptions } from "@/types/auth";

let refreshPromise: Promise<string> | null = null;

// Helper function to get cookies
const getCookie = (name: string) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(";").shift();
  return null;
};

// Helper function to set cookies
const setCookie = (
  name: string,
  value: string,
  maxAge: number = 60 * 60 * 24
) => {
  const cookieOptions = [
    `${name}=${value}`,
    "path=/",
    `max-age=${maxAge}`,
    "SameSite=Lax",
  ];

  if (process.env.NEXT_PUBLIC_ENV === "production") {
    cookieOptions.push("secure");
    cookieOptions.push("domain=.incept.school");
  }

  document.cookie = cookieOptions.join("; ");
};

/**
All these fire at once
```ts
const request1 = authFetch('/api/courses')  // Gets 401, starts refresh
const request2 = authFetch('/api/profile')  // Gets 401, sees refresh in progress, waits
const request3 = authFetch('/api/settings') // Gets 401, sees refresh in progress, waits
```

What happens:
1. request1 creates refreshPromise and starts refresh
2. request2 and request3 see refreshPromise exists
3. All three wait for the same refresh to complete
4. All three get the same new token
5. All three retry their original requests with the new token
*/
export const authFetch = async (
  url: string,
  options: RequestOptions = {},
  onLogout?: () => void
): Promise<Response> => {
  // Get tokens from cookies
  let accessToken = getCookie("discovita-access-token");
  const refreshToken = getCookie("discovita-refresh-token");

  // Set default headers if not provided
  options.headers = options.headers || {};
  options.headers["Content-Type"] =
    options.headers["Content-Type"] || "application/json";

  // Include the access token in the Authorization header
  if (accessToken) {
    options.headers["Authorization"] = `Bearer ${accessToken}`;
  }

  // Helper function to refresh the access token
  const refreshAccessToken = async () => {
    if (refreshPromise) {
      return refreshPromise;
    }

    // Create a new refresh promise and store it
    refreshPromise = (async () => {
      try {
        const response = await fetch(`${COACH_BASE_URL}${REFRESH}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh: refreshToken }),
        });

        if (response.ok) {
          const data = await response.json();
          if (data.access) {
            setCookie("discovita-access-token", data.access);
            return data.access;
          }
          throw new Error("Access token is missing in the response.");
        }
        throw new Error("Refresh token expired or invalid.");
      } finally {
        // Clear the promise so future refreshes can happen
        refreshPromise = null;
      }
    })();

    return refreshPromise;
  };

  // Make the initial request
  console.log("[authFetch] Making request to:", url);
  let response = await fetch(url, options);

  // If access token has expired, refresh it and retry the request
  if (response.status === 401 && refreshToken) {
    try {
      accessToken = await refreshAccessToken();
      // Update the Authorization header with the new access token
      options.headers["Authorization"] = `Bearer ${accessToken}`;
      // Retry the original request
      console.log("[authFetch] Retrying request to:", url);
      response = await fetch(url, options);
    } catch (error) {
      // If refreshing the token fails, call onLogout if provided
      if (onLogout) {
        onLogout(); // Log out the user
      }
      throw error;
    }
  }

  // If the response is still unauthorized, call onLogout if provided
  if (response.status === 401) {
    if (onLogout) {
      onLogout();
    }
    throw new Error("Unauthorized. Please log in.");
  }

  return response;
};
