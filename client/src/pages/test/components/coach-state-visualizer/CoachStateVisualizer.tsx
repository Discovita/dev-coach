import React, { useState, useEffect, useRef } from 'react';
import { CoachStateVisualizerProps, TabName, TabUpdateStatus, ExtractedActions } from './types';
import {
  extractActions,
  renderTabContent,
  getDefaultExpandedSections,
  getTabsConfig,
  detectAllTabChanges,
} from './utils';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { motion } from 'framer-motion';

export const CoachStateVisualizer: React.FC<CoachStateVisualizerProps> = ({
  coachState,
  lastResponse,
}) => {
  const [activeTab, setActiveTab] = useState<TabName>(TabName.STATE);
  const [expandedSections, setExpandedSections] = useState(getDefaultExpandedSections());
  const [tabUpdates, setTabUpdates] = useState<TabUpdateStatus>({});
  const prevStateRef = useRef<null | typeof coachState>(null);
  const prevResponseRef = useRef<undefined | typeof lastResponse>(undefined);
  const prevActionsRef = useRef<null | ExtractedActions>(null);
  const extractedActionsRef = useRef<ExtractedActions>(extractActions(coachState, lastResponse));
  const tabsConfig = getTabsConfig();

  // Toggle section expansion
  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  // Handle tab click - change active tab and clear update indicator
  const handleTabClick = (tabName: TabName) => {
    setActiveTab(tabName);
    // Clear update indicator for this tab
    if (tabUpdates[tabName]) {
      setTabUpdates(prev => {
        const newUpdates = { ...prev };
        newUpdates[tabName] = false;
        return newUpdates;
      });
    }
  };

  // Detect changes in data when state or response updates
  useEffect(() => {
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
    Object.values(updates).forEach(value => {
      if (value === true) hasAnyUpdates = true;
    });
    if (hasAnyUpdates) {
      setTabUpdates(prev => ({
        ...prev,
        ...updates,
      }));
    }
    // Store current values for next comparison
    prevStateRef.current = coachState;
    prevResponseRef.current = lastResponse;
    prevActionsRef.current = currentActions;
  }, [coachState, lastResponse, activeTab]);

  return (
    <div className="_CoachStateVisualizer flex flex-col h-full w-full max-h-screen rounded-none dark:rounded-none shadow-gold-md overflow-hidden dark:bg-[#333333] dark:border-none">
      <Tabs
        value={activeTab}
        onValueChange={v => handleTabClick(v as TabName)}
        className="flex flex-col h-full"
      >
        <TabsList className="border-b-2 bg-gold-200 border-gold-500 flex gap-2 w-full dark:text-gold-50">
          {tabsConfig.map(tab => (
            <TabsTrigger
              key={tab.name}
              value={tab.name}
              className={
                'relative whitespace-nowrap px-4 py-3 font-medium transition-all' +
                (tabUpdates[tab.name] ? ' font-semibold text-gold-700' : '')
              }
            >
              {tab.label}
              {/* Tab update indicator using Framer Motion for pulse animation */}
              {tabUpdates[tab.name] && (
                <motion.span
                  className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#e74c3c]"
                  initial={{ scale: 0.9, boxShadow: '0 0 0 0 rgba(231,76,60,0.7)' }}
                  animate={{
                    scale: [0.9, 1.1, 0.9],
                    boxShadow: [
                      '0 0 0 0 rgba(231,76,60,0.7)',
                      '0 0 0 5px rgba(231,76,60,0)',
                      '0 0 0 0 rgba(231,76,60,0)',
                    ],
                  }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
                />
              )}
            </TabsTrigger>
          ))}
        </TabsList>
        {tabsConfig.map(tab => (
          <TabsContent
            key={tab.name}
            value={tab.name}
            className="flex-1 overflow-y-auto p-4 scrollbar"
          >
            {activeTab === tab.name &&
              renderTabContent(
                tab.name as TabName,
                coachState,
                lastResponse,
                expandedSections,
                toggleSection,
                extractedActionsRef.current
              )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
};
