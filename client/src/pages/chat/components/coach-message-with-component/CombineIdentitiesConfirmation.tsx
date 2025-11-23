import React from "react";
import { ComponentConfig, ComponentIdentity } from "@/types/componentConfig";
import { CoachRequest } from "@/types/coachRequest";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import {
  getIdentityCategoryColor,
  getIdentityCategoryLightColor,
  getIdentityCategoryDarkColor,
} from "@/enums/identityCategory";
import {
  FaDollarSign,
  FaPiggyBank,
  FaUser,
  FaDumbbell,
  FaHeart,
  FaRegCheckSquare,
} from "react-icons/fa";
import { MdFamilyRestroom } from "react-icons/md";
import { BsStars } from "react-icons/bs";
import { AiOutlineSun } from "react-icons/ai";
import { createLogger, LogLevel } from "@/lib/logger";
const log = createLogger("CombineIdentitiesConfirmation", LogLevel.DEBUG);

const CATEGORY_ICON_MAP: Record<
  string,
  React.ComponentType<{ className?: string }>
> = {
  passions_and_talents: BsStars,
  maker_of_money: FaDollarSign,
  keeper_of_money: FaPiggyBank,
  spiritual: AiOutlineSun,
  personal_appearance: FaUser,
  physical_expression: FaDumbbell,
  familial_relations: MdFamilyRestroom,
  romantic_relation: FaHeart,
  doer_of_things: FaRegCheckSquare,
};

const getCategoryIcon = (category: string) => {
  const normalizedCategory = category.toLowerCase();
  if (CATEGORY_ICON_MAP[normalizedCategory]) {
    return CATEGORY_ICON_MAP[normalizedCategory];
  }
  for (const [key, icon] of Object.entries(CATEGORY_ICON_MAP)) {
    if (
      normalizedCategory.includes(key.split("_")[0]) ||
      key.split("_").some((part) => normalizedCategory.includes(part))
    ) {
      return icon;
    }
  }
  return FaUser;
};

const IdentityCard: React.FC<{ identity: ComponentIdentity | null }> = ({
  identity,
}) => {
  if (!identity) {
    return (
      <div className="w-fit min-w-[120px] max-w-[200px] p-4 rounded-lg border border-gray-300/50 dark:border-gray-700 bg-white/70 dark:bg-gray-900/30">
        <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
        <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
    );
  }

  const IconComponent = getCategoryIcon(String(identity.category || ""));
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
      className={`_IdentityCard w-fit min-w-[120px] max-w-[250px] p-4 rounded-lg border shadow-sm ${lightColorClasses} ${darkColorClasses}`}
    >
      <div className="flex items-center gap-2 mb-2">
        <IconComponent
          className={`w-4 h-4 ${darkColorClasses
            .split(" ")
            .filter((cls) => cls.startsWith("text-"))
            .join(" ")}`}
        />
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

export const CombineIdentitiesConfirmation: React.FC<{
  coachMessage: React.ReactNode;
  config: ComponentConfig;
  onSendUserMessageToCoach: (request: CoachRequest) => void;
  disabled: boolean;
}> = ({ coachMessage, config, onSendUserMessageToCoach, disabled }) => {
  const identities = (config.identities || []) as ComponentIdentity[];
  const identityA = identities[0] || null;
  const identityB = identities[1] || null;

  const hasButtons = config.buttons && config.buttons.length > 0;

  return (
    <div
      className={`_CombineIdentitiesConfirmation mb-4 p-4 rounded-xl ${
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
        We’ll combine these two identities into a single one.
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

        {(() => {
          // Determine which identity will be kept (same logic as backend)
          const passionsValue = "passions_and_talents";
          const categoryA = identityA?.category || "";
          const categoryB = identityB?.category || "";
          
          let savedIdentity;
          if ((categoryA === passionsValue) !== (categoryB === passionsValue)) {
            // Exactly one is Passions and Talents → keep the non-Passions one
            savedIdentity = categoryA === passionsValue ? identityB : identityA;
          } else {
            // Neither or both are Passions and Talents → keep identity A
            savedIdentity = identityA;
          }
          
          if (savedIdentity?.category) {
            const lightColorClasses = getIdentityCategoryLightColor(String(savedIdentity.category));
            const darkColorClasses = getIdentityCategoryDarkColor(String(savedIdentity.category));
            const IconComponent = getCategoryIcon(String(savedIdentity.category));
            
            return (
              <div className={`w-fit min-w-[160px] max-w-[300px] p-4 rounded-lg border shadow-sm ${lightColorClasses} ${darkColorClasses}`}>
                <div className="flex items-center gap-2 mb-2">
                  <IconComponent
                    className={`w-4 h-4 ${darkColorClasses
                      .split(" ")
                      .filter((cls) => cls.startsWith("text-"))
                      .join(" ")}`}
                  />
                  <div className="text-lg font-semibold text-center flex-1">
                    {identityA?.name && identityB?.name ? (
                      <div>
                        <div>{identityA.name}/</div>
                        <div>{identityB.name}</div>
                      </div>
                    ) : (
                      "<Name will be set>"
                    )}
                  </div>
                </div>
              </div>
            );
          }
          
          // Fallback if no saved identity category
          return (
            <div className="w-fit min-w-[160px] max-w-[300px] p-4 rounded-lg border-2 border-gold-400/80 dark:border-gold-500/80 bg-gold-50/60 dark:bg-gold-900/20">
              <div className="text-lg font-semibold text-gold-900 dark:text-gold-200 text-center">
                {identityA?.name && identityB?.name ? (
                  <div>
                    <div>{identityA.name}/</div>
                    <div>{identityB.name}</div>
                  </div>
                ) : (
                  "<Name will be set>"
                )}
              </div>
            </div>
          );
        })()}
      </div>

      {config.buttons && config.buttons.length > 0 && (
        <div className="_CombineIdentitiesConfirmationButtons mt-4 flex flex-wrap gap-2 justify-end">
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
