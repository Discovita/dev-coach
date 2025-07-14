import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { TestScenarioUser } from "@/types/testScenario";

interface TestScenarioUserFormProps {
  firstName: string;
  lastName: string;
  onChange: (fields: Pick<TestScenarioUser, "first_name" | "last_name">) => void;
  email?: string;
  password?: string;
}

const TestScenarioUserForm = ({
  firstName,
  lastName,
  onChange,
  email,
  password,
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
      {email && (
        <div>
          <Label htmlFor="test_user_email">Test User Email</Label>
          <Input
            id="test_user_email"
            type="text"
            value={email}
            readOnly
            className="mt-1 bg-neutral-100 cursor-not-allowed"
          />
        </div>
      )}
      {password && (
        <div>
          <Label htmlFor="test_user_password">Test User Password</Label>
          <Input
            id="test_user_password"
            type="text"
            value={password}
            readOnly
            className="mt-1 bg-neutral-100 cursor-not-allowed"
          />
        </div>
      )}
    </div>
  );
};

export default TestScenarioUserForm;
