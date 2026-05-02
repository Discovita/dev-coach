import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useProfile } from "@/hooks/use-profile";
import { createQueryWrapper } from "@/tests/query-wrapper";
import type { User } from "@/types/user";

vi.mock("@/api/user", () => ({
  fetchUserProfile: vi.fn(),
}));

import { fetchUserProfile } from "@/api/user";

const adminUser: User = {
  id: "user-1",
  email: "admin@test.com",
  is_staff: true,
  is_superuser: false,
  created_at: "2025-01-01",
  updated_at: "2025-01-01",
};

const regularUser: User = {
  id: "user-2",
  email: "user@test.com",
  is_staff: false,
  is_superuser: false,
  created_at: "2025-01-01",
  updated_at: "2025-01-01",
};

describe("useProfile", () => {
  beforeEach(() => {
    vi.mocked(fetchUserProfile).mockReset();
  });

  it("fetches and returns user profile", async () => {
    vi.mocked(fetchUserProfile).mockResolvedValue(regularUser);
    const { wrapper } = createQueryWrapper();

    const { result } = renderHook(() => useProfile(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.profile).toEqual(regularUser);
    expect(fetchUserProfile).toHaveBeenCalledTimes(1);
  });

  it("sets isAdmin to true for staff users", async () => {
    vi.mocked(fetchUserProfile).mockResolvedValue(adminUser);
    const { wrapper } = createQueryWrapper();

    const { result } = renderHook(() => useProfile(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAdmin).toBe(true);
  });

  it("sets isAdmin to false for regular users", async () => {
    vi.mocked(fetchUserProfile).mockResolvedValue(regularUser);
    const { wrapper } = createQueryWrapper();

    const { result } = renderHook(() => useProfile(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAdmin).toBe(false);
  });

  it("sets isAdmin to undefined when no data", () => {
    vi.mocked(fetchUserProfile).mockReturnValue(new Promise(() => {}));
    const { wrapper } = createQueryWrapper();

    const { result } = renderHook(() => useProfile(), { wrapper });

    expect(result.current.isAdmin).toBeUndefined();
    expect(result.current.isLoading).toBe(true);
  });

  it("handles fetch errors", async () => {
    vi.mocked(fetchUserProfile).mockRejectedValue(new Error("Network error"));
    const { wrapper } = createQueryWrapper();

    const { result } = renderHook(() => useProfile(), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.profile).toBeUndefined();
  });
});
