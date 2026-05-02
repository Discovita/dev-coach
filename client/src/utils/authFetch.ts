import { COACH_BASE_URL, REFRESH } from "@/constants/api";
import type { RequestOptions } from "@/types/auth";
import { getCookie, setCookie } from "@/api/auth";
import { createLogger, LogLevel } from "@/lib/logger";

const log = createLogger("authFetch", LogLevel.DEBUG);

let refreshPromise: Promise<string> | null = null;

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
  let accessToken = getCookie("neovita-access-token");
  const refreshToken = getCookie("neovita-refresh-token");

  // Set default headers if not provided
  options.headers = options.headers || {};
  // Don't set Content-Type for FormData - browser will set it with boundary
  if (!(options.body instanceof FormData)) {
    options.headers["Content-Type"] =
      options.headers["Content-Type"] || "application/json";
  }

  // Include the access token in the Authorization header
  if (accessToken) {
    options.headers["Authorization"] = `Bearer ${accessToken}`;
  }

  // Helper function to refresh the access token
  const refreshAccessToken = async () => {
    log.debug("Refreshing access token");
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
            setCookie("neovita-access-token", data.access);
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

  log.debug("Making request to:", url);
  let response = await fetch(url, options);

  // If access token has expired, refresh it and retry the request
  if (response.status === 401 && refreshToken) {
    try {
      accessToken = await refreshAccessToken();
      // Update the Authorization header with the new access token
      options.headers["Authorization"] = `Bearer ${accessToken}`;
      // Retry the original request
      log.debug("Retrying request to:", url);
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
