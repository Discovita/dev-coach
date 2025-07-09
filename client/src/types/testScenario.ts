export type TestScenario = {
    id: string;
    name: string;
    description: string;
    created_by?: string;
    template: Record<string, unknown>;
    created_at: string;
    updated_at: string;
  };