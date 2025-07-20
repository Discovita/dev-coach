import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface TestScenarioGeneralFormProps {
  name: string;
  description: string;
  onChange: (fields: { name: string; description: string }) => void;
}

const TestScenarioGeneralForm = ({ name, description, onChange }: TestScenarioGeneralFormProps) => {
  return (
    <div className="flex flex-col gap-4 mt-4">
      <div>
        <Label htmlFor="scenario_name">Title</Label>
        <Input
          id="scenario_name"
          type="text"
          value={name}
          onChange={e => onChange({ name: e.target.value, description })}
          required
          className="mt-1"
        />
      </div>
      <div>
        <Label htmlFor="scenario_description">Description</Label>
        <Textarea
          id="scenario_description"
          value={description}
          onChange={e => onChange({ name, description: e.target.value })}
          className="mt-1"
        />
      </div>
    </div>
  );
};

export default TestScenarioGeneralForm; 