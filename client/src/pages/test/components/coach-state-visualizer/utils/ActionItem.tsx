import React, { useState } from "react";
import { Action } from "@/types/action";

const ActionItem: React.FC<{ action: Action }> = ({ action }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const hasParameters =
    action.parameters &&
    typeof action.parameters === "object" &&
    !Array.isArray(action.parameters) &&
    Object.keys(action.parameters).length > 0;

  return (
    <div className="border rounded-md overflow-hidden bg-white dark:bg-neutral-800 shadow">
      <div
        className="flex justify-between items-center px-4 py-2 bg-blue-100 dark:bg-blue-900/20 cursor-pointer transition-colors"
        onClick={() => hasParameters && setIsExpanded(!isExpanded)}
      >
        <div className="text-sm text-blue-600 dark:text-blue-300">
          {action.result_summary || action.action_type_display}
        </div>
        {hasParameters && (
          <span
            className={`text-xs transition-transform ${
              isExpanded ? "" : "rotate-[-90deg]"
            }`}
          >
            ▼
          </span>
        )}
      </div>
      {isExpanded && hasParameters && (
        <div className="p-3 bg-[#f8f8f8] dark:bg-neutral-700">
          <div className="mb-2 text-xs text-gray-600 dark:text-gray-400">
            <strong>Action Type:</strong> {action.action_type_display}
          </div>
          <table className="w-full border-collapse text-xs">
            <thead>
              <tr>
                <th className="bg-[#f8f8f8] dark:bg-neutral-700 font-semibold text-[#555] dark:text-gold-50 p-1 text-left">
                  Parameter
                </th>
                <th className="bg-[#f8f8f8] dark:bg-neutral-700 font-semibold text-[#555] dark:text-gold-50 p-1 text-left">
                  Value
                </th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(action.parameters).map(
                ([name, value], pIndex) => (
                  <tr key={pIndex}>
                    <td className="font-medium text-[#555] dark:text-gold-100 w-2/5 p-1">
                      {name}
                    </td>
                    <td className="font-mono bg-[#f9f9f9] dark:bg-neutral-900 p-1 rounded break-words max-w-[60%] text-[#333] dark:text-gold-50">
                      {JSON.stringify(value)}
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ActionItem;
