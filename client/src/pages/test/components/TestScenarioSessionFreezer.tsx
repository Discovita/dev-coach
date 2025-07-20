import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { useFreezeTestScenarioSession } from "@/hooks/test-scenario/use-freeze-test-scenario-session";
import { toast } from "sonner";
import { TestScenario } from "@/types/testScenario";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { useQueryClient } from "@tanstack/react-query";

/**
 * TestScenarioSessionFreezer
 * Button + modal to freeze the current session as a test scenario.
 *
 * Uses shadcn/ui Dialog for modal.
 *
 * Props:
 *   userId: string (required)
 *   onSuccess?: (scenario: TestScenario) => void (optional)
 */
export const TestScenarioSessionFreezer: React.FC<{
  userId: string;
  onSuccess?: (scenario: TestScenario) => void;
}> = ({ userId, onSuccess }) => {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const { mutateAsync, isPending, error } = useFreezeTestScenarioSession();
  const queryClient = useQueryClient();

  // Type guard for API error shape
  function getErrorMessage(err: unknown): string {
    if (typeof err === "string") return err;
    if (err && typeof err === "object") {
      const e = err as { detail?: string; errors?: { error: string }[] };
      if (e.detail) return e.detail;
      if (e.errors && Array.isArray(e.errors)) {
        return e.errors.map((er) => er.error).join(", ");
      }
    }
    return "Failed to create test scenario";
  }

  // Handler for form submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Use defaults if fields are blank
    const safeFirstName = firstName.trim() || "Test";
    const safeLastName = lastName.trim() || "User";
    if (!name.trim()) {
      toast.error("Scenario name is required");
      return;
    }
    try {
      const scenario = await mutateAsync({
        user_id: userId,
        name,
        description,
        first_name: safeFirstName,
        last_name: safeLastName,
      });
      toast.success("Test scenario created from session!");
      setOpen(false);
      setName("");
      setDescription("");
      setFirstName("");
      setLastName("");
      // Invalidate test scenarios query so the table updates
      queryClient.invalidateQueries({ queryKey: ["testScenarios"] });
      if (onSuccess) onSuccess(scenario);
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button disabled={isPending}>
          Create Test Scenario from Current Session
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Freeze Current Session</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 mt-2">
          <div>
            <Label htmlFor="scenario_name">Scenario Name</Label>
            <Input
              id="scenario_name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="Unique scenario name"
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="scenario_description">Description</Label>
            <Input
              id="scenario_description"
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe this scenario (optional)"
              className="mt-1"
            />
          </div>
          <div className="flex gap-2">
            <div className="flex-1">
              <Label htmlFor="first_name">First Name</Label>
              <Input
                id="first_name"
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                placeholder="Test"
                required
                className="mt-1"
              />
            </div>
            <div className="flex-1">
              <Label htmlFor="last_name">Last Name</Label>
              <Input
                id="last_name"
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                placeholder="User"
                required
                className="mt-1"
              />
            </div>
          </div>
          {/* Optionally show userId as email if present and looks like an email */}
          {userId && userId.includes("@") && (
            <div>
              <Label htmlFor="test_user_email">Test User Email</Label>
              <Input
                id="test_user_email"
                type="text"
                value={userId}
                readOnly
                className="mt-1 bg-neutral-100 cursor-not-allowed"
              />
            </div>
          )}
          {error && (
            <div className="text-red-600 text-sm">{getErrorMessage(error)}</div>
          )}
          <DialogFooter className="flex gap-2 mt-4">
            <Button type="submit" disabled={isPending}>
              {isPending ? "Freezing..." : "Freeze Session"}
            </Button>
            <DialogClose asChild>
              <Button type="button" variant="secondary" disabled={isPending}>
                Cancel
              </Button>
            </DialogClose>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
