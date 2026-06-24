export type NavItem = {
	to: string; // The route to navigate to
	label: string; // The label to display for the nav item
	icon: string; // The icon to display for the nav item
	locked?: boolean; // When true, the item shows a lock badge and is not navigable
};
