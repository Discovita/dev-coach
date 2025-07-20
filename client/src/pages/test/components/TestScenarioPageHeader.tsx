import { Button } from "@/components/ui/button";

interface TestScenarioPageHeaderProps {
  onCreate: () => void;
}

const TestScenarioPageHeader = ({ onCreate }: TestScenarioPageHeaderProps) => (
  <div className="_TestScenarioPageHeader flex justify-between items-center mb-4">
    <h1 className="text-2xl font-bold">Test Scenarios</h1>
    <Button variant="default" onClick={onCreate}>
      + New Scenario
    </Button>
  </div>
);

export default TestScenarioPageHeader; 