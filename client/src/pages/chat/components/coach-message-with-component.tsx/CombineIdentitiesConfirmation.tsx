import React from "react";
import { ComponentConfig, ComponentIdentity } from "@/types/componentConfig";
import { CoachRequest } from "@/types/coachRequest";
import MarkdownRenderer from "@/utils/MarkdownRenderer";

const IdentityCard: React.FC<{ identity: ComponentIdentity | null }>
  = ({ identity }) => {
  if (!identity) {
    return (
      <div className="flex-1 min-w-[220px] p-4 rounded-lg border border-gray-300/50 dark:border-gray-700 bg-white/70 dark:bg-gray-900/30">
        <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
        <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
    );
  }

  return (
    <div className="flex-1 min-w-[220px] p-4 rounded-lg border border-gold-400/60 dark:border-gold-600/60 bg-white/90 dark:bg-gray-900/40 shadow-sm">
      <div className="text-sm uppercase tracking-wide text-gray-600 dark:text-gray-300 mb-1">
        Identity
      </div>
      <div className="text-lg font-semibold text-gray-900 dark:text-gold-200">
        {identity.name}
      </div>
      {identity.category && (
        <div className="mt-2 inline-block text-xs px-2 py-0.5 rounded-full bg-gold-100 text-gold-800 dark:bg-gold-900/40 dark:text-gold-200">
          {identity.category.replace(/_/g, " ")}
        </div>
      )}
    </div>
  );
};

export const CombineIdentitiesConfirmation: React.FC<{
  coachMessage: React.ReactNode;
  config: ComponentConfig;
  onSelect: (request: CoachRequest) => void;
  disabled: boolean;
}> = ({ coachMessage, config, onSelect, disabled }) => {
  const identities = (config.identities || []) as ComponentIdentity[];
  const identityA = identities[0] || null;
  const identityB = identities[1] || null;
  const combinedName = [identityA?.name || "", identityB?.name || ""]
    .filter(Boolean)
    .join("/");

  const hasButtons = config.buttons && config.buttons.length > 0;

  return (
    <div
      className={`_CombineIdentitiesConfirmation mb-4 p-4 rounded-xl ${
        hasButtons ? "w-fit max-w-[100%]" : "w-fit max-w-[75%]"
      } leading-[1.5] shadow-sm animate-fadeIn break-words mr-auto bg-gold-100/60 border border-gold-400 dark:bg-transparent dark:border-gold-700 dark:text-gold-200`}
    >
      <div className="mb-3">
        {React.isValidElement(coachMessage) ? (
          coachMessage
        ) : (
          <MarkdownRenderer content={String(coachMessage)} />
        )}
      </div>

      <div className="mb-3 text-sm text-gray-700 dark:text-gray-300">
        We’ll combine these two identities into a single one. You can review the
        result before confirming.
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <IdentityCard identity={identityA} />

        <div className="flex items-center justify-center px-2 text-gray-700 dark:text-gray-300 select-none">
          <span className="hidden sm:block text-base">+</span>          
        </div>

        <IdentityCard identity={identityB} />

        <div className="flex items-center justify-center px-2 text-gray-700 dark:text-gray-300 select-none">
          <span className="text-2xl">=</span>
        </div>

        <div className="flex-1 min-w-[240px] p-4 rounded-lg border-2 border-emerald-400/80 dark:border-emerald-500/80 bg-emerald-50/60 dark:bg-emerald-900/20">
          <div className="text-sm uppercase tracking-wide text-emerald-700 dark:text-emerald-300 mb-1">
            Resulting Identity
          </div>
          <div className="text-lg font-semibold text-emerald-900 dark:text-emerald-200">
            {combinedName || "<Name will be set>"}
          </div>
          <div className="mt-2 text-xs text-emerald-800/80 dark:text-emerald-300/80">
            The resulting identity name will be set to “{combinedName || "A/B"}”.
          </div>
        </div>
      </div>

      {config.buttons && config.buttons.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2 justify-end">
          {config.buttons.map((button, index) => (
            <button
              key={index}
              onClick={() =>
                onSelect({ message: button.label, actions: button.actions })
              }
              disabled={disabled}
              className={`${
                button.label.toLowerCase() === "yes"
                  ? "bg-emerald-500 hover:bg-emerald-600 text-black"
                  : "bg-gray-300 hover:bg-gray-400 text-black dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-100"
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

