import React from "react";
import {
  ComponentConfig,
  ComponentText,
  ComponentIdentity,
} from "@/types/componentConfig";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import { CoachRequest } from "@/types/coachRequest";
import { getIdentityCategoryColor } from "@/enums/identityCategory";
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

/**
 * Maps identity categories to their corresponding icons
 */
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

  // Direct match first
  if (CATEGORY_ICON_MAP[normalizedCategory]) {
    return CATEGORY_ICON_MAP[normalizedCategory];
  }

  // Fallback to partial matching for flexibility
  for (const [key, icon] of Object.entries(CATEGORY_ICON_MAP)) {
    if (
      normalizedCategory.includes(key.split("_")[0]) ||
      key.split("_").some((part) => normalizedCategory.includes(part))
    ) {
      return icon;
    }
  }

  // Default fallback
  return FaUser;
};

/**
 * Renders a single identity as a badge
 */
const IdentityBadge: React.FC<{ identity: ComponentIdentity }> = ({
  identity,
}) => {
  const IconComponent = getCategoryIcon(identity.category);
  const colorClasses = getIdentityCategoryColor(identity.category);

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${colorClasses}`}
    >
      <IconComponent className="w-3 h-3" />
      <span className="font-medium">{identity.name}</span>
    </div>
  );
};

/**
 * Renders a list of identities as badges
 */
const IdentitiesRenderer: React.FC<{ identities: ComponentIdentity[] }> = ({
  identities,
}) => {
  if (!identities || identities.length === 0) {
    return null;
  }

  return (
    <div className="mb-3 p-3 bg-gold-50 dark:bg-gray-800 rounded-lg">
      <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Your Current Identities:
      </div>
      <div className="flex flex-wrap gap-2">
        {identities.map((identity) => (
          <IdentityBadge key={identity.id} identity={identity} />
        ))}
      </div>
    </div>
  );
};

export interface CoachMessageWithComponentProps {
  children: React.ReactNode;
  componentConfig: ComponentConfig;
  onSelect: (request: CoachRequest) => void;
  disabled: boolean;
}

/**
 * Separates texts by their source type for different rendering strategies
 */
const groupTextsBySource = (texts: ComponentText[]) => {
  const grouped: Record<string, ComponentText[]> = {};

  texts.forEach((text) => {
    const source = text.source || "default";
    if (!grouped[source]) {
      grouped[source] = [];
    }
    grouped[source].push(text);
  });

  return grouped;
};

/**
 * Handles warmup text merging with main content
 */
const WarmupTextRenderer: React.FC<{
  warmupTexts: ComponentText[];
  children: React.ReactNode;
}> = ({ warmupTexts, children }) => {
  const warmupBefore = warmupTexts.filter((t) => t.location === "before");
  const warmupAfter = warmupTexts.filter((t) => t.location === "after");

  const canMerge =
    React.isValidElement(children) &&
    (children as React.ReactElement).type === MarkdownRenderer;

  const originalContent: string | undefined = canMerge
    ? (children as React.ReactElement<{ content: string }>).props?.content
    : undefined;

  const mergedMarkdown =
    canMerge && typeof originalContent === "string"
      ? [
          warmupBefore
            .map((t) => t.text)
            .filter(Boolean)
            .join("\n\n"),
          originalContent,
          warmupAfter
            .map((t) => t.text)
            .filter(Boolean)
            .join("\n\n"),
        ]
          .filter((s) => s && s.trim().length > 0)
          .join("\n\n")
      : null;

  return (
    <div className="max-w-[75%]">
      {mergedMarkdown ? (
        <MarkdownRenderer content={mergedMarkdown} />
      ) : (
        children
      )}
    </div>
  );
};

/**
 * Handles standard text rendering (before/after main content)
 */
const StandardTextRenderer: React.FC<{
  texts: ComponentText[];
}> = ({ texts }) => {
  const beforeTexts = texts.filter((t) => t.location === "before");
  const afterTexts = texts.filter((t) => t.location === "after");

  return (
    <>
      {beforeTexts.length > 0 && (
        <div className="max-w-[75%] space-y-2">
          {beforeTexts.map((t, idx) => (
            <MarkdownRenderer
              key={`before-${t.source}-${idx}`}
              content={t.text}
            />
          ))}
        </div>
      )}

      {afterTexts.length > 0 && (
        <div className="max-w-[75%] space-y-2 mt-2">
          {afterTexts.map((t, idx) => (
            <MarkdownRenderer
              key={`after-${t.source}-${idx}`}
              content={t.text}
            />
          ))}
        </div>
      )}
    </>
  );
};

/**
 * Main content renderer that delegates to appropriate sub-renderers based on source type
 */
const ContentRenderer: React.FC<{
  // textsBySource: Record<string, ComponentText[]>; // Add this back in when we want to use it
  children: React.ReactNode;
}> = ({ children }) => {
  const textsBySource: Record<string, ComponentText[]> = {};
  const sources = Object.keys(textsBySource);

  // If no texts, just render children
  if (sources.length === 0) {
    return <div className="max-w-[75%]">{children}</div>;
  }

  const warmupTexts = textsBySource["warmup"] || [];
  const standardTexts = sources
    .filter((source) => source !== "warmup")
    .flatMap((source) => textsBySource[source]);

  return (
    <>
      {/* Render standard texts that go before */}
      {standardTexts.length > 0 && (
        <StandardTextRenderer
          texts={standardTexts.filter((t) => t.location === "before")}
        />
      )}

      {/* Main content - merge with warmup if applicable */}
      {warmupTexts.length > 0 ? (
        <WarmupTextRenderer warmupTexts={warmupTexts}>
          {children}
        </WarmupTextRenderer>
      ) : (
        <div className="max-w-[75%]">{children}</div>
      )}

      {/* Render standard texts that go after */}
      {standardTexts.length > 0 && (
        <StandardTextRenderer
          texts={standardTexts.filter((t) => t.location === "after")}
        />
      )}

      {/* 
        Future: Add more source-type specific renderers here
        Example:
        {textsBySource["quiz"] && <QuizRenderer texts={textsBySource["quiz"]} />}
        {textsBySource["reflection"] && <ReflectionRenderer texts={textsBySource["reflection"]} />}
      */}
    </>
  );
};

export const CoachMessageWithComponent: React.FC<
  CoachMessageWithComponentProps
> = ({ children, componentConfig, onSelect, disabled }) => {
  const allTexts = componentConfig.texts || [];
  const textsBySource = groupTextsBySource(allTexts);
  const identities = componentConfig.identities || [];
  const hasButtons =
    componentConfig.buttons && componentConfig.buttons.length > 0;

  return (
    <div
      className={`_CoachMessageWithComponent mb-4 p-3.5 pr-4 pl-4 rounded-t-[18px] rounded-br-[18px] rounded-bl-[6px] ${
        hasButtons ? "w-fit max-w-[100%]" : "w-fit max-w-[75%]"
      } leading-[1.5] shadow-sm animate-fadeIn break-words mr-auto bg-gold-200 border-l-[3px] border-l-gold-600 dark:bg-transparent dark:border-r-[1px] dark:border-r-gold-600 dark:border-t-[1px] dark:border-t-gold-600 dark:border-b-[1px] dark:border-b-gold-600 dark:text-gold-200`}
    >
      {/* Render identities if they exist */}
      {/* {identities.length > 0 && (
        <IdentitiesRenderer identities={identities} />
      )} */}

      {/* Temporary disable the textsBySource renderer */}
      {/* <ContentRenderer textsBySource={textsBySource}>
        {children}
      </ContentRenderer> */}
      <ContentRenderer>{children}</ContentRenderer>

      {/* Render component buttons if they exist */}
      {componentConfig.buttons && componentConfig.buttons.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2 justify-end">
          {componentConfig.buttons.map((button, index) => (
            <button
              key={index}
              onClick={() =>
                onSelect({ message: button.label, actions: button.actions })
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
