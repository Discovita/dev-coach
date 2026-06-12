import {
	getIdentityCategoryColor,
	getIdentityCategoryDisplayName,
	getIdentityCategoryIcon,
} from "@/enums/identityCategory";

/**
 * Category badge rendered as a colored pill with the category's icon.
 *
 * Shared by the identity detail view and the edit-form category dropdown so
 * the dropdown options match the displayed badge exactly.
 *
 * Note on the icon classes: shadcn's Select trigger/item force any svg without
 * a `size-`/`text-` class to `size-4` / muted-foreground. `size-3 text-current`
 * opts out of both so the pill keeps its size and category color inside the
 * dropdown.
 */
export function CategoryPill({ category }: { category: string }) {
	const Icon = getIdentityCategoryIcon(category);
	const colorClasses = getIdentityCategoryColor(category);
	return (
		<span
			className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${colorClasses}`}
		>
			<Icon className="size-3 text-current" />
			<span>{getIdentityCategoryDisplayName(category)}</span>
		</span>
	);
}
