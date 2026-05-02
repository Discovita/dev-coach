import { describe, it, expect } from "vitest";
import { renderHook } from "@testing-library/react";
import { useUserTarget, UserTargetContext } from "@/context/UserTargetContext";
import type { UserTargetContextValue } from "@/context/UserTargetContext";
import type { ReactNode } from "react";

describe("useUserTarget", () => {
  it("returns default non-impersonating value outside a provider", () => {
    const { result } = renderHook(() => useUserTarget());

    expect(result.current.isImpersonating).toBe(false);
    expect(result.current.targetUserId).toBeNull();
    expect(result.current.scenarioId).toBeNull();
    expect(result.current.queryKeyPrefix).toEqual(["user"]);
  });

  it("returns provided context value inside a provider", () => {
    const contextValue: UserTargetContextValue = {
      isImpersonating: true,
      targetUserId: "user-abc",
      scenarioId: "scenario-xyz",
      queryKeyPrefix: ["testScenarioUser", "user-abc"],
    };

    function Wrapper({ children }: { children: ReactNode }) {
      return (
        <UserTargetContext.Provider value={contextValue}>
          {children}
        </UserTargetContext.Provider>
      );
    }

    const { result } = renderHook(() => useUserTarget(), { wrapper: Wrapper });

    expect(result.current.isImpersonating).toBe(true);
    expect(result.current.targetUserId).toBe("user-abc");
    expect(result.current.scenarioId).toBe("scenario-xyz");
    expect(result.current.queryKeyPrefix).toEqual(["testScenarioUser", "user-abc"]);
  });
});
