import React, { useState, useMemo, useEffect } from "react";
import { TabName } from "./types";
import { getDefaultExpandedSections, getTabsConfig } from "./utils";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import { TabContent } from "./utils/tabContentFactory";
import { usePrevious } from "@/hooks/use-previous";
import { useCoachState } from "@/hooks/use-coach-state";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useIdentities } from "@/hooks/use-identities";
import { useFinalPrompt } from "@/hooks/use-final-prompt";
import { useActions } from "@/hooks/use-actions";

/**
 * CoachStateVisualizer component (self-fetching version)
 * Fetches all required data using hooks and visualizes the coach state.
 * Now uses TabContent component for tab rendering.
 *
 * Step-by-step:
 * 1. Fetch coach state using useCoachState.
 * 2. Fetch chat messages (and last response) using useChatMessages.
 * 3. Fetch identities using useIdentities (for extensibility).
 * 4. Handle loading and error states for all hooks.
 * 5. Use the fetched coachState and latest response for visualization.
 * 6. Maintain tab, section, and update state as before, but now use robust cache-driven tab update notification logic.
 */
export const CoachStateVisualizer: React.FC = () => {
  // Fetch data
  const {
    coachState,
    isLoading: isCoachStateLoading,
    isError: isCoachStateError,
  } = useCoachState();
  const { chatMessages } = useChatMessages();
  useIdentities(); // Not used directly, but ensures cache is up to date
  const finalPrompt = useFinalPrompt();
  const {
    actions,
    isLoading: isActionsLoading,
    isError: isActionsError,
  } = useActions();

  useEffect(() => {
    if (actions) {
      console.log("[CoachStateVisualizer] Actions: ", actions);
    }
  });

  // State
  const [activeTab, setActiveTab] = useState<TabName>(TabName.STATE);
  const [expandedSections, setExpandedSections] = useState(
    getDefaultExpandedSections()
  );
  const [visitedTabs, setVisitedTabs] = useState<Set<TabName>>(new Set());

  // Get previous values
  const prevCoachState = usePrevious(coachState);
  const prevFinalPrompt = usePrevious(finalPrompt);
  const prevActions = usePrevious(actions);
  const prevChatMessages = usePrevious(chatMessages);

  const tabsConfig = getTabsConfig();

  // Calculate tab updates
  const tabUpdates = useMemo(() => {
    const updates: Record<TabName, boolean> = {
      [TabName.STATE]: false,
      [TabName.PROMPT]: false,
      [TabName.ACTIONS]: false,
      [TabName.IDENTITIES]: false,
      [TabName.CONVERSATION]: false,
    };

    if (visitedTabs.has(TabName.STATE) && prevCoachState && coachState) {
      updates[TabName.STATE] =
        JSON.stringify(prevCoachState) !== JSON.stringify(coachState);
    }

    if (visitedTabs.has(TabName.PROMPT) && prevFinalPrompt !== undefined) {
      updates[TabName.PROMPT] = prevFinalPrompt !== finalPrompt;
    }

    if (visitedTabs.has(TabName.ACTIONS) && prevActions) {
      updates[TabName.ACTIONS] =
        JSON.stringify(prevActions) !== JSON.stringify(actions);
    }

    if (visitedTabs.has(TabName.IDENTITIES) && prevCoachState && coachState) {
      updates[TabName.IDENTITIES] =
        JSON.stringify(prevCoachState) !== JSON.stringify(coachState);
    }

    if (visitedTabs.has(TabName.CONVERSATION) && prevChatMessages) {
      updates[TabName.CONVERSATION] =
        JSON.stringify(prevChatMessages) !== JSON.stringify(chatMessages);
    }

    return updates;
  }, [
    coachState,
    prevCoachState,
    finalPrompt,
    prevFinalPrompt,
    actions,
    prevActions,
    chatMessages,
    prevChatMessages,
    visitedTabs,
  ]);

  const handleTabClick = (tabName: TabName) => {
    setVisitedTabs((prev) => new Set(prev).add(tabName));
    setActiveTab(tabName);
  };

  // Handle loading and error states
  const isLoading = isCoachStateLoading || isActionsLoading;
  const isError = isCoachStateError || isActionsError;

  if (isLoading) {
    return <div className="p-4">Loading coach state...</div>;
  }

  if (isError) {
    return (
      <div className="p-4 text-red-700">
        Error loading coach state or related data.
      </div>
    );
  }

  if (!coachState) {
    return (
      <div className="p-4 text-neutral-500">No coach state available.</div>
    );
  }

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  return (
    <div className="_CoachStateVisualizer flex flex-col h-full w-full max-h-screen rounded-none dark:rounded-none shadow-gold-md overflow-hidden dark:bg-[#333333] dark:border-none">
      <Tabs
        value={activeTab}
        onValueChange={(v) => handleTabClick(v as TabName)}
        className="flex flex-col h-full"
      >
        <TabsList className="border-b-2 bg-gold-200 border-gold-500 flex gap-2 w-full dark:text-gold-50">
          {tabsConfig.map((tab) => (
            <TabsTrigger
              key={tab.name}
              value={tab.name}
              className={
                "relative whitespace-nowrap px-4 py-3 font-medium transition-all" +
                (tabUpdates[tab.name] ? " font-semibold text-gold-700" : "")
              }
            >
              {tab.label}
              {tabUpdates[tab.name] && (
                <motion.span
                  className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#e74c3c]"
                  initial={{
                    scale: 0.9,
                    boxShadow: "0 0 0 0 rgba(231,76,60,0.7)",
                  }}
                  animate={{
                    scale: [0.9, 1.1, 0.9],
                    boxShadow: [
                      "0 0 0 0 rgba(231,76,60,0.7)",
                      "0 0 0 5px rgba(231,76,60,0)",
                      "0 0 0 0 rgba(231,76,60,0)",
                    ],
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                />
              )}
            </TabsTrigger>
          ))}
        </TabsList>
        {tabsConfig.map((tab) => (
          <TabsContent
            key={tab.name}
            value={tab.name}
            className="flex-1 overflow-y-auto p-4 scrollbar"
          >
            {activeTab === tab.name && (
              <TabContent
                tabName={tab.name as TabName}
                expandedSections={expandedSections}
                toggleSection={toggleSection}
              />
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
};