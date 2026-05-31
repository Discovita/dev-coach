import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import type {
  TestScenario,
  TestScenarioTemplate,
  TestScenarioUser,
  TestScenarioCoachState,
  TestScenarioIdentity,
  TestScenarioChatMessage,
  TestScenarioUserNote,
  TestScenarioAction,
  TestScenarioBreak,
} from "@/types/testScenario";
import { CoachingPhase } from "@/enums/coachingPhase";
import { IdentityCategory } from "@/enums/identityCategory";
import TestScenarioGeneralForm from "@/pages/test/components/TestScenarioGeneralForm";
import TestScenarioUserForm from "@/pages/test/components/TestScenarioUserForm";
import TestScenarioCoachStateForm from "@/pages/test/components/TestScenarioCoachStateForm";
import TestScenarioIdentitiesForm from "@/pages/test/components/TestScenarioIdentitiesForm";
import TestScenarioChatMessagesForm from "@/pages/test/components/TestScenarioChatMessagesForm";
import TestScenarioUserNotesForm from "@/pages/test/components/TestScenarioUserNotesForm";
import TestScenarioActionsForm from "@/pages/test/components/TestScenarioActionsForm";
import TestScenarioBreaksForm from "@/pages/test/components/TestScenarioBreaksForm";

interface TestScenarioEditorProps {
  scenario: TestScenario | null;
  onSave: (fields: {
    name: string;
    description: string;
    template: TestScenarioTemplate;
    imageFiles?: Map<number, File>;
  }) => void;
  onCancel: () => void;
  onDelete?: () => void;
}

const TestScenarioEditor = ({
  scenario,
  onSave,
  onCancel,
  onDelete,
}: TestScenarioEditorProps) => {
  const [name, setName] = useState(scenario?.name || "");
  const [description, setDescription] = useState(scenario?.description || "");
  const [firstName, setFirstName] = useState(
    (() => {
      const user =
        scenario?.template &&
        typeof scenario.template === "object" &&
        scenario.template.user
          ? (scenario.template.user as TestScenarioUser)
          : undefined;
      return user?.first_name || "";
    })()
  );
  const [lastName, setLastName] = useState(
    (() => {
      const user =
        scenario?.template &&
        typeof scenario.template === "object" &&
        scenario.template.user
          ? (scenario.template.user as TestScenarioUser)
          : undefined;
      return user?.last_name || "";
    })()
  );
  const testUserEmail =
    scenario?.template &&
    typeof scenario.template === "object" &&
    scenario.template.user
      ? (scenario.template.user as TestScenarioUser).email
      : undefined;
  const testUserPassword =
    scenario?.template &&
    typeof scenario.template === "object" &&
    scenario.template.user
      ? (scenario.template.user as TestScenarioUser).password
      : undefined;
  const [coachState, setCoachState] = useState<TestScenarioCoachState>(
    (() => {
      if (
        scenario?.template &&
        typeof scenario.template === "object" &&
        scenario.template.coach_state
      ) {
        return scenario.template.coach_state as TestScenarioCoachState;
      }
      return {};
    })()
  );
  const [identities, setIdentities] = useState<TestScenarioIdentity[]>(
    (() => {
      if (
        scenario?.template &&
        typeof scenario.template === "object" &&
        scenario.template.identities
      ) {
        return scenario.template.identities as TestScenarioIdentity[];
      }
      return [];
    })()
  );
  const [chatMessages, setChatMessages] = useState<TestScenarioChatMessage[]>(
    (() => {
      if (
        scenario?.template &&
        typeof scenario.template === "object" &&
        scenario.template.chat_messages
      ) {
        return scenario.template.chat_messages as TestScenarioChatMessage[];
      }
      return [];
    })()
  );
  const [userNotes, setUserNotes] = useState<TestScenarioUserNote[]>(
    (() => {
      if (
        scenario?.template &&
        typeof scenario.template === "object" &&
        scenario.template.user_notes
      ) {
        return scenario.template.user_notes as TestScenarioUserNote[];
      }
      return [];
    })()
  );
  const [actions, setActions] = useState<TestScenarioAction[]>(
    (() => {
      if (
        scenario?.template &&
        typeof scenario.template === "object" &&
        scenario.template.actions
      ) {
        return scenario.template.actions as TestScenarioAction[];
      }
      return [];
    })()
  );
  const [breaks, setBreaks] = useState<TestScenarioBreak[]>(
    (() => {
      if (
        scenario?.template &&
        typeof scenario.template === "object" &&
        scenario.template.breaks
      ) {
        return scenario.template.breaks as TestScenarioBreak[];
      }
      return [];
    })()
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("general");
  const [identityImageFiles, setIdentityImageFiles] = useState<Map<number, File>>(new Map());

  useEffect(() => {
    if (scenario) {
      setName(scenario.name || "");
      setDescription(scenario.description || "");

      const user = scenario.template &&
        typeof scenario.template === "object" &&
        scenario.template.user
          ? (scenario.template.user as TestScenarioUser)
          : undefined;
      setFirstName(user?.first_name || "");
      setLastName(user?.last_name || "");

      if (
        scenario.template &&
        typeof scenario.template === "object" &&
        scenario.template.coach_state
      ) {
        setCoachState(scenario.template.coach_state as TestScenarioCoachState);
      } else {
        setCoachState({});
      }

      if (
        scenario.template &&
        typeof scenario.template === "object" &&
        scenario.template.identities
      ) {
        setIdentities(scenario.template.identities as TestScenarioIdentity[]);
      } else {
        setIdentities([]);
      }

      if (
        scenario.template &&
        typeof scenario.template === "object" &&
        scenario.template.chat_messages
      ) {
        setChatMessages(scenario.template.chat_messages as TestScenarioChatMessage[]);
      } else {
        setChatMessages([]);
      }

      if (
        scenario.template &&
        typeof scenario.template === "object" &&
        scenario.template.user_notes
      ) {
        setUserNotes(scenario.template.user_notes as TestScenarioUserNote[]);
      } else {
        setUserNotes([]);
      }

      if (
        scenario.template &&
        typeof scenario.template === "object" &&
        scenario.template.actions
      ) {
        setActions(scenario.template.actions as TestScenarioAction[]);
      } else {
        setActions([]);
      }

      if (
        scenario.template &&
        typeof scenario.template === "object" &&
        scenario.template.breaks
      ) {
        setBreaks(scenario.template.breaks as TestScenarioBreak[]);
      } else {
        setBreaks([]);
      }
    } else {
      setName("");
      setDescription("");
      setFirstName("");
      setLastName("");
      setCoachState({});
      setIdentities([]);
      setChatMessages([]);
      setUserNotes([]);
      setActions([]);
      setBreaks([]);
    }
  }, [scenario]);

  const handleGeneralChange = (fields: {
    name: string;
    description: string;
  }) => {
    setName(fields.name);
    setDescription(fields.description);
  };

  const handleUserChange = (fields: {
    first_name: string;
    last_name: string;
  }) => {
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
      const template: TestScenarioTemplate = {
        user: { first_name: firstName, last_name: lastName },
        coach_state: {
          current_phase: coachState.current_phase || CoachingPhase.INTRODUCTION,
          identity_focus: coachState.identity_focus || IdentityCategory.PASSIONS_AND_TALENTS,
          who_you_are: coachState.who_you_are || [],
          who_you_want_to_be: coachState.who_you_want_to_be || [],
          ...coachState,
        },
      };

      if (identities && identities.length > 0) {
        template.identities = identities;
      }
      if (chatMessages && chatMessages.length > 0) {
        template.chat_messages = chatMessages;
      }
      if (userNotes && userNotes.length > 0) {
        template.user_notes = userNotes;
      }
      if (actions && actions.length > 0) {
        template.actions = actions;
      }
      if (breaks && breaks.length > 0) {
        template.breaks = breaks;
      }

      onSave({
        name,
        description,
        template,
        imageFiles: identityImageFiles.size > 0 ? identityImageFiles : undefined,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form
      className="w-7xl p-6 bg-card rounded-lg shadow mb-8"
      onSubmit={handleSubmit}
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold">
          {scenario ? "Edit Test Scenario" : "Create New Test Scenario"}
        </h2>
        {scenario && (
          <Badge variant="secondary" className="text-sm px-3 py-1.5">
            <span className="text-primary mr-1">Editing:</span>
            <span className="font-semibold">{scenario.name}</span>
          </Badge>
        )}
      </div>
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="user">User</TabsTrigger>
          <TabsTrigger value="coach_state">Coach State</TabsTrigger>
          <TabsTrigger value="identities">Identities</TabsTrigger>
          <TabsTrigger value="chat_messages">Chat Messages</TabsTrigger>
          <TabsTrigger value="user_notes">User Notes</TabsTrigger>
          <TabsTrigger value="actions">Actions</TabsTrigger>
          <TabsTrigger value="breaks">Breaks</TabsTrigger>
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
            email={testUserEmail}
            password={testUserPassword}
          />
        </TabsContent>
        <TabsContent value="coach_state">
          <TestScenarioCoachStateForm
            value={coachState}
            onChange={setCoachState}
            identities={identities}
          />
        </TabsContent>
        <TabsContent value="identities">
          <TestScenarioIdentitiesForm
            value={identities}
            onChange={setIdentities}
            onImageFilesChange={setIdentityImageFiles}
          />
        </TabsContent>
        <TabsContent value="chat_messages">
          <TestScenarioChatMessagesForm
            value={chatMessages}
            onChange={setChatMessages}
          />
        </TabsContent>
        <TabsContent value="user_notes">
          <TestScenarioUserNotesForm
            value={userNotes}
            onChange={setUserNotes}
          />
        </TabsContent>
        <TabsContent value="actions">
          <TestScenarioActionsForm
            value={actions}
            onChange={setActions}
          />
        </TabsContent>
        <TabsContent value="breaks">
          <TestScenarioBreaksForm
            value={breaks}
            onChange={setBreaks}
          />
        </TabsContent>
      </Tabs>
      {error && <div className="text-red-600 mt-2">{error}</div>}
      <div className="flex gap-2 mt-6">
        <Button type="submit" variant="default" disabled={saving}>
          {saving ? "Saving..." : "Save"}
        </Button>
        <Button
          type="button"
          onClick={onCancel}
          variant="secondary"
          disabled={saving}
        >
          Cancel
        </Button>
        {scenario && onDelete && (
          <Button
            type="button"
            onClick={onDelete}
            variant="destructive"
            disabled={saving}
          >
            Delete
          </Button>
        )}
      </div>
    </form>
  );
};

export default TestScenarioEditor;
