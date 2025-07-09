import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { TestScenario } from "@/types/testScenario";
import TestScenarioGeneralForm from "@/pages/test/components/TestScenarioGeneralForm";
import TestScenarioUserForm from "@/pages/test/components/TestScenarioUserForm";
import TestScenarioCoachStateForm, { CoachStateFormValue } from "@/pages/test/components/TestScenarioCoachStateForm";

interface TestScenarioEditorProps {
  scenario: TestScenario | null;
  onSave: (fields: {
    name: string;
    description: string;
    user: { first_name: string; last_name: string };
    coach_state?: Record<string, unknown>;
  }) => void;
  onCancel: () => void;
  onDelete?: () => void;
}

const TestScenarioEditor = ({ scenario, onSave, onCancel, onDelete }: TestScenarioEditorProps) => {
  // General section state
  const [name, setName] = useState(
    scenario?.name || ""
  );
  const [description, setDescription] = useState(
    scenario?.description || ""
  );
  // User section state
  const [firstName, setFirstName] = useState(
    (() => {
      const user = scenario?.template && typeof scenario.template === 'object' && scenario.template !== null && 'user' in scenario.template
        ? (scenario.template as Record<string, unknown>).user
        : undefined;
      if (user && typeof user === 'object' && user !== null && 'first_name' in user) {
        const value = (user as Record<string, unknown>)["first_name"];
        return typeof value === 'string' ? value : '';
      }
      return '';
    })()
  );
  const [lastName, setLastName] = useState(
    (() => {
      const user = scenario?.template && typeof scenario.template === 'object' && scenario.template !== null && 'user' in scenario.template
        ? (scenario.template as Record<string, unknown>).user
        : undefined;
      if (user && typeof user === 'object' && user !== null && 'last_name' in user) {
        const value = (user as Record<string, unknown>)["last_name"];
        return typeof value === 'string' ? value : '';
      }
      return '';
    })()
  );
  // Coach State section state
  const [coachState, setCoachState] = useState<CoachStateFormValue>(
    (() => {
      if (scenario?.template && typeof scenario.template === 'object' && scenario.template !== null && 'coach_state' in scenario.template) {
        return (scenario.template as Record<string, unknown>).coach_state as CoachStateFormValue;
      }
      return {};
    })()
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("general");

  const handleGeneralChange = (fields: { name: string; description: string }) => {
    setName(fields.name);
    setDescription(fields.description);
  };

  const handleUserChange = (fields: { first_name: string; last_name: string }) => {
    setFirstName(fields.first_name);
    setLastName(fields.last_name);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    if (!name.trim()) {
      setError("Title is required.");
      setSaving(false);
      return;
    }
    try {
      await onSave({
        name,
        description,
        user: { first_name: firstName, last_name: lastName },
        coach_state: coachState as Record<string, unknown>,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form
      className="w-full p-6 bg-white rounded-lg shadow mb-8"
      onSubmit={handleSubmit}
    >
      <h2 className="text-2xl font-semibold mb-4">
        {scenario ? "Edit Test Scenario" : "Create New Test Scenario"}
      </h2>
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="user">User</TabsTrigger>
          <TabsTrigger value="coach_state">Coach State</TabsTrigger>
          <TabsTrigger value="identities">Identities</TabsTrigger>
          <TabsTrigger value="chat_messages">Chat Messages</TabsTrigger>
          <TabsTrigger value="user_notes">User Notes</TabsTrigger>
        </TabsList>
        <TabsContent value="general">
          <TestScenarioGeneralForm
            name={name}
            description={description}
            onChange={handleGeneralChange}
          />
        </TabsContent>
        <TabsContent value="user">
          <TestScenarioUserForm
            firstName={firstName}
            lastName={lastName}
            onChange={handleUserChange}
          />
        </TabsContent>
        <TabsContent value="coach_state">
          <TestScenarioCoachStateForm value={coachState} onChange={setCoachState} />
        </TabsContent>
        <TabsContent value="identities">
          <div className="text-neutral-500">[Identities form coming soon]</div>
        </TabsContent>
        <TabsContent value="chat_messages">
          <div className="text-neutral-500">[Chat Messages form coming soon]</div>
        </TabsContent>
        <TabsContent value="user_notes">
          <div className="text-neutral-500">[User Notes form coming soon]</div>
        </TabsContent>
      </Tabs>
      {error && <div className="text-red-600 mt-2">{error}</div>}
      <div className="flex gap-2 mt-6">
        <Button type="submit" variant="default" disabled={saving}>
          {saving ? "Saving..." : "Save"}
        </Button>
        <Button type="button" onClick={onCancel} variant="secondary" disabled={saving}>
          Cancel
        </Button>
        {scenario && onDelete && (
          <Button type="button" onClick={onDelete} variant="destructive" disabled={saving}>
            Delete
          </Button>
        )}
      </div>
    </form>
  );
};

export default TestScenarioEditor; 