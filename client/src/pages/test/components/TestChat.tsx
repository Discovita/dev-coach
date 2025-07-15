import React from "react";
import { CoachStateVisualizer } from "@/pages/test/components/coach-state-visualizer/CoachStateVisualizer";
import { Button } from "@/components/ui/button";
import { TestScenario } from "@/types/testScenario";
import { TestScenarioChatInterface } from "@/pages/test/components/TestScenarioChatInterface";

interface TestChatProps {
  scenario: TestScenario;
  setHasStarted: (value: boolean) => void;
}

const TestChat: React.FC<TestChatProps> = ({
  scenario,
  setHasStarted,
}) => {
  // Get the test user id from the scenario (use id for API calls)
  const testUserId = scenario.template.user?.id;
  if (!testUserId) {
    return <div className="flex-1 flex items-center justify-center text-red-500">No test user id found in scenario.</div>;
  }

  return (
    <div className="relative z-10 flex flex-col h-full _TestChat">
      <div className="sticky top-0 left-0 w-full flex justify-between items-center px-5 py-3 shadow-gold-sm z-50 border-b-2 border-primary-color h-[62px]">
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
      <div className="flex flex-col xl:flex-row items-start flex-1 min-h-0">
        <div className="flex flex-col w-full xl:flex-1 min-w-0 overflow-hidden h-full min-h-0 xl:mr-4">
          {/* Render the test scenario chat interface for the test user */}
          <TestScenarioChatInterface userId={String(testUserId)} />
        </div>
        <div className="w-full xl:w-2/5 min-w-0 xl:min-w-[600px] border-t xl:border-t-0 xl:border-l border-border-color overflow-hidden h-full min-h-0">
          <CoachStateVisualizer />
        </div>
      </div>
    </div>
  );
};

export default TestChat;
