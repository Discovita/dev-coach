import React, { useRef, useState, useEffect } from "react";
import { TabName } from "./types";
import { getDefaultExpandedSections, getTabsConfig } from "./utils";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import { useCoachState } from "@/hooks/use-coach-state";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useIdentities } from "@/hooks/use-identities";
import { useFinalPrompt } from "@/hooks/use-final-prompt";
import { useActions } from "@/hooks/use-actions";
import { TabContent } from "./utils/tabContentFactory";
import { CoachState } from "@/types/coachState";
import { Action } from "@/types/action";
import { Message } from "@/types/message";

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
  // 1. Fetch coach state
  const {
    coachState,
    isLoading: isCoachStateLoading,
    isError: isCoachStateError,
  } = useCoachState();
  // 2. Fetch chat messages (and last response)
  const { chatMessages } = useChatMessages();
  // 3. Fetch identities (optional, for extensibility)
  useIdentities(); // Not used directly, but ensures cache is up to date
  // Fetch final prompt
  const finalPrompt = useFinalPrompt();
  // Fetch actions
  const actions = useActions();

  // 6. Maintain tab and section state as before
  const [activeTab, setActiveTab] = useState<TabName>(TabName.STATE);
  const [expandedSections, setExpandedSections] = useState(
    getDefaultExpandedSections()
  );
  const tabsConfig = getTabsConfig();

  // --- Robust cache-driven tab update notification logic ---
  // Store the last seen value for each tab
  const lastSeen = useRef<{
    [TabName.STATE]: CoachState | null;
    [TabName.PROMPT]: string | undefined;
    [TabName.ACTIONS]: Action[];
    [TabName.IDENTITIES]: CoachState | null;
    [TabName.CONVERSATION]: Message[];
  }>({
    [TabName.STATE]: coachState ?? null,
    [TabName.PROMPT]: finalPrompt,
    [TabName.ACTIONS]: actions,
    [TabName.IDENTITIES]: coachState ?? null,
    [TabName.CONVERSATION]: chatMessages,
  });

  // Store the update flag for each tab
  const [tabUpdates, setTabUpdates] = useState<Record<TabName, boolean>>({
    [TabName.STATE]: false,
    [TabName.PROMPT]: false,
    [TabName.ACTIONS]: false,
    [TabName.IDENTITIES]: false,
    [TabName.CONVERSATION]: false,
  });

  // On every cache change, compare the current value to the last seen value for each tab
  useEffect(() => {
    // Debug logging: log current and last seen values for each tab
    console.log("[TabUpdate] Current values:", {
      state: coachState,
      prompt: finalPrompt,
      actions: actions,
      identities: coachState,
      conversation: chatMessages,
    });
    console.log("[TabUpdate] Last seen values:", {
      state: lastSeen.current[TabName.STATE],
      prompt: lastSeen.current[TabName.PROMPT],
      actions: lastSeen.current[TabName.ACTIONS],
      identities: lastSeen.current[TabName.IDENTITIES],
      conversation: lastSeen.current[TabName.CONVERSATION],
    });

    // Compute change detection for each tab and log the result
    const stateChanged = !!(
      lastSeen.current[TabName.STATE] &&
      coachState &&
      JSON.stringify(lastSeen.current[TabName.STATE]) !== JSON.stringify(coachState)
    );
    const promptChanged = lastSeen.current[TabName.PROMPT] !== finalPrompt;
    const actionsChanged = JSON.stringify(lastSeen.current[TabName.ACTIONS]) !== JSON.stringify(actions);
    const identitiesChanged = !!(
      lastSeen.current[TabName.IDENTITIES] &&
      coachState &&
      JSON.stringify(lastSeen.current[TabName.IDENTITIES]) !== JSON.stringify(coachState)
    );
    const conversationChanged = JSON.stringify(lastSeen.current[TabName.CONVERSATION]) !== JSON.stringify(chatMessages);

    console.log("[TabUpdate] Change detection results:", {
      stateChanged,
      promptChanged,
      actionsChanged,
      identitiesChanged,
      conversationChanged,
    });

    setTabUpdates((prev) => ({
      ...prev,
      [TabName.STATE]: stateChanged,
      [TabName.PROMPT]: promptChanged,
      [TabName.ACTIONS]: actionsChanged,
      [TabName.IDENTITIES]: identitiesChanged,
      [TabName.CONVERSATION]: conversationChanged,
    }));

    // Log the computed tabUpdates object after each cache change
    setTimeout(() => {
      // Use setTimeout to ensure this logs after state update
      console.log("[TabUpdate] tabUpdates (after setState):", {
        state: stateChanged,
        prompt: promptChanged,
        actions: actionsChanged,
        identities: identitiesChanged,
        conversation: conversationChanged,
      });
    }, 0);
  }, [coachState, finalPrompt, actions, chatMessages]);

  // When the user visits a tab, update the last seen value for that tab and clear the update flag
  const handleTabClick = (tabName: TabName) => {
    switch (tabName) {
      case TabName.STATE:
        lastSeen.current[TabName.STATE] = coachState ?? null;
        break;
      case TabName.PROMPT:
        lastSeen.current[TabName.PROMPT] = finalPrompt;
        break;
      case TabName.ACTIONS:
        lastSeen.current[TabName.ACTIONS] = actions;
        break;
      case TabName.IDENTITIES:
        lastSeen.current[TabName.IDENTITIES] = coachState ?? null;
        break;
      case TabName.CONVERSATION:
        lastSeen.current[TabName.CONVERSATION] = chatMessages;
        break;
    }
    setTabUpdates((prev) => ({ ...prev, [tabName]: false }));
    setActiveTab(tabName);
  };

  // 4. Handle loading and error states
  const isLoading = isCoachStateLoading;
  const isError = isCoachStateError;
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

  // Toggle section expansion
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
              {/* Tab update indicator using Framer Motion for pulse animation */}
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
