import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { TestState } from "@/tests/testStates";

interface TestStateSelectorProps {
  selectedState: string;
  setSelectedState: (value: string) => void;
  setHasStarted: (value: boolean) => void;
  testStates: Record<string, TestState>;
}

const TestStateSelector: React.FC<TestStateSelectorProps> = ({
  selectedState,
  setSelectedState,
  setHasStarted,
  testStates,
}) => {
  return (
    <div className="_TestStateSelector">
      <Card className="w-full p-8 mt-10">
        <CardHeader>
          <CardTitle className="text-2xl mb-2">Test State Selection</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gold-900 mb-6">
            Select a test state to simulate different chat scenarios
          </p>
          <form className="flex flex-col gap-4">
            <div className="flex flex-col md:flex-row md:items-center gap-4">
              <Label htmlFor="test-state-select" className="min-w-[120px]">
                Test State
              </Label>
              <Select value={selectedState} onValueChange={setSelectedState}>
                <SelectTrigger
                  id="test-state-select"
                  className="min-w-[200px]"
                  aria-label="Select a test state"
                >
                  <SelectValue placeholder="Select a test state" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(testStates).map(([key, state]) => (
                    <SelectItem key={key} value={key}>
                      {state.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                type="button"
                onClick={() => setHasStarted(true)}
                disabled={!selectedState}
                className="ml-0 md:ml-2"
              >
                Start Test
              </Button>
            </div>
          </form>
          {selectedState && (
            <div className="mt-8 bg-gold-50 border border-gold-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gold-700 mb-2">
                Selected State Details:
              </h3>
              <div className="space-y-1 text-gold-900">
                <p>
                  <span className="font-semibold">Name:</span>{" "}
                  {testStates[selectedState].name}
                </p>
                <p>
                  <span className="font-semibold">Description:</span>{" "}
                  {testStates[selectedState].description}
                </p>
                <p>
                  <span className="font-semibold">Current State:</span>{" "}
                  {testStates[selectedState].coach_state.current_state}
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default TestStateSelector;
