import React from "react";
import { ChatInterface } from "@/pages/chat/components/ChatInterface";
import { CoachStateVisualizer } from "@/pages/test/components/coach-state-visualizer/CoachStateVisualizer";
import { Button } from "@/components/ui/button";
import { TestState } from "@/tests/testStates";

interface TestChatProps {
  selectedState: string;
  setHasStarted: (value: boolean) => void;
  testStates: Record<string, TestState>;
}

const TestChat: React.FC<TestChatProps> = ({
  selectedState,
  setHasStarted,
  testStates,
}) => {
  return (
    <div className="relative z-10 flex flex-col h-full _TestChat">
      <div className="sticky top-0 left-0 w-full flex justify-between items-center px-5 py-3 shadow-gold-sm z-50 border-b-2 border-primary-color h-[62px]">
        <h2 className="text-[1.2rem] font-semibold m-0">
          Test Mode: {testStates[selectedState].name}
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
          <ChatInterface />
        </div>
        <div className="w-full xl:w-2/5 min-w-0 xl:min-w-[600px] border-t xl:border-t-0 xl:border-l border-border-color overflow-hidden h-full min-h-0">
          <CoachStateVisualizer />
        </div>
      </div>
    </div>
  );
};

export default TestChat;
