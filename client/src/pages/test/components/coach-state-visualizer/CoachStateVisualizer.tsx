import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useActions } from "@/hooks/use-actions";
import { useChatMessages } from "@/hooks/use-chat-messages";
import { useCoachState } from "@/hooks/use-coach-state";
import { useFinalPrompt } from "@/hooks/use-final-prompt";
import { useIdentities } from "@/hooks/use-identities";
import { usePrevious } from "@/hooks/use-previous";
import { motion } from "framer-motion";
import type React from "react";
import { useMemo, useState } from "react";
import { TabName } from "./types";
import { getDefaultExpandedSections, getTabsConfig } from "./utils";
import { TabContent } from "./utils/tabContentFactory";

export const CoachStateVisualizer: React.FC = () => {
	const {
		coachState,
		isLoading: isCoachStateLoading,
		isError: isCoachStateError,
	} = useCoachState();
	const { chatMessages } = useChatMessages();
	useIdentities();
	const finalPrompt = useFinalPrompt();
	const {
		actions,
		isLoading: isActionsLoading,
		isError: isActionsError,
	} = useActions();

	const [activeTab, setActiveTab] = useState<TabName>(TabName.STATE);
	const [expandedSections, setExpandedSections] = useState(
		getDefaultExpandedSections(),
	);
	const [visitedTabs, setVisitedTabs] = useState<Set<TabName>>(new Set());

	const prevCoachState = usePrevious(coachState);
	const prevFinalPrompt = usePrevious(finalPrompt);
	const prevActions = usePrevious(actions);
	const prevChatMessages = usePrevious(chatMessages);

	const tabsConfig = getTabsConfig();

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
			<div className="p-4 text-muted-foreground">No coach state available.</div>
		);
	}

	const toggleSection = (section: string) => {
		setExpandedSections((prev) => ({
			...prev,
			[section]: !prev[section],
		}));
	};

	return (
		<div className="_CoachStateVisualizer flex flex-col h-full w-full max-h-screen rounded-none shadow-md overflow-hidden dark:bg-neutral-800">
			<Tabs
				value={activeTab}
				onValueChange={(v) => handleTabClick(v as TabName)}
				className="flex flex-col h-full"
			>
				<TabsList className="border-b-2 bg-muted border-border flex gap-2 w-full">
					{tabsConfig.map((tab) => (
						<TabsTrigger
							key={tab.name}
							value={tab.name}
							className={`relative whitespace-nowrap px-4 py-3 font-medium transition-all${tabUpdates[tab.name] ? " font-semibold text-primary" : ""}`}
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
										repeat: Number.POSITIVE_INFINITY,
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
