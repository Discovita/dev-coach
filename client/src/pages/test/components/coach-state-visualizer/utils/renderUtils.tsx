import React from "react";
import { CoachResponse } from "@/types/coachResponse";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import { copyToClipboard } from "./dataUtils";
import { Button } from "@/components/ui/button";

/**
 * Minimal Action type for rendering actions in the visualizer.
 * If a more complete type is available, import it instead.
 */
type Action = {
  type: string;
  params?: { name: string; value: unknown }[];
};

export const renderJsonSection = (
  title: string,
  data: Record<string, unknown> | unknown[] | null | undefined,
  sectionKey: string,
  isExpanded: boolean,
  toggleSection: (section: string) => void
): React.ReactElement | null => {
  if (!data || (Array.isArray(data) && data.length === 0)) return null;

  return (
    <div className="mb-4 border rounded-md overflow-hidden border-gold-600">
      <div
        className="flex justify-between items-center px-4 py-2 bg-gold-200 dark:bg-neutral-800 cursor-pointer transition-colors"
        onClick={() => toggleSection(sectionKey)}
      >
        <h3 className="m-0 text-base font-semibold text-gold-900 dark:text-gold-200">
          {title}
        </h3>
        <div className="flex items-center gap-2">
          <Button
            className="rounded-md px-2 py-1 text-xs font-medium transition-colors hover:bg-gold-600"
            onClick={(e) => {
              e.stopPropagation();
              copyToClipboard(data);
            }}
          >
            Copy
          </Button>
          <span
            className={`text-xs transition-transform ${
              isExpanded ? "" : "rotate-[-90deg]"
            }`}
          >
            ▼
          </span>
        </div>
      </div>
      {isExpanded && (
        <pre className="m-0 p-3 bg-[#f8f8f8] dark:bg-neutral-700 overflow-x-auto font-mono text-xs text-[#333] dark:text-gold-50 whitespace-pre-wrap break-words w-full box-border">
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
};

export const renderActionsSection = (
  title: string,
  actions: Action[],
  sectionKey: string,
  isExpanded: boolean,
  toggleSection: (section: string) => void
): React.ReactElement | null => {
  if (!actions || actions.length === 0) return null;

  return (
    <div className="mb-4 border rounded-md overflow-hidden border-gold-600">
      <div
        className="flex justify-between items-center px-4 py-2 bg-gold-200 dark:bg-neutral-800 cursor-pointer transition-colors"
        onClick={() => toggleSection(sectionKey)}
      >
        <h3 className="m-0 text-base font-semibold text-gold-700 dark:text-gold-200">
          {title}
        </h3>
        <div className="flex items-center gap-2">
          <Button
            className="rounded-md px-2 py-1 text-xs font-medium transition-colors hover:bg-gold-600"
            onClick={(e) => {
              e.stopPropagation();
              copyToClipboard(actions);
            }}
          >
            Copy
          </Button>
          <span
            className={`text-xs transition-transform ${
              isExpanded ? "" : "rotate-[-90deg]"
            }`}
          >
            ▼
          </span>
        </div>
      </div>
      {isExpanded && (
        <div className="flex flex-col gap-3 p-4 max-h-[500px] overflow-y-auto bg-gold-50 dark:bg-neutral-700">
          {actions.map((action: Action, index: number) => (
            <div
              key={index}
              className="rounded-md border overflow-hidden bg-white dark:bg-neutral-800 shadow transition-transform hover:-translate-y-0.5 hover:shadow-lg"
            >
              <div className="px-4 py-2 text-white font-semibold text-sm uppercase tracking-wide bg-gold-500 dark:bg-gold-600">
                {action.type}
              </div>
              <div className="p-3">
                {action.params && action.params.length > 0 ? (
                  <table className="w-full border-collapse text-sm">
                    <thead>
                      <tr>
                        <th className="bg-[#f8f8f8] dark:bg-neutral-700 font-semibold text-[#555] dark:text-gold-50 p-2 text-left">
                          Parameter
                        </th>
                        <th className="bg-[#f8f8f8] dark:bg-neutral-700 font-semibold text-[#555] dark:text-gold-50 p-2 text-left">
                          Value
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {action.params.map((param: { name: string; value: unknown }, pIndex: number) => (
                        <tr key={pIndex}>
                          <td className="font-medium text-[#555] dark:text-gold-100 w-2/5 p-2">
                            {param.name}
                          </td>
                          <td className="font-mono bg-[#f9f9f9] dark:bg-neutral-900 p-2 rounded break-words max-w-[60%] text-[#333] dark:text-gold-50">
                            {JSON.stringify(param.value)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="italic text-[#888] dark:text-gold-200 text-center p-2">
                    No parameters
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const renderFinalPrompt = (
  lastResponse: CoachResponse | undefined,
  isExpanded: boolean,
  toggleSection: (section: string) => void
): React.ReactElement | null => {
  if (!lastResponse?.final_prompt) return null;

  return (
    <div className="mb-4 border rounded-md overflow-hidden border-gold-600">
      <div
        className="flex justify-between items-center px-4 py-2 bg-gold-200 dark:bg-neutral-800 cursor-pointer transition-colors"
        onClick={() => toggleSection("prompt")}
      >
        <h3 className="m-0 text-base font-semibold text-gold-900 dark:text-gold-200">
          Final Prompt
        </h3>
        <div className="flex items-center gap-2">
          <Button
            className="bg-gold-500 dark:bg-gold-600 rounded-md px-2 py-1 text-xs font-medium transition-colors hover:bg-gold-700 dark:hover:bg-gold-700"
            onClick={(e) => {
              e.stopPropagation();
              copyToClipboard(lastResponse.final_prompt);
            }}
          >
            Copy
          </Button>
          <span
            className={`text-xs transition-transform ${
              isExpanded ? "" : "rotate-[-90deg]"
            }`}
          >
            ▼
          </span>
        </div>
      </div>
      {isExpanded && (
        <div className="flex flex-col flex-1 min-h-0">
          <MarkdownRenderer
            content={lastResponse.final_prompt}
            className="flex-1 min-h-0 p-4 bg-gold-50 dark:bg-neutral-700 overflow-y-auto text-sm leading-[1.5] text-[#333] dark:text-gold-50 scrollbar w-full max-w-full break-words whitespace-pre-wrap box-border"
          />
        </div>
      )}
    </div>
  );
};

export const renderEmptyState = (
  primaryText: string,
  secondaryText?: string
): React.ReactElement => {
  return (
    <div className="p-6 text-center bg-gold-50 dark:bg-neutral-800 border border-dashed rounded-md text-neutral-400 dark:border-gold-500">
      <p className="font-medium mb-2">{primaryText}</p>
      {secondaryText && <p className="mt-1">{secondaryText}</p>}
    </div>
  );
};
