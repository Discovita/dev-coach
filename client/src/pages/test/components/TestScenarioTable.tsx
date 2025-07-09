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
}

const TestScenarioTable = ({ scenarios, isLoading, isError, onEdit }: TestScenarioTableProps) => {
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
            onClick={() => onEdit(params.data as TestScenario)}
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
    [onEdit]
  );

  return (
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
  );
};

export default TestScenarioTable; 