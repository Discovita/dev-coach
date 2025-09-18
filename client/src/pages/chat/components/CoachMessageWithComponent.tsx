import React from "react";
import { ComponentConfig } from "@/types/componentConfig";
import { CoachRequest } from "@/types/coachRequest";

export interface CoachMessageWithComponentProps {
  /**
   * The coach message content (typically markdown)
   */
  children: React.ReactNode;

  /**
   * Component configuration containing buttons to render
   */
  componentConfig: ComponentConfig;

  /**
   * Callback when a button is clicked
   * @param request The CoachRequest object containing the message and actions
   */
  onSelect: (request: CoachRequest) => void;

  /**
   * Whether buttons should be disabled (e.g., while processing)
   */
  disabled: boolean;
}

export const CoachMessageWithComponent: React.FC<
  CoachMessageWithComponentProps
> = ({ children, componentConfig, onSelect, disabled }) => {
  return (
    <div className="_CoachMessageWithComponent mb-4 p-3.5 pr-4 pl-4 rounded-t-[18px] rounded-br-[18px] rounded-bl-[6px] w-fit max-w-[100%] leading-[1.5] shadow-sm animate-fadeIn break-words mr-auto bg-gold-200 border-l-[3px] border-l-gold-600 dark:bg-transparent dark:border-r-[1px] dark:border-r-gold-600 dark:border-t-[1px] dark:border-t-gold-600 dark:border-b-[1px] dark:border-b-gold-600 dark:text-gold-200">
      {/* Render the coach message content */}
      <div className="max-w-[75%]">{children}</div>

      {/* Render component buttons if they exist */}
      {componentConfig.buttons && componentConfig.buttons.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2 justify-end">
          {componentConfig.buttons.map((button, index) => (
            <button
              key={index}
              onClick={() => onSelect({ message: button.label, actions: button.actions })}
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
