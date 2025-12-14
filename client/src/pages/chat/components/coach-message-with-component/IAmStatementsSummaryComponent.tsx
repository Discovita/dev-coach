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
import { FiDownload } from "react-icons/fi";
import { MdFamilyRestroom } from "react-icons/md";
import { BsStars } from "react-icons/bs";
import { AiOutlineSun } from "react-icons/ai";
import { createLogger, LogLevel } from "@/lib/logger";
import { useDownloadIAmPdf } from "@/hooks/use-download-i-am-pdf";

const log = createLogger("IAmStatementsSummaryComponent", LogLevel.DEBUG);

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

const IdentityCard: React.FC<{ identity: ComponentIdentity }> = ({
  identity,
}) => {
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
      className={`_IdentityCard w-full p-4 rounded-lg border shadow-sm ${lightColorClasses} ${darkColorClasses}`}
    >
      <div className="flex items-center justify-between mb-3">
        <div
          className={`text-lg font-semibold ${darkColorClasses
            .split(" ")
            .filter((cls) => cls.startsWith("text-"))
            .join(" ")}`}
        >
          {identity.name}
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
      {identity.i_am_statement && (
        <div className="mt-3 pt-3 border-t border-gray-300/50 dark:border-gray-700">
          <div className="text-sm text-gray-700 dark:text-gray-300 italic">
            <MarkdownRenderer content={identity.i_am_statement} />
          </div>
        </div>
      )}
    </div>
  );
};

export const IAmStatementsSummaryComponent: React.FC<{
  coachMessage: React.ReactNode;
  config: ComponentConfig;
  onSendUserMessageToCoach: (request: CoachRequest) => void;
  disabled: boolean;
}> = ({ coachMessage, config, onSendUserMessageToCoach, disabled }) => {
  const identities = (config.identities || []) as ComponentIdentity[];
  const hasButtons = config.buttons && config.buttons.length > 0;
  const { downloadPdf, isDownloading } = useDownloadIAmPdf();

  return (
    <div
      className={`_IAmStatementsSummaryComponent mb-4 p-4 rounded-xl ${
        hasButtons ? "w-fit max-w-[100%]" : "w-fit max-w-[75%]"
      } leading-[1.5] shadow-sm animate-fadeIn break-words mr-auto bg-gold-200 dark:bg-transparent dark:border dark:border-gold-600 dark:text-gold-200`}
    >
      <div className="mb-4">
        {React.isValidElement(coachMessage) ? (
          coachMessage
        ) : (
          <MarkdownRenderer content={String(coachMessage)} />
        )}
      </div>

      {identities.length > 0 && (
        <div className="mb-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {identities.map((identity) => (
              <IdentityCard key={identity.id} identity={identity} />
            ))}
          </div>
        </div>
      )}

      <div className="_IAmStatementsSummaryButtons mt-4 flex flex-wrap gap-2 justify-end">
        {/* Download PDF button */}
        <button
          onClick={() => {
            log.debug("Download PDF button clicked");
            downloadPdf();
          }}
          disabled={disabled || isDownloading}
          className="px-4 py-2 text-sm font-medium rounded-md bg-white/50 hover:bg-white/70 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-600 transition-colors cursor-pointer flex items-center gap-2"
        >
          <FiDownload className="w-4 h-4" />
          {isDownloading ? "Downloading..." : "Download PDF"}
        </button>

        {/* Dynamic buttons from config */}
        {config.buttons &&
          config.buttons.map((button, index) => (
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
              className="px-4 py-2 text-sm font-medium rounded-md bg-gold-500 hover:bg-gold-600 text-black transition-colors cursor-pointer"
            >
              {button.label}
            </button>
          ))}
      </div>
    </div>
  );
};
