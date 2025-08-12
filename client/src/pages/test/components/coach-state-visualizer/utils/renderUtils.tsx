import React from "react";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import { copyToClipboard } from "./dataUtils";
import { Button } from "@/components/ui/button";
import { Action } from "@/types/action";
import ActionItem from "@/pages/test/components/coach-state-visualizer/utils/ActionItem";
import { CoachState } from "@/types/coachState";
import {
  getIdentityCategoryDisplayName,
  getIdentityCategoryColor,
} from "@/enums/identityCategory";
import {
  getCoachingPhaseDisplayName,
  getCoachingPhaseColor,
} from "@/enums/coachingPhase";
import { getGetToKnowYouQuestionDisplayName } from "@/enums/getToKnowYouQuestions";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  UserIcon,
  TargetIcon,
  SparklesIcon,
  ClockIcon,
  HeartIcon,
  StarIcon,
  ListIcon,
  HelpCircleIcon,
} from "lucide-react";

export const renderCoachState = () => {};

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

/**
 * Renders the Coach State in a beautiful, organized layout
 * Displays all coach state information in a structured, visually appealing way
 */
export const renderCoachStateSection = (
  coachState: CoachState | null | undefined,
  sectionKey: string,
  isExpanded: boolean,
  toggleSection: (section: string) => void
): React.ReactElement | null => {
  if (!coachState) {
    return (
      <div className="_CoachStateSection mb-4 border rounded-md overflow-hidden border-gold-600">
        <div
          className="flex justify-between items-center px-4 py-2 bg-gold-200 dark:bg-neutral-800 cursor-pointer transition-colors"
          onClick={() => toggleSection(sectionKey)}
        >
          <h3 className="m-0 text-base font-semibold text-gold-700 dark:text-gold-200">
            Coach State
          </h3>
          <span
            className={`text-xs transition-transform ${
              isExpanded ? "" : "rotate-[-90deg]"
            }`}
          >
            ▼
          </span>
        </div>
        {isExpanded && (
          <div className="p-4 bg-gold-50 dark:bg-neutral-700">
            <div className="text-center text-neutral-500 dark:text-neutral-400">
              <UserIcon className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No coach state available</p>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Helper function to format date
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="_CoachStateSection mb-4 border rounded-md overflow-hidden border-gold-600">
      <div
        className="flex justify-between items-center px-4 py-2 bg-gold-200 dark:bg-neutral-800 cursor-pointer transition-colors"
        onClick={() => toggleSection(sectionKey)}
      >
        <h3 className="m-0 text-base font-semibold text-gold-700 dark:text-gold-200">
          Coach State
        </h3>
        <div className="flex items-center gap-2">
          <Button
            className="rounded-md px-2 py-1 text-xs font-medium transition-colors hover:bg-gold-600"
            onClick={(e) => {
              e.stopPropagation();
              copyToClipboard(coachState);
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
        <div className="p-4 bg-gold-50 dark:bg-neutral-700">
          <Card className="border-gold-300 dark:border-gold-600">
            <CardContent>
              <div className="space-y-4">
                {/* Current Phase */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <TargetIcon className="w-4 h-4 text-gold-600 dark:text-gold-400" />
                    <span className="text-sm font-semibold text-gold-800 dark:text-gold-200">
                      Current Phase
                    </span>
                  </div>
                  <div className="text-right min-w-0 flex-1">
                    <Badge
                      className={`${getCoachingPhaseColor(
                        coachState.current_phase
                      )} text-xs`}
                    >
                      {getCoachingPhaseDisplayName(coachState.current_phase)}
                    </Badge>
                  </div>
                </div>

                {/* Identity Focus */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <SparklesIcon className="w-4 h-4 text-gold-600 dark:text-gold-400" />
                    <span className="text-sm font-semibold text-gold-800 dark:text-gold-200">
                      Focused Identity Category
                    </span>
                  </div>
                  <div className="text-right min-w-0 flex-1">
                    {coachState.identity_focus ? (
                      <Badge
                        className={`text-xs ${getIdentityCategoryColor(
                          coachState.identity_focus
                        )}`}
                      >
                        {getIdentityCategoryDisplayName(
                          coachState.identity_focus
                        )}
                      </Badge>
                    ) : (
                      <p className="text-xs text-neutral-500 dark:text-neutral-400 italic">
                        No identity focus set
                      </p>
                    )}
                  </div>
                </div>

                {/* Current Identity */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <UserIcon className="w-4 h-4 text-gold-600 dark:text-gold-400" />
                    <span className="text-sm font-semibold text-gold-800 dark:text-gold-200">
                      Current Identity
                    </span>
                  </div>
                  <div className="text-right min-w-0 flex-1">
                    {coachState.current_identity ? (
                      <p className="text-xs text-neutral-700 dark:text-neutral-300 break-words">
                        {coachState.current_identity.name}
                      </p>
                    ) : (
                      <p className="text-xs text-neutral-500 dark:text-neutral-400 italic">
                        None yet...
                      </p>
                    )}
                  </div>
                </div>

                {/* Who You Are */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <HeartIcon className="w-4 h-4 text-gold-600 dark:text-gold-400" />
                    <span className="text-sm font-semibold text-gold-800 dark:text-gold-200">
                      Who You Are
                    </span>
                  </div>
                  <div className="text-right min-w-0 flex-1">
                    {coachState.who_you_are &&
                    coachState.who_you_are.length > 0 ? (
                      <p className="text-xs text-neutral-700 dark:text-neutral-300 text-right break-words">
                        {coachState.who_you_are.join(", ")}
                      </p>
                    ) : (
                      <p className="text-xs text-neutral-500 dark:text-neutral-400 italic">
                        Nothing yet...
                      </p>
                    )}
                  </div>
                </div>

                {/* Who You Want To Be */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <StarIcon className="w-4 h-4 text-gold-600 dark:text-gold-400" />
                    <span className="text-sm font-semibold text-gold-800 dark:text-gold-200">
                      Who You Want To Be
                    </span>
                  </div>
                  <div className="text-right min-w-0 flex-1">
                    {coachState.who_you_want_to_be &&
                    coachState.who_you_want_to_be.length > 0 ? (
                      <p className="text-xs text-neutral-700 dark:text-neutral-300 text-right break-words">
                        {coachState.who_you_want_to_be.join(", ")}
                      </p>
                    ) : (
                      <p className="text-xs text-neutral-500 dark:text-neutral-400 italic">
                        Nothing yet...
                      </p>
                    )}
                  </div>
                </div>

                {/* Asked Questions */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <HelpCircleIcon className="w-4 h-4 text-gold-600 dark:text-gold-400" />
                    <span className="text-sm font-semibold text-gold-800 dark:text-gold-200">
                      Asked Questions
                    </span>
                  </div>
                  <div className="text-right min-w-0 flex-1">
                    {coachState.asked_questions &&
                    coachState.asked_questions.length > 0 ? (
                      <p className="text-xs text-neutral-700 dark:text-neutral-300 text-right break-words">
                        {coachState.asked_questions.map(question => getGetToKnowYouQuestionDisplayName(question)).join(", ")}
                      </p>
                    ) : (
                      <p className="text-xs text-neutral-500 dark:text-neutral-400 italic">
                        Nothing yet...
                      </p>
                    )}
                  </div>
                </div>

                {/* Skipped Categories */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <ListIcon className="w-4 h-4 text-gold-600 dark:text-gold-400" />
                    <span className="text-sm font-semibold text-gold-800 dark:text-gold-200">
                      Skipped Categories
                    </span>
                  </div>
                  <div className="text-right min-w-0 flex-1">
                    {coachState.skipped_identity_categories &&
                    coachState.skipped_identity_categories.length > 0 ? (
                      <div className="flex flex-wrap gap-1 justify-end">
                        {coachState.skipped_identity_categories.map(
                          (category, index) => (
                            <Badge
                              key={index}
                              className={`text-xs ${getIdentityCategoryColor(
                                category
                              )}`}
                            >
                              {getIdentityCategoryDisplayName(category)}
                            </Badge>
                          )
                        )}
                      </div>
                    ) : (
                      <p className="text-xs text-neutral-500 dark:text-neutral-400 italic">
                        No skipped categories
                      </p>
                    )}
                  </div>
                </div>
                {/* Last Updated */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <ClockIcon className="w-4 h-4 text-gold-600 dark:text-gold-400" />
                    <span className="text-sm font-semibold text-gold-800 dark:text-gold-200">
                      Last Updated
                    </span>
                  </div>
                  <div className="text-right min-w-0 flex-1">
                    <p className="text-xs text-neutral-500 dark:text-neutral-400">
                      {formatDate(coachState.updated_at)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Metadata - Full Width */}
              {coachState.metadata &&
                Object.keys(coachState.metadata).length > 0 && (
                  <div className="mt-6 pt-4 border-t border-gold-200 dark:border-gold-700">
                    <div className="space-y-2">
                      <h4 className="text-sm font-semibold text-gold-800 dark:text-gold-200">
                        Metadata
                      </h4>
                      <pre className="text-xs bg-neutral-100 dark:bg-neutral-800 p-2 rounded overflow-x-auto">
                        {JSON.stringify(coachState.metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
