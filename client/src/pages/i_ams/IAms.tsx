import { useIdentities } from "@/hooks/use-identities";
import type { Identity } from "@/types/identity";
import { getArticle } from "@/utils/getArticle";
import {
	DndContext,
	type DragEndEvent,
	KeyboardSensor,
	PointerSensor,
	closestCenter,
	useSensor,
	useSensors,
} from "@dnd-kit/core";
import {
	SortableContext,
	arrayMove,
	rectSortingStrategy,
	sortableKeyboardCoordinates,
	useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Link } from "@tanstack/react-router";
import { GripVertical } from "lucide-react";
import { useEffect, useState } from "react";

/**
 * I Am's Page
 *
 * Purpose:
 * - Displays the user's identities in a grid layout
 * - Drag-to-reorder: grab a card's handle to change the display order. The
 *   order persists and applies to both /iams and /identities. Works for the
 *   logged-in user and for an admin impersonating a test user (the hook routes
 *   to the regular or admin reorder endpoint accordingly).
 *
 * Smoothness: the grid renders from local `items` state that we reorder
 * synchronously on drop, so dnd-kit animates into place without waiting on the
 * (background) persistence request. The cache write/refetch that follows keeps
 * the same order, so it never re-shuffles the cards mid-animation.
 */

const DEFAULT_I_AM_STATEMENT =
	"This identity doesn't have an I Am statement yet. Continue coaching to craft one.";

/**
 * A single draggable I Am card. The card itself remains a Link to the detail
 * page; only the grip handle initiates a drag, so clicking the card still
 * navigates as before.
 */
function SortableIAmCard({ identity }: { identity: Identity }) {
	const {
		attributes,
		listeners,
		setNodeRef,
		transform,
		transition,
		isDragging,
	} = useSortable({ id: identity.id ?? "" });

	const style = {
		transform: CSS.Transform.toString(transform),
		transition,
		zIndex: isDragging ? 20 : undefined,
	};

	return (
		<div
			ref={setNodeRef}
			style={style}
			className={`group/card relative ${isDragging ? "opacity-90" : ""}`}
		>
			<button
				type="button"
				aria-label="Drag to reorder"
				title="Drag to reorder"
				className="absolute top-2.5 right-2.5 z-10 grid h-7 w-7 cursor-grab touch-none place-items-center rounded-lg border border-white/20 bg-black/45 text-white shadow-md backdrop-blur-md transition-all duration-200 hover:scale-105 hover:bg-black/65 active:scale-95 active:cursor-grabbing focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/80 opacity-100 md:opacity-0 md:group-hover/card:opacity-100 md:focus-visible:opacity-100"
				{...attributes}
				{...listeners}
			>
				<GripVertical className="h-[14px] w-[14px]" />
			</button>
			<Link
				to="/identities/$identityId"
				params={{ identityId: identity.id ?? "" }}
				className="flex flex-col gap-[24px] cursor-pointer group"
			>
				{/* Image Card */}
				<div className="relative overflow-hidden rounded-[16px] shadow-[0px_1px_4px_0px_rgba(30,30,30,0.25)] w-full aspect-video bg-muted flex items-center justify-center group-hover:shadow-[0px_4px_12px_0px_rgba(30,30,30,0.3)] transition-shadow">
					{identity.image?.large ? (
						<img
							src={identity.image.large}
							alt={identity.name}
							className="w-full h-full object-cover"
						/>
					) : (
						<div className="text-center p-4">
							<p className="text-sm text-muted-foreground">Image coming soon</p>
						</div>
					)}
				</div>

				{/* Identity Name and Description */}
				<div className="flex flex-col gap-[8px] leading-none text-[#1e1e1e]">
					<h2 className="text-[20px] md:text-[24px] font-semibold group-hover:text-[color:var(--nv-violet-blue)] transition-colors">
						I am {getArticle(identity.name)} {identity.name}
					</h2>
					<p className="text-[14px] md:text-[16px] font-normal">
						{identity.i_am_statement || DEFAULT_I_AM_STATEMENT}
					</p>
				</div>
			</Link>
		</div>
	);
}

export default function IAms() {
	const { identities, isLoading, isError, reorderIdentities } = useIdentities();

	// Local copy that drives the grid so a drop reorders instantly (smooth
	// dnd-kit animation) without waiting on the network. We only adopt the
	// server list when its order actually differs from what we're showing, so
	// the post-drop cache write/refetch doesn't re-render the cards into place.
	const [items, setItems] = useState<Identity[]>(identities ?? []);
	useEffect(() => {
		if (!identities) return;
		setItems((prev) => {
			const sameOrder =
				prev.length === identities.length &&
				prev.every((p, idx) => p.id === identities[idx].id);
			return sameOrder ? prev : identities;
		});
	}, [identities]);

	const sensors = useSensors(
		useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
		useSensor(KeyboardSensor, {
			coordinateGetter: sortableKeyboardCoordinates,
		}),
	);

	if (isLoading) {
		return <div className="text-muted-foreground">Loading identities...</div>;
	}

	if (isError) {
		return (
			<div className="text-destructive">
				Failed to load identities. Please try again.
			</div>
		);
	}

	if (!identities || identities.length === 0) {
		return (
			<div className="text-muted-foreground">
				No identities found. Create your first identity to get started.
			</div>
		);
	}

	const ids = items.map((identity) => identity.id ?? "");

	const handleDragEnd = (event: DragEndEvent) => {
		const { active, over } = event;
		if (!over || active.id === over.id) return;

		const oldIndex = ids.indexOf(String(active.id));
		const newIndex = ids.indexOf(String(over.id));
		if (oldIndex === -1 || newIndex === -1) return;

		// Reorder locally first (instant + smooth), then persist in the background.
		const reordered = arrayMove(items, oldIndex, newIndex);
		setItems(reordered);
		reorderIdentities(reordered.map((identity) => identity.id ?? ""));
	};

	return (
		<div className="flex flex-col gap-[32px] bg-white">
			<DndContext
				sensors={sensors}
				collisionDetection={closestCenter}
				onDragEnd={handleDragEnd}
			>
				<SortableContext items={ids} strategy={rectSortingStrategy}>
					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[32px]">
						{items.map((identity: Identity, index: number) => (
							<SortableIAmCard
								key={identity.id || `identity-${index}`}
								identity={identity}
							/>
						))}
					</div>
				</SortableContext>
			</DndContext>
		</div>
	);
}
