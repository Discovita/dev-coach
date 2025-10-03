import React from "react";
import { ComponentConfig, ComponentText } from "@/types/componentConfig";
import MarkdownRenderer from "@/utils/MarkdownRenderer";
import { CoachRequest } from "@/types/coachRequest";

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
          warmupBefore.map((t) => t.text).filter(Boolean).join("\n\n"),
          originalContent,
          warmupAfter.map((t) => t.text).filter(Boolean).join("\n\n"),
        ]
          .filter((s) => s && s.trim().length > 0)
          .join("\n\n")
      : null;

  return (
    <div className="max-w-[75%]">
      {mergedMarkdown ? <MarkdownRenderer content={mergedMarkdown} /> : children}
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
            <MarkdownRenderer key={`before-${t.source}-${idx}`} content={t.text} />
          ))}
        </div>
      )}
      
      {afterTexts.length > 0 && (
        <div className="max-w-[75%] space-y-2 mt-2">
          {afterTexts.map((t, idx) => (
            <MarkdownRenderer key={`after-${t.source}-${idx}`} content={t.text} />
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
  textsBySource: Record<string, ComponentText[]>;
  children: React.ReactNode;
}> = ({ textsBySource, children }) => {
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
        <StandardTextRenderer texts={standardTexts.filter((t) => t.location === "before")} />
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
        <StandardTextRenderer texts={standardTexts.filter((t) => t.location === "after")} />
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

  return (
    <div className="_CoachMessageWithComponent mb-4 p-3.5 pr-4 pl-4 rounded-t-[18px] rounded-br-[18px] rounded-bl-[6px] w-fit max-w-[100%] leading-[1.5] shadow-sm animate-fadeIn break-words mr-auto bg-gold-200 border-l-[3px] border-l-gold-600 dark:bg-transparent dark:border-r-[1px] dark:border-r-gold-600 dark:border-t-[1px] dark:border-t-gold-600 dark:border-b-[1px] dark:border-b-gold-600 dark:text-gold-200">
      <ContentRenderer textsBySource={textsBySource}>
        {children}
      </ContentRenderer>

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