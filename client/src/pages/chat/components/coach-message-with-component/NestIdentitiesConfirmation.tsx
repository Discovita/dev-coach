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
const log = createLogger("NestIdentitiesConfirmation", LogLevel.DEBUG);

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

const NestedIdentityCard: React.FC<{
  parentIdentity: ComponentIdentity | null;
  nestedIdentity: ComponentIdentity | null;
}> = ({ parentIdentity, nestedIdentity }) => {
  if (!parentIdentity) {
    return (
      <div className="w-fit p-3 rounded-lg border border-gray-300/50 dark:border-gray-700 bg-white/70 dark:bg-gray-900/30">
        <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
        <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
    );
  }

  const ParentIcon = getIdentityCategoryIcon(
    String(parentIdentity.category || "")
  );
  const parentBadgeColorClasses = getIdentityCategoryColor(
    String(parentIdentity.category || "")
  );
  const parentLightColorClasses = getIdentityCategoryLightColor(
    String(parentIdentity.category || "")
  );
  const parentDarkColorClasses = getIdentityCategoryDarkColor(
    String(parentIdentity.category || "")
  );

  return (
    <div
      className={`_NestedIdentityCard w-fit p-3 rounded-lg border shadow-sm relative ${parentLightColorClasses} ${parentDarkColorClasses} flex items-center justify-center gap-3`}
    >
      <div className="flex flex-col items-center gap-2">
        <div className="flex items-center gap-2 mb-2">
          <div
            className={`text-lg font-semibold ${parentDarkColorClasses
              .split(" ")
              .filter((cls) => cls.startsWith("text-"))
              .join(" ")}`}
          >
            {parentIdentity.name}
          </div>
        </div>
        {parentIdentity.category && (
          <div
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${parentBadgeColorClasses} mb-2`}
          >
            <ParentIcon className="w-3 h-3" />
            <span className="font-medium">
              {parentIdentity.category.replace(/_/g, " ")}
            </span>
          </div>
        )}
      </div>

      <IdentityCard identity={nestedIdentity} />
    </div>
  );
};

export const NestIdentitiesConfirmation: React.FC<{
  coachMessage: React.ReactNode;
  config: ComponentConfig;
  onSendUserMessageToCoach: (request: CoachRequest) => void;
  disabled: boolean;
}> = ({ coachMessage, config, onSendUserMessageToCoach, disabled }) => {
  const identities = (config.identities || []) as ComponentIdentity[];
  // First identity is the nested one, second is the parent
  const nestedIdentity = identities[0] || null;
  const parentIdentity = identities[1] || null;

  const hasButtons = config.buttons && config.buttons.length > 0;

  return (
    <div
      className={`_NestIdentitiesConfirmation mb-4 p-3 rounded-xl ${
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

      <div className="mb-3 text-sm text-gray-700 dark:text-gray-300">
        We'll nest the first identity under the second one.
      </div>

      <div className="flex flex-wrap items-center gap-3 justify-start">
        {/* Nested Identity */}
        <IdentityCard identity={nestedIdentity} />

        {/* Arrow pointing right */}
        <div className="flex items-center justify-center px-2 text-gray-700 dark:text-gray-300 select-none">
          <span className="text-xl">→</span>
        </div>

        {/* Parent Identity */}
        <IdentityCard identity={parentIdentity} />

        {/* Equals sign */}
        <div className="flex items-center justify-center px-2 text-gray-700 dark:text-gray-300 select-none">
          <span className="text-xl font-bold">=</span>
        </div>

        {/* Combined visual: Parent with nested inside */}
        <NestedIdentityCard
          parentIdentity={parentIdentity}
          nestedIdentity={nestedIdentity}
        />
      </div>

      {config.buttons && config.buttons.length > 0 && (
        <div className="_NestIdentitiesConfirmationButtons mt-4 flex flex-wrap gap-2 justify-end">
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
