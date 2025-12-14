import React, { useMemo, useState } from "react";
import { ComponentConfig, ComponentAction, ComponentIdentity, ComponentText } from "@/types/componentConfig";
import { CoachRequest } from "@/types/coachRequest";
import { ActionType } from "@/enums/actionType";
import MarkdownRenderer from "@/utils/MarkdownRenderer";

export const SuggestIAmStatementComponent: React.FC<{
  coachMessage: React.ReactNode;
  config: ComponentConfig;
  onSendUserMessageToCoach: (request: CoachRequest) => void;
  disabled: boolean;
}> = ({ coachMessage, config, onSendUserMessageToCoach, disabled }) => {
  const initialStatement = useMemo<string>(() => {
    const textBlocks = config.texts as ComponentText[] | undefined;
    return textBlocks && textBlocks.length > 0 ? textBlocks[0].text : "";
  }, [config.texts]);

  const identity = useMemo<ComponentIdentity | null>(() => {
    const ids = config.identities as ComponentIdentity[] | undefined;
    return ids && ids.length > 0 ? ids[0] : null;
  }, [config.identities]);

  const [statement, setStatement] = useState<string>(initialStatement);

  const hasButtons = Boolean(config.buttons && config.buttons.length > 0);

  const buildActionsWithStatement = (actions?: ComponentAction[]): ComponentAction[] | undefined => {
    if (!actions) return undefined;
    return actions.map((action) => {
      const params = { ...(action.params || {}) };

      // Always apply the current statement to relevant actions
      if (
        action.action === ActionType.UPDATE_I_AM_STATEMENT ||
        action.action === ActionType.PERSIST_SUGGEST_I_AM_STATEMENT_COMPONENT ||
        "i_am_statement" in params
      ) {
        params["i_am_statement"] = statement;
      }

      return {
        action: action.action,
        params,
      };
    });
  };

  const handleClick = (label: string, actions?: ComponentAction[]) => {
    const updatedActions = buildActionsWithStatement(actions);
    const message =
      label === "I came up with my own" && statement.trim().length > 0
        ? statement
        : label;

    onSendUserMessageToCoach({
      message,
      actions: updatedActions,
    });
  };

  return (
    <div
      className={`_SuggestIAmStatementComponent mb-4 p-4 rounded-xl ${
        hasButtons ? "w-fit max-w-[100%]" : "w-fit max-w-[75%]"
      } leading-[1.5] shadow-sm animate-fadeIn break-words mr-auto bg-gold-200 dark:bg-transparent dark:border dark:border-gold-600 dark:text-gold-200`}
    >
      <div className="mb-3">
        {React.isValidElement(coachMessage) ? (
          coachMessage
        ) : (
          <MarkdownRenderer content={String(coachMessage)} />
        )}
      </div>

      {identity && (
        <div className="mb-2 text-sm font-semibold text-gray-800 dark:text-gold-100">
          {identity.name}
        </div>
      )}

      {hasButtons ? (
        <div className="flex flex-col gap-3">
          <label className="text-sm text-gray-700 dark:text-gold-200">
            Suggested I Am statement
          </label>
          <textarea
            value={statement}
            onChange={(event) => setStatement(event.target.value)}
            disabled={disabled}
            className="w-full min-h-[120px] rounded-md border border-gold-400 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-gold-600 focus:outline-none focus:ring-1 focus:ring-gold-600 dark:bg-[#1f1f1f] dark:text-gold-100 dark:border-gold-700"
          />

          {config.buttons && config.buttons.length > 0 && (
            <div className="flex flex-wrap gap-2 justify-end">
              {config.buttons.map((button, index) => (
                <button
                  key={index}
                  onClick={() => handleClick(button.label, button.actions)}
                  disabled={disabled}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors cursor-pointer ${
                    button.label === "I love it"
                      ? "bg-gold-500 hover:bg-gold-600 text-black"
                      : "bg-gold-300 hover:bg-gold-400 text-black dark:bg-gold-100 dark:hover:bg-gold-200 dark:text-gold-900"
                  }`}
                >
                  {button.label}
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="mt-2 text-sm text-gray-800 dark:text-gold-100">
          <MarkdownRenderer content={statement || initialStatement} />
        </div>
      )}
    </div>
  );
};
