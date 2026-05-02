import React from "react";
import { CoachStateVisualizer } from "@/pages/test/components/coach-state-visualizer/CoachStateVisualizer";
import { Button } from "@/components/ui/button";
import type { TestScenario } from "@/types/testScenario";
import { ChatInterface } from "@/pages/chat/components/ChatInterface";
import { UserTargetProvider } from "@/providers/UserTargetProvider";
import { toast } from "sonner";

interface TestChatProps {
  scenario: TestScenario;
  setHasStarted: (value: boolean) => void;
  testUserId?: string;
}

/**
 * TestChat component
 * Wraps the shared ChatInterface and CoachStateVisualizer in a
 * UserTargetProvider so all hooks inside automatically switch to
 * admin/test-user endpoints when a testUserId is present.
 *
 * When testUserId is undefined, the provider defaults to the
 * logged-in user (admin testing as themselves).
 */
const TestChat: React.FC<TestChatProps> = ({
  scenario,
  setHasStarted,
  testUserId,
}) => {
  return (
    <UserTargetProvider targetUserId={testUserId} scenarioId={scenario.id}>
      <div className="_TestChat relative z-10 flex flex-col h-full">
        <div className="_TestChatHeader sticky top-0 left-0 w-full flex justify-between items-center px-5 py-3 shadow-sm z-50 border-b-2 border-border h-[62px]">
          <h2 className="text-[1.2rem] font-semibold m-0">
            Test Mode: {scenario.name}
          </h2>
          <Button
            variant="default"
            size="sm"
            onClick={() => setHasStarted(false)}
          >
            Back to Test Selection
          </Button>
        </div>
        <div className="_TestChatContent flex flex-col xl:flex-row items-start flex-1 min-h-0">
          <div className="_TestChatInterfaceContainer flex flex-col w-full xl:flex-1 min-w-0 overflow-hidden h-full min-h-0 xl:mr-4">
            <ChatInterface
              onResetSuccess={() => {
                toast.success("Test scenario reset successfully!");
                setHasStarted(false);
              }}
            />
          </div>
          <div className="_TestChatCoachStateVisualizerContainer w-full xl:w-2/5 min-w-0 xl:min-w-[600px] border-t xl:border-t-0 xl:border-l border-border overflow-hidden h-full min-h-0">
            <CoachStateVisualizer
              key={testUserId ? `test-${testUserId}` : "admin"}
            />
          </div>
        </div>
      </div>
    </UserTargetProvider>
  );
};

export default TestChat;
