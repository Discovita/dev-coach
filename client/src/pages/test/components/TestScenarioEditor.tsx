import { Button } from "@/components/ui/button";
import { TestScenario } from "@/types/testScenario";

interface TestScenarioEditorProps {
  scenario: TestScenario | null;
  onSave: () => void;
  onCancel: () => void;
}

const TestScenarioEditor = ({ scenario, onSave, onCancel }: TestScenarioEditorProps) => {
  return (
    <div className="w-full p-6 bg-white rounded-lg shadow mb-8">
      <h2 className="text-2xl font-semibold mb-4">
        {scenario ? "Edit Test Scenario" : "Create New Test Scenario"}
      </h2>
      {/* Form fields for user, coach state, identities, chat messages, user notes go here */}
      <div className="text-neutral-500">
        [TestScenarioEditor form coming soon]
      </div>
      <div className="flex gap-2 mt-4">
        <Button onClick={onSave} variant="default">
          Save
        </Button>
        <Button onClick={onCancel} variant="secondary">
          Cancel
        </Button>
      </div>
    </div>
  );
};

export default TestScenarioEditor; 