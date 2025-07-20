import React from "react";
import { CoachStateVisualizer } from "@/pages/test/components/coach-state-visualizer/CoachStateVisualizer";
import { TestScenarioCoachStateVisualizer } from "@/pages/test/components/coach-state-visualizer/TestScenarioCoachStateVisualizer";
import { Button } from "@/components/ui/button";
import { TestScenario } from "@/types/testScenario";
import { TestScenarioChatInterface } from "@/pages/test/components/TestScenarioChatInterface";
import { ChatInterface } from "@/pages/chat/components/ChatInterface";
import { toast } from "sonner";

interface TestChatProps {
  scenario: TestScenario;
  setHasStarted: (value: boolean) => void;
  testUserId?: string;
}

const TestChat: React.FC<TestChatProps> = ({
  scenario,
  setHasStarted,
  testUserId,
}) => {
  console.log("[TestChat] testUserId", testUserId);

  if (testUserId) {
    // Test scenario mode
    return (
      <div className="_TestChat relative z-10 flex flex-col h-full">
        <div className="_TestChatHeader sticky top-0 left-0 w-full flex justify-between items-center px-5 py-3 shadow-gold-sm z-50 border-b-2 border-primary-color h-[62px]">
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
            <TestScenarioChatInterface
              userId={String(testUserId)}
              scenarioId={scenario.id}
              onResetSuccess={() => {
                toast.success("Test scenario reset successfully!");
                setHasStarted(false); // Navigate back to /test page
              }}
            />
          </div>
          <div className="_TestChatCoachStateVisualizerContainer w-full xl:w-2/5 min-w-0 xl:min-w-[600px] border-t xl:border-t-0 xl:border-l border-border-color overflow-hidden h-full min-h-0">
            <TestScenarioCoachStateVisualizer
              testUserId={testUserId}
              key={`test-${testUserId}`}
            />
          </div>
        </div>
      </div>
    );
  }

  // Admin/authenticated user mode
  return (
    <div className="_TestChat relative z-10 flex flex-col h-full">
      <div className="_TestChatHeader sticky top-0 left-0 w-full flex justify-between items-center px-5 py-3 shadow-gold-sm z-50 border-b-2 border-primary-color h-[62px]">
        <h2 className="text-[1.2rem] font-semibold m-0">
          Test Mode: {scenario.name}
        </h2>
        <div className="flex gap-2 items-center">
          <Button
            variant="default"
            size="sm"
            onClick={() => setHasStarted(false)}
          >
            Back to Test Selection
          </Button>
        </div>
      </div>
      <div className="_TestChatContent flex flex-col xl:flex-row items-start flex-1 min-h-0">
        <div className="_ChatInterfaceContainer flex flex-col w-full xl:flex-1 min-w-0 overflow-hidden h-full min-h-0 xl:mr-4">
          <ChatInterface />
        </div>
        <div className="_ChatCoachStateVisualizerContainer w-full xl:w-2/5 min-w-0 xl:min-w-[600px] border-t xl:border-t-0 xl:border-l border-border-color overflow-hidden h-full min-h-0">
          <CoachStateVisualizer key="admin" />
        </div>
      </div>
    </div>
  );
};

export default TestChat;
