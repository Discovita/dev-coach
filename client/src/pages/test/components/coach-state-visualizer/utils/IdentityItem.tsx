import React, { useState } from "react";
import { Identity } from "@/types/identity";
import { IdentityState } from "@/enums/identityState";
import {
  getIdentityCategoryDisplayName,
  getIdentityCategoryColor,
} from "@/enums/identityCategory";
import { Badge } from "@/components/ui/badge";
import {
  UserIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  StarIcon,
  TargetIcon,
} from "lucide-react";

interface IdentityItemProps {
  identity: Identity;
}

const IdentityItem: React.FC<IdentityItemProps> = ({ identity }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Get state display info
  const getStateInfo = (state?: string) => {
    console.log("state", state);
    switch (state) {
      case IdentityState.PROPOSED.toString():
        return {
          icon: AlertCircleIcon,
          color: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
          label: "Proposed",
        };
      case IdentityState.ACCEPTED.toString():
        return {
          icon: CheckCircleIcon,
          color: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
          label: "Accepted",
        };
      case IdentityState.REFINEMENT_COMPLETE.toString():
        return {
          icon: StarIcon,
          color: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
          label: "Refinement Complete",
        };
      case IdentityState.COMMITMENT_COMPLETE.toString():
        return {
          icon: TargetIcon,
          color: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
          label: "Commitment Complete",
        };
      default:
        return {
          icon: AlertCircleIcon,
          color: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
          label: "Unknown",
        };
    }
  };

  const stateInfo = getStateInfo(identity.state);
  const StateIcon = stateInfo.icon;

  // Check if there are expandable details
  const hasExpandableDetails = 
    identity.i_am_statement || 
    identity.visualization || 
    (identity.notes && identity.notes.length > 0);

  return (
    <div className="_IdentityItem border rounded-md overflow-hidden bg-white dark:bg-neutral-800 shadow">
      <div
        className="flex justify-between items-center px-4 py-2 bg-gold-100 dark:bg-gold-900/20 cursor-pointer transition-colors"
        onClick={() => hasExpandableDetails && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <UserIcon className="w-4 h-4 text-gold-600 dark:text-gold-400" />
          <div className="text-sm text-gold-600 dark:text-gold-300">
            {identity.name}
          </div>
        </div>
        {hasExpandableDetails && (
          <span
            className={`text-xs transition-transform ${
              isExpanded ? "" : "rotate-[-90deg]"
            }`}
          >
            ▼
          </span>
        )}
      </div>
      {isExpanded && hasExpandableDetails && (
        <div className="p-3 bg-[#f8f8f8] dark:bg-neutral-700">
          {/* Category and State Badges */}
          <div className="flex flex-wrap gap-2 mb-3">
            <Badge className={`text-xs ${getIdentityCategoryColor(identity.category)}`}>
              {getIdentityCategoryDisplayName(identity.category)}
            </Badge>
            <Badge className={`text-xs ${stateInfo.color}`}>
              <StateIcon className="w-3 h-3 mr-1" />
              {stateInfo.label}
            </Badge>
          </div>

          {/* I Am Statement */}
          {identity.i_am_statement && (
            <div className="mb-3">
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                <strong>I Am Statement:</strong>
              </div>
              <div className="text-xs text-[#333] dark:text-gold-50 italic">
                "{identity.i_am_statement}"
              </div>
            </div>
          )}

          {/* Visualization */}
          {identity.visualization && (
            <div className="mb-3">
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                <strong>Visualization:</strong>
              </div>
              <div className="text-xs text-[#333] dark:text-gold-50">
                {identity.visualization}
              </div>
            </div>
          )}

          {/* Notes */}
          {identity.notes && identity.notes.length > 0 && (
            <div>
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                <strong>Notes ({identity.notes.length}):</strong>
              </div>
              <ul className="space-y-1">
                {identity.notes.map((note, index) => (
                  <li key={index} className="text-xs text-[#333] dark:text-gold-50">
                    • {note}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default IdentityItem;
