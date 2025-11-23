import React from "react";
import { ComponentConfig, ComponentIdentity } from "@/types/componentConfig";
import { CoachRequest } from "@/types/coachRequest";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import {
  getIdentityCategoryColor,
  getIdentityCategoryLightColor,
  getIdentityCategoryDarkColor,
} from "@/enums/identityCategory";
import { createLogger, LogLevel } from "@/lib/logger";
import { getIdentityCategoryIcon } from "@/utils/getIdentityCategoryIcon";
import { Trash2 } from "lucide-react";
import { motion } from "framer-motion";
const log = createLogger("ArchiveIdentityConfirmation", LogLevel.DEBUG);

const IdentityCard: React.FC<{ identity: ComponentIdentity | null }> = ({
  identity,
}) => {
  if (!identity) {
    return (
      <div className="w-fit p-3 rounded-lg border border-gray-300/50 dark:border-gray-700 bg-white/70 dark:bg-gray-900/30">
        <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
        <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
    );
  }

  const IconComponent = getIdentityCategoryIcon(
    String(identity.category || "")
  );
  const badgeColorClasses = getIdentityCategoryColor(
    String(identity.category || "")
  );
  const lightColorClasses = getIdentityCategoryLightColor(
    String(identity.category || "")
  );
  const darkColorClasses = getIdentityCategoryDarkColor(
    String(identity.category || "")
  );

  return (
    <div
      className={`_IdentityCard w-fit p-3 rounded-lg border shadow-sm ${lightColorClasses} ${darkColorClasses}`}
    >
      <div className="flex items-center gap-2 mb-2">
        <div
          className={`text-lg font-semibold ${darkColorClasses
            .split(" ")
            .filter((cls) => cls.startsWith("text-"))
            .join(" ")}`}
        >
          {identity.name}
        </div>
      </div>
      {identity.category && (
        <div
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${badgeColorClasses}`}
        >
          <IconComponent className="w-3 h-3" />
          <span className="font-medium">
            {identity.category.replace(/_/g, " ")}
          </span>
        </div>
      )}
    </div>
  );
};

const ArchivedIdentityCard: React.FC<{
  identity: ComponentIdentity | null;
}> = ({ identity }) => {
  if (!identity) {
    return (
      <div className="w-12 h-12 rounded border border-gray-300/50 dark:border-gray-700 bg-white/70 dark:bg-gray-900/30 animate-pulse" />
    );
  }

  const lightColorClasses = getIdentityCategoryLightColor(
    String(identity.category || "")
  );
  const darkColorClasses = getIdentityCategoryDarkColor(
    String(identity.category || "")
  );

  return (
    <div
      className={`_ArchivedIdentityCard w-12 h-12 rounded border shadow-sm relative ${lightColorClasses} ${darkColorClasses} opacity-70 transform rotate-12`}
    >
      {/* X icon overlay */}
      <div className="absolute inset-0 flex items-center justify-center z-10">
        <div className="text-xs font-bold text-red-500 dark:text-red-400">
          ✕
        </div>
      </div>
      <div className="absolute inset-0 flex items-center justify-center z-20">
        <div
          className={`text-[8px] font-semibold line-through ${darkColorClasses
            .split(" ")
            .filter((cls) => cls.startsWith("text-"))
            .join(" ")}`}
        >
          {identity.name.length > 8 ? identity.name.substring(0, 6) + "..." : identity.name}
        </div>
      </div>
    </div>
  );
};

const TrashCan: React.FC = () => {
  return (
    <div className="relative flex flex-col items-center justify-center">
      <Trash2 
        size={80} 
        className="text-gray-600 dark:text-gray-400 drop-shadow-lg"
        strokeWidth={1.5}
      />
    </div>
  );
};

export const ArchiveIdentityConfirmation: React.FC<{
  coachMessage: React.ReactNode;
  config: ComponentConfig;
  onSendUserMessageToCoach: (request: CoachRequest) => void;
  disabled: boolean;
}> = ({ coachMessage, config, onSendUserMessageToCoach, disabled }) => {
  const identities = (config.identities || []) as ComponentIdentity[];
  const identity = identities[0] || null;

  const hasButtons = config.buttons && config.buttons.length > 0;

  return (
    <div
      className={`_ArchiveIdentityConfirmation mb-4 p-3 rounded-xl ${
        hasButtons ? "w-fit max-w-[100%]" : "w-fit max-w-[75%]"
      } leading-[1.5] shadow-sm animate-fadeIn break-words mr-auto bg-gold-200`}
    >
      <div className="mb-3">
        {React.isValidElement(coachMessage) ? (
          coachMessage
        ) : (
          <MarkdownRenderer content={String(coachMessage)} />
        )}
      </div>

      <div className="flex flex-wrap items-center gap-4 justify-start relative">
        {/* Original Identity */}
        <IdentityCard identity={identity} />

        {/* Arrow pointing right */}
        <div className="flex items-center justify-center px-2 text-gray-700 dark:text-gray-300 select-none">
          <span className="text-xl">→</span>
        </div>

        {/* Trash can with animated card */}
        <div className="relative">
          <TrashCan />
          {/* Small card that animates into trash can and disappears */}
          <motion.div 
            className="absolute top-10 left-1/2"
            initial={{ 
              x: -80, 
              y: -20, 
              rotate: -12, 
              scale: 1,
              opacity: 1 
            }}
            animate={{ 
              x: [-80, -40, 0], // Move horizontally from start to end
              y: [-20, -50, 0], // Arc up high, then down into trashcan
              rotate: [-12, 45, 90], // Rotate as it arcs
              scale: [1, 0.7, 0.5], // Shrink as it moves
              opacity: [1, 0.8, 0] // Fade out
            }}
            transition={{
              duration: 1.5,
              times: [0, 0.5, 1], // Keyframe timing: start, peak of arc, end
              ease: "easeInOut",
              x: {
                type: "tween",
                duration: 1.5,
                ease: "easeInOut",
              },
              y: {
                type: "tween",
                duration: 1.5,
                ease: [0.25, 0.1, 0.25, 1], // Smooth arc: slow start, fast middle, slow end
              },
              rotate: {
                type: "tween",
                duration: 1.5,
                ease: "easeInOut",
              },
              scale: {
                type: "tween",
                duration: 1.5,
                ease: "easeInOut",
              },
              opacity: {
                type: "tween",
                duration: 1.5,
                ease: "easeOut",
                times: [0, 0.7, 1], // Fade out in last 30%
              }
            }}
            style={{
              transformOrigin: "center center",
            }}
          >
            <ArchivedIdentityCard identity={identity} />
          </motion.div>
        </div>
      </div>

      {config.buttons && config.buttons.length > 0 && (
        <div className="_ArchiveIdentityConfirmationButtons mt-4 flex flex-wrap gap-2 justify-end">
          {config.buttons.map((button, index) => (
            <button
              key={index}
              onClick={() => {
                log.debug(`Button '${button.label}' was clicked`);
                onSendUserMessageToCoach({
                  message: button.label,
                  actions: button.actions,
                });
              }}
              disabled={disabled}
              className={`${
                button.label.toLowerCase() === "yes"
                  ? "bg-gold-500 hover:bg-gold-600 text-black"
                  : "bg-gold-300 hover:bg-gold-400 text-black dark:bg-gold-100 dark:hover:bg-gold-200 dark:text-gold-100"
              } px-3 py-1.5 text-sm font-medium rounded-md transition-colors cursor-pointer`}
            >
              {button.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

