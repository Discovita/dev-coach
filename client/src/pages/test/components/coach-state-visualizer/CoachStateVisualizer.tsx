import React, { useState, useEffect, useRef } from "react";
import { TabName, TabUpdateStatus, ExtractedActions } from "./types";
import {
  extractActions,
  getDefaultExpandedSections,
  getTabsConfig,
  detectAllTabChanges,
} from "./utils";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import { useCoachState } from "@/hooks/use-coach-state";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useIdentities } from "@/hooks/use-identities";
import { CoachResponse } from "@/types/coachResponse";
import { TabContent } from "./utils/tabContentFactory";

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
 * 6. Maintain tab, section, and update state as before.
 */
export const CoachStateVisualizer: React.FC = () => {
  // 1. Fetch coach state
  const {
    coachState,
    isLoading: isCoachStateLoading,
    isError: isCoachStateError,
  } = useCoachState();
  // 2. Fetch chat messages (and last response)
  // chatMessages is not used directly yet, but hook is called for future extensibility
  const { isLoading: isMessagesLoading, isError: isMessagesError } =
    useChatMessages();
  // 3. Fetch identities (optional, for extensibility)
  // identities is not used directly yet, but hook is called for future extensibility
  const { isLoading: isIdentitiesLoading, isError: isIdentitiesError } =
    useIdentities();

  // 6. Maintain tab, section, and update state as before (hooks must be called unconditionally)
  const [activeTab, setActiveTab] = useState<TabName>(TabName.STATE);
  const [expandedSections, setExpandedSections] = useState(
    getDefaultExpandedSections()
  );
  const [tabUpdates, setTabUpdates] = useState<TabUpdateStatus>({});
  const prevStateRef = useRef<null | typeof coachState>(null);
  const prevResponseRef = useRef<CoachResponse | undefined>(undefined);
  const prevActionsRef = useRef<null | ExtractedActions>(null);
  const extractedActionsRef = useRef<ExtractedActions>(
    extractActions(coachState, undefined)
  );
  const tabsConfig = getTabsConfig();

  // 5. Extract the latest CoachResponse from chatMessages if available
  // (Assume the last message in chatMessages is the latest response, or adapt as needed)
  // If you have a dedicated lastResponse, use that instead.
  const lastResponse = undefined;
  // Example for future: if (chatMessages && Array.isArray(chatMessages) && chatMessages.length > 0) { ... }

  // Detect changes in data when state or response updates
  // This hook must be called unconditionally, so we guard inside if data is missing
  useEffect(() => {
    if (!coachState) return; // Guard: skip effect if coachState is not available
    // Extract current actions
    const currentActions = extractActions(coachState, lastResponse);
    extractedActionsRef.current = currentActions;
    // Skip first render
    if (prevStateRef.current === null) {
      prevStateRef.current = coachState;
      prevResponseRef.current = lastResponse;
      prevActionsRef.current = currentActions;
      return;
    }
    // Detect changes in each tab's data
    const updates = detectAllTabChanges(
      prevStateRef.current,
      coachState,
      prevResponseRef.current,
      lastResponse,
      prevActionsRef.current,
      currentActions,
      activeTab
    );
    // Only update state if there are actual changes
    let hasAnyUpdates = false;
    Object.values(updates).forEach((value) => {
      if (value === true) hasAnyUpdates = true;
    });
    if (hasAnyUpdates) {
      setTabUpdates((prev) => ({
        ...prev,
        ...updates,
      }));
    }
    // Store current values for next comparison
    prevStateRef.current = coachState;
    prevResponseRef.current = lastResponse;
    prevActionsRef.current = currentActions;
  }, [coachState, lastResponse, activeTab]);

  // 4. Handle loading and error states
  const isLoading =
    isCoachStateLoading || isMessagesLoading || isIdentitiesLoading;
  const isError = isCoachStateError || isMessagesError || isIdentitiesError;
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

  // Handle tab click - change active tab and clear update indicator
  const handleTabClick = (tabName: TabName) => {
    setActiveTab(tabName);
    if (tabUpdates[tabName]) {
      setTabUpdates((prev) => {
        const newUpdates = { ...prev };
        newUpdates[tabName] = false;
        return newUpdates;
      });
    }
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
