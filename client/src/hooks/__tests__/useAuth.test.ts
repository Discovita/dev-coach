import { useAuth } from "@/hooks/use-auth";
import { createQueryWrapper } from "@/tests/query-wrapper";
import type { AuthResponse } from "@/types/auth";
import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/api/auth", () => ({
	login: vi.fn(),
	register: vi.fn(),
	forgotPassword: vi.fn(),
	resetPassword: vi.fn(),
	verifyEmail: vi.fn(),
	resendVerification: vi.fn(),
	logout: vi.fn(),
}));

vi.mock("@/permissions/isAdminUser", () => ({
	isAdminUser: vi.fn().mockReturnValue(false),
}));

import {
	forgotPassword as forgotPasswordApi,
	login as loginApi,
	logout as logoutApi,
	register as registerApi,
	resetPassword as resetPasswordApi,
} from "@/api/auth";

const successResponse: AuthResponse = {
	success: true,
	user_id: "user-1",
	tokens: { access: "access-token", refresh: "refresh-token" },
	user: {
		id: "user-1",
		email: "test@test.com",
		created_at: "2025-01-01",
		updated_at: "2025-01-01",
	},
};

describe("useAuth", () => {
	beforeEach(() => {
		vi.mocked(loginApi).mockReset();
		vi.mocked(registerApi).mockReset();
		vi.mocked(forgotPasswordApi).mockReset();
		vi.mocked(resetPasswordApi).mockReset();
		vi.mocked(logoutApi).mockReset();
	});

	it("provides login function that calls loginApi", async () => {
		vi.mocked(loginApi).mockResolvedValue(successResponse);
		const { wrapper } = createQueryWrapper();

		const { result } = renderHook(() => useAuth(), { wrapper });

		await act(async () => {
			const response = await result.current.login({
				email: "test@test.com",
				password: "password",
			});
			expect(response).toEqual(successResponse);
		});

		expect(loginApi).toHaveBeenCalledWith(
			{ email: "test@test.com", password: "password" },
			expect.anything(),
		);
	});

	it("caches user data after successful login", async () => {
		vi.mocked(loginApi).mockResolvedValue(successResponse);
		const { wrapper, queryClient } = createQueryWrapper();

		const { result } = renderHook(() => useAuth(), { wrapper });

		await act(async () => {
			await result.current.login({ email: "test@test.com", password: "pass" });
		});

		await waitFor(() => {
			expect(queryClient.getQueryData(["user", "profile"])).toMatchObject({
				id: "user-1",
				email: "test@test.com",
			});
		});
		expect(queryClient.getQueryData(["user", "complete"])).toBeDefined();
	});

	it("provides register function that calls registerApi", async () => {
		vi.mocked(registerApi).mockResolvedValue(successResponse);
		const { wrapper } = createQueryWrapper();

		const { result } = renderHook(() => useAuth(), { wrapper });

		await act(async () => {
			const response = await result.current.register({
				email: "new@test.com",
				password: "password",
			});
			expect(response).toEqual(successResponse);
		});

		expect(registerApi).toHaveBeenCalledWith(
			{ email: "new@test.com", password: "password" },
			expect.anything(),
		);
	});

	it("provides forgotPassword function", async () => {
		const forgotResponse: AuthResponse = { success: true, email_sent: true };
		vi.mocked(forgotPasswordApi).mockResolvedValue(forgotResponse);
		const { wrapper } = createQueryWrapper();

		const { result } = renderHook(() => useAuth(), { wrapper });

		await act(async () => {
			const response = await result.current.forgotPassword("user@test.com");
			expect(response.email_sent).toBe(true);
		});

		expect(forgotPasswordApi).toHaveBeenCalledWith(
			"user@test.com",
			expect.anything(),
		);
	});

	it("provides resetPassword function", async () => {
		const resetResponse: AuthResponse = { success: true };
		vi.mocked(resetPasswordApi).mockResolvedValue(resetResponse);
		const { wrapper } = createQueryWrapper();

		const { result } = renderHook(() => useAuth(), { wrapper });

		await act(async () => {
			const response = await result.current.resetPassword({
				token: "reset-token",
				password: "newpass",
			});
			expect(response.success).toBe(true);
		});

		expect(resetPasswordApi).toHaveBeenCalledWith(
			{ token: "reset-token", password: "newpass" },
			expect.anything(),
		);
	});

	it("provides logout function that calls logoutApi", async () => {
		vi.mocked(logoutApi).mockResolvedValue();
		Object.defineProperty(window, "location", {
			writable: true,
			value: { href: "/chat" },
		});
		const { wrapper } = createQueryWrapper();

		const { result } = renderHook(() => useAuth(), { wrapper });

		await act(async () => {
			await result.current.logout();
		});

		expect(logoutApi).toHaveBeenCalled();
	});

	it("does not cache user data when response has no user", async () => {
		const noUserResponse: AuthResponse = {
			success: false,
			error: "Bad credentials",
		};
		vi.mocked(loginApi).mockResolvedValue(noUserResponse);
		const { wrapper, queryClient } = createQueryWrapper();

		const { result } = renderHook(() => useAuth(), { wrapper });

		await act(async () => {
			await result.current.login({ email: "test@test.com", password: "wrong" });
		});

		expect(queryClient.getQueryData(["user", "profile"])).toBeUndefined();
	});
});
