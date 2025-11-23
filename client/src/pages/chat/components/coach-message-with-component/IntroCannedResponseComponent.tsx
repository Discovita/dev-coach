import React from "react";
import { ComponentConfig } from "@/types/componentConfig";
import { CoachRequest } from "@/types/coachRequest";
import MarkdownRenderer from "@/utils/MarkdownRenderer";

export const IntroCannedResponseComponent: React.FC<{
  coachMessage: React.ReactNode;
  config: ComponentConfig;
  onSendUserMessageToCoach: (request: CoachRequest) => void;
  disabled: boolean;
}> = ({ coachMessage, config, onSendUserMessageToCoach, disabled }) => {
  const hasButtons = config.buttons && config.buttons.length > 0;

  return (
    <div
      className={`_IntroCannedResponseComponent mb-4 p-3.5 pr-4 pl-4 rounded-t-[18px] rounded-br-[18px] rounded-bl-[6px] ${
        hasButtons ? "w-fit max-w-[100%]" : "w-fit max-w-[75%]"
      } leading-[1.5] shadow-sm animate-fadeIn break-words mr-auto bg-gold-200 border-l-[3px] border-l-gold-600 dark:bg-transparent dark:border-r-[1px] dark:border-r-gold-600 dark:border-t-[1px] dark:border-t-gold-600 dark:border-b-[1px] dark:border-b-gold-600 dark:text-gold-200`}
    >
      <div className="max-w-[75%]">
        {React.isValidElement(coachMessage) ? (
          coachMessage
        ) : (
          <MarkdownRenderer content={String(coachMessage)} />
        )}
      </div>

      {config.buttons && config.buttons.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2 justify-end">
          {config.buttons.map((button, index) => (
            <button
              key={index}
              onClick={() =>
                onSendUserMessageToCoach({ message: button.label, actions: button.actions })
              }
              disabled={disabled}
              className="px-3 py-1.5 text-sm font-medium rounded-md bg-gold-500 text-black hover:bg-gold-600 hover:text-gold-50 transition-colors cursor-pointer"
            >
              {button.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
