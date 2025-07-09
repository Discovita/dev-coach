import { useState, useMemo } from "react";
import { testStates } from "@/tests/testStates";
import TestStateSelector from "@/pages/test/components/TestStateSelector";
import TestChat from "@/pages/test/components/TestChat";
import { AgGridReact } from "ag-grid-react";
import {
  themeQuartz,
  ModuleRegistry,
  ClientSideRowModelModule,
  ValidationModule,
  ColDef,
} from "ag-grid-community";
import { ICellRendererParams } from "ag-grid-community"; // AG Grid cell renderer params type
import { Button } from "@/components/ui/button";
import { useTestScenarios } from "@/hooks/use-test-scenarios";
import { TestScenario } from "@/types/testScenario";
// If you see a type error for ag-grid-react, ensure @types/ag-grid-react is installed or use a type override.

// Register AG Grid modules
ModuleRegistry.registerModules([ClientSideRowModelModule, ValidationModule]);

// Placeholder for the editor component
const TestScenarioEditor = ({
  scenario,
  onSave,
  onCancel,
}: {
  scenario: TestScenario | null;
  onSave: () => void;
  onCancel: () => void;
}) => {
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

function Test() {
  const [selectedState, setSelectedState] = useState("");
  const [hasStarted, setHasStarted] = useState(false);
  // Fetch test scenarios from API
  const { data: scenarios, isLoading, isError } = useTestScenarios();
  const [editingScenario, setEditingScenario] = useState<TestScenario | null>(
    null
  );
  const [showEditor, setShowEditor] = useState(false);

  // AG Grid column definitions
  const columnDefs = useMemo<ColDef<TestScenario>[]>(
    () => [
      { field: "name", headerName: "Name", flex: 1 },
      { field: "description", headerName: "Description", flex: 2 },
      { field: "created_by", headerName: "Created By", flex: 1 },
      {
        headerName: "Actions",
        field: undefined, // Not a real data field
        cellRenderer: (params: ICellRendererParams<TestScenario>) => (
          <Button
            size="sm"
            variant="secondary"
            onClick={() => handleEditScenario(params.data as TestScenario)}
            className="mr-2"
          >
            Edit
          </Button>
        ),
        width: 120,
        sortable: false,
        filter: false,
      },
    ],
    []
  );

  // Handler for editing a scenario
  const handleEditScenario = (scenario: TestScenario) => {
    setEditingScenario(scenario);
    setShowEditor(true);
  };

  // Handler for creating a new scenario
  const handleCreateScenario = () => {
    setEditingScenario(null);
    setShowEditor(true);
  };

  // Handler for saving a scenario (placeholder)
  const handleSaveScenario = () => {
    // TODO: Implement save logic (POST/PUT to backend)
    setShowEditor(false);
    setEditingScenario(null);
    // Optionally, refresh the scenario list
  };

  // Handler for canceling edit/create
  const handleCancelEdit = () => {
    setShowEditor(false);
    setEditingScenario(null);
  };

  if (hasStarted) {
    return (
      <TestChat
        selectedState={selectedState}
        setHasStarted={setHasStarted}
        testStates={testStates}
      />
    );
  }

  return (
    <div className="_Test flex flex-col items-center w-full h-full p-4">
      {/* Existing test runner UI below */}
      <div className="w-full max-w-3xl">
        <TestStateSelector
          selectedState={selectedState}
          setSelectedState={setSelectedState}
          setHasStarted={setHasStarted}
          testStates={testStates}
        />
      </div>
      {/* AG Grid Table */}
      <div className="w-full max-w-5xl my-8">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Test Scenarios</h1>
          <Button variant="default" onClick={handleCreateScenario}>
            + New Scenario
          </Button>
        </div>
        <div className="w-full">
          {isLoading ? (
            <div className="ag-overlay-loading-center">Loading...</div>
          ) : isError ? (
            <div className="ag-overlay-loading-center text-red-600">Error loading scenarios.</div>
          ) : (
            <AgGridReact<TestScenario>
              theme={themeQuartz}
              rowData={scenarios || []}
              columnDefs={columnDefs}
              domLayout="autoHeight"
              animateRows={true}
              suppressHorizontalScroll={false}
              noRowsOverlayComponent={() => (
                <div className="ag-overlay-loading-center">
                  No test scenarios found.
                </div>
              )}
            />
          )}
        </div>
      </div>
      {/* Editor (not a modal) */}
      {showEditor && (
        <TestScenarioEditor
          scenario={editingScenario}
          onSave={handleSaveScenario}
          onCancel={handleCancelEdit}
        />
      )}
    </div>
  );
}

export default Test;
