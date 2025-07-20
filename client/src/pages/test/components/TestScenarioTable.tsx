import { useMemo } from "react";
import { AgGridReact } from "ag-grid-react";
import { ColDef, ICellRendererParams } from "ag-grid-community";
import { Button } from "@/components/ui/button";
import { TestScenario } from "@/types/testScenario";
import { themeQuartz } from "ag-grid-community";

interface TestScenarioTableProps {
  scenarios: TestScenario[] | undefined;
  isLoading: boolean;
  isError: boolean;
  onEdit: (scenario: TestScenario) => void;
  onDelete: (scenario: TestScenario) => void;
  /**
   * Handler for starting a scenario (continue from current state)
   * Provided by Test.tsx
   */
  onStart: (scenario: TestScenario) => void;
  /**
   * Handler for starting a scenario fresh (reset to template)
   * Provided by Test.tsx
   */
  onStartFresh: (scenario: TestScenario) => void;
}

const TestScenarioTable = ({
  scenarios,
  isLoading,
  isError,
  onEdit,
  onDelete,
  onStart,
}: TestScenarioTableProps) => {
  // Dummy handlers for Start and Start Fresh actions
  // const handleStart = (scenario: TestScenario) => {
  //   // TODO: Implement navigation to session (continue)
  //   console.log("Start (continue) scenario", scenario.id);
  // };
  // const handleStartFresh = (scenario: TestScenario) => {
  //   // TODO: Implement reset and navigation
  //   console.log("Start Fresh scenario", scenario.id);
  // };

  const columnDefs = useMemo<ColDef<TestScenario>[]>(
    () => [
      { field: "name", headerName: "Name", flex: 1 },
      { field: "description", headerName: "Description", flex: 2 },
      {
        headerName: "Actions",
        field: undefined, // Not a real data field
        cellRenderer: (params: ICellRendererParams<TestScenario>) => (
          <div className="flex gap-2 mt-1">
            <Button
              size="xs"
              variant="default"
              onClick={() => onStart(params.data as TestScenario)}
            >
              Start
            </Button>
            <Button
              size="xs"
              variant="secondary"
              onClick={() => onEdit(params.data as TestScenario)}
            >
              Edit
            </Button>
            <Button
              size="xs"
              variant="destructive"
              onClick={() => onDelete(params.data as TestScenario)}
            >
              Delete
            </Button>
          </div>
        ),
        width: 230,
        sortable: false,
        filter: false,
      },
    ],
    [onEdit, onDelete, onStart]
  );

  return (
    <div className="_TestScenarioTable w-full">
      {isLoading ? (
        <div className="ag-overlay-loading-center">Loading...</div>
      ) : isError ? (
        <div className="ag-overlay-loading-center text-red-600">
          Error loading scenarios.
        </div>
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
  );
};

export default TestScenarioTable;
