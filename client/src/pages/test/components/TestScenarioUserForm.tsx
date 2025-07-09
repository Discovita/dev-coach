import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface TestScenarioUserFormProps {
  firstName: string;
  lastName: string;
  onChange: (fields: { first_name: string; last_name: string }) => void;
}

const TestScenarioUserForm = ({
  firstName,
  lastName,
  onChange,
}: TestScenarioUserFormProps) => {
  return (
    <div className="flex flex-col gap-4 mt-4">
      <div className="mb-2 text-neutral-500 text-sm">
        Email and password are backend-controlled and not editable.
      </div>
      <div>
        <Label htmlFor="first_name">First Name</Label>
        <Input
          id="first_name"
          type="text"
          value={firstName}
          onChange={(e) =>
            onChange({ first_name: e.target.value, last_name: lastName })
          }
          required
          className="mt-1"
        />
      </div>
      <div>
        <Label htmlFor="last_name">Last Name</Label>
        <Input
          id="last_name"
          type="text"
          value={lastName}
          onChange={(e) =>
            onChange({ first_name: firstName, last_name: e.target.value })
          }
          required
          className="mt-1"
        />
      </div>
    </div>
  );
};

export default TestScenarioUserForm;
