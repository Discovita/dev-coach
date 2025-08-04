import React from "react";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import { copyToClipboard } from "./dataUtils";
import { Button } from "@/components/ui/button";
import { Action } from "@/types/action";
import ActionItem from "@/pages/test/components/coach-state-visualizer/utils/ActionItem";

export const renderJsonSection = (
  title: string,
  data: Record<string, unknown> | unknown[] | null | undefined,
  sectionKey: string,
  isExpanded: boolean,
  toggleSection: (section: string) => void
): React.ReactElement | null => {
  if (!data || (Array.isArray(data) && data.length === 0)) return null;

  return (
    <div className="_JSONSection mb-4 border rounded-md overflow-hidden border-gold-600">
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
    <div className="_ActionsSection mb-4 border rounded-md overflow-hidden border-gold-600">
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
        <div className="flex flex-col gap-2 p-4 max-h-full overflow-y-auto bg-gold-50 dark:bg-neutral-700">
          {actions.map((action: Action, index: number) => (
            <ActionItem key={index} action={action} />
          ))}
        </div>
      )}
    </div>
  );
};

export const renderFinalPrompt = (
  prompt: string,
  isExpanded: boolean,
  toggleSection: (section: string) => void
): React.ReactElement | null => {
  return (
    <div className="_FinalPrompt mb-4 border rounded-md overflow-hidden border-gold-600">
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
              copyToClipboard(prompt);
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
            content={prompt}
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
    <div className="_EmptyState p-6 text-center bg-gold-50 dark:bg-neutral-800 border border-dashed rounded-md text-neutral-400 dark:border-gold-500">
      <p className="font-medium mb-2">{primaryText}</p>
      {secondaryText && <p className="mt-1">{secondaryText}</p>}
    </div>
  );
};
