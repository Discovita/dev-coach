import { Button } from "@/components/ui/button";
import {
	Select,
	SelectContent,
	SelectGroup,
	SelectItem,
	SelectLabel,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import {
	getIdentityCategoryColor,
	getIdentityCategoryDisplayName,
	getIdentityCategoryIcon,
} from "@/enums/identityCategory";
import { useIdentities } from "@/hooks/use-identities";
import type { Identity } from "@/types/identity";
import { CheckCircle2, CircleDashed, Download } from "lucide-react";
import { toast } from "sonner";

interface IdentitySelectorProps {
	selectedIdentityId: string | null;
	onIdentitySelect: (identityId: string | null) => void;
	/**
	 * Whether to show the large "selected identity" details card under the selector.
	 *
	 * This exists because some screens (like the Image Generation "studio" layout)
	 * want to keep the selector compact and show identity context elsewhere.
	 *
	 * Defaults to true to preserve current behavior.
	 */
	showSelectedIdentityCard?: boolean;
}

/**
 * IdentitySelector Component
 * --------------------------
 * Allows selecting an identity from the current user's identities.
 * Displays identity details and current image when selected.
 */
export function IdentitySelector({
	selectedIdentityId,
	onIdentitySelect,
	showSelectedIdentityCard = true,
}: IdentitySelectorProps) {
	const { identities, isLoading } = useIdentities();

	/**
	 * Determine whether an identity already has an image saved.
	 *
	 * We consider an identity "complete" if any rendition URL is present.
	 * This matches the fallback strategy used elsewhere on the Images page.
	 */
	const identityHasImage = (identity: Identity): boolean => {
		return Boolean(
			identity.image?.large ||
				identity.image?.medium ||
				identity.image?.original ||
				identity.image?.thumbnail,
		);
	};

	const handleValueChange = (value: string) => {
		if (value === "none") {
			onIdentitySelect(null);
		} else {
			onIdentitySelect(value);
		}
	};

	const handleDownload = async () => {
		if (!selectedIdentity?.image?.original) {
			toast.error("No image available to download");
			return;
		}

		try {
			// Fetch the original image directly with CORS mode
			const response = await fetch(selectedIdentity.image.original, {
				mode: "cors",
				credentials: "omit",
			});
			if (!response.ok) {
				throw new Error("Failed to fetch image");
			}

			// Convert to blob
			const blob = await response.blob();

			// Create download link
			const url = URL.createObjectURL(blob);
			const link = document.createElement("a");
			link.href = url;
			link.download = `identity-image-${selectedIdentity.name || "identity"}-${Date.now()}.png`;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
			URL.revokeObjectURL(url);

			toast.success("Image downloaded successfully");
		} catch (error) {
			toast.error("Failed to download image");
			console.error("Download error:", error);
		}
	};

	if (isLoading) {
		return (
			<div className="text-[var(--nv-royal-purple)]/60">
				Loading identities...
			</div>
		);
	}

	if (!identities || identities.length === 0) {
		return (
			<div className="text-[var(--nv-royal-purple)]/60">
				No identities found. Create identities first through the AI Coach.
			</div>
		);
	}

	const selectedIdentity = identities.find(
		(id: Identity) => id.id === selectedIdentityId,
	);

	// Progress indicator: how many identities already have an image saved.
	const totalIdentityCount = identities.length;
	const identitiesWithImageCount = (identities as Identity[]).reduce(
		(count: number, identity: Identity) => {
			return count + (identityHasImage(identity) ? 1 : 0);
		},
		0,
	);

	/**
	 * Category badge UI used in the selector (dropdown + selected value).
	 * Mirrors the badge pattern used on the Identity page in
	 * `client/src/pages/identities/Identity.tsx`.
	 */
	const renderCategoryBadge = (category: string) => {
		const IconComponent = getIdentityCategoryIcon(String(category));
		const colorClasses = getIdentityCategoryColor(String(category));
		return (
			<span
				className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${colorClasses}`}
			>
				<IconComponent className="w-3 h-3" />
				<span>{getIdentityCategoryDisplayName(String(category))}</span>
			</span>
		);
	};

	return (
		<div className="flex flex-col gap-2">
			<div className="flex items-center justify-between gap-3">
				<label className="text-sm font-medium text-[var(--nv-indigo)]">
					Select Identity
				</label>
				<span className="text-xs text-[var(--nv-royal-purple)]/60">
					{identitiesWithImageCount} / {totalIdentityCount} have images
				</span>
			</div>
			<Select
				value={selectedIdentityId || "none"}
				onValueChange={handleValueChange}
			>
				<SelectTrigger className="w-full max-w-2xl h-12 text-base border-[var(--nv-royal-purple)]/30 focus:ring-[var(--nv-royal-purple)]">
					<SelectValue placeholder="Choose an identity">
						{selectedIdentity ? (
							<span className="flex items-center gap-3 w-full pr-4">
								<span className="truncate">{selectedIdentity.name}</span>
								{selectedIdentity.category ? (
									<span className="flex-shrink-0 ml-auto">
										{renderCategoryBadge(String(selectedIdentity.category))}
									</span>
								) : null}
							</span>
						) : (
							"Choose an identity"
						)}
					</SelectValue>
				</SelectTrigger>
				<SelectContent>
					<SelectGroup>
						<SelectLabel>Identities</SelectLabel>
						<SelectItem value="none">None (Select an identity)</SelectItem>
						{identities.map((identity: Identity) => (
							<SelectItem key={identity.id} value={identity.id || ""}>
								{/* 
                  Reserve space on the right for the Radix check indicator.
                  `SelectItem` uses `pr-8` + an absolutely positioned check at `right-2`.
                */}
								<div className="flex items-center gap-2 w-full pr-6">
									<span
										className="flex-shrink-0"
										aria-label={
											identityHasImage(identity)
												? "Identity has an image"
												: "Identity needs an image"
										}
										title={
											identityHasImage(identity) ? "Has image" : "Needs image"
										}
									>
										{identityHasImage(identity) ? (
											<CheckCircle2
												className="size-4"
												fill="var(--nv-royal-purple)"
												color="white"
											/>
										) : (
											<CircleDashed className="size-4 text-[var(--nv-royal-purple)]/40" />
										)}
									</span>
									<span className="truncate">{identity.name}</span>
									{identity.category ? (
										<span className="flex-shrink-0 ml-auto">
											{renderCategoryBadge(String(identity.category))}
										</span>
									) : null}
								</div>
							</SelectItem>
						))}
					</SelectGroup>
				</SelectContent>
			</Select>

			{selectedIdentity && showSelectedIdentityCard && (
				<div className="mt-4 p-6 bg-[var(--nv-pale-lavender)]/30 rounded-lg border border-[var(--nv-royal-purple)]/20">
					{/* Two-column layout: image on left, details on right */}
					<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
						{/* Left side: Image */}
						<div className="flex flex-col items-center w-full">
							{selectedIdentity.image?.original ||
							selectedIdentity.image?.large ||
							selectedIdentity.image?.medium ||
							selectedIdentity.image?.thumbnail ? (
								<>
									<img
										src={
											selectedIdentity.image.original ||
											selectedIdentity.image.large ||
											selectedIdentity.image.medium ||
											selectedIdentity.image.thumbnail
										}
										alt={`${selectedIdentity.name} identity`}
										className="w-full h-auto rounded-lg border border-[var(--nv-royal-purple)]/20"
										style={{
											minHeight: "300px",
											objectFit: "contain",
											backgroundColor: "var(--nv-lilac-white)",
										}}
									/>
									<p className="text-sm text-[var(--nv-royal-purple)]/60 mt-2">
										Current Image
									</p>
									<Button
										type="button"
										variant="outline"
										size="sm"
										onClick={handleDownload}
										className="mt-2 border-[var(--nv-royal-purple)]/30 text-[var(--nv-royal-purple)] hover:bg-[var(--nv-pale-lavender)]"
									>
										<Download className="size-4" />
										Download
									</Button>
								</>
							) : (
								<div className="w-full aspect-video bg-[var(--nv-lilac-white)] rounded-lg flex items-center justify-center min-h-[300px] border border-[var(--nv-royal-purple)]/20">
									<p className="text-[var(--nv-royal-purple)]/60 text-lg">
										No image generated yet
									</p>
								</div>
							)}
						</div>

						{/* Right side: Identity details */}
						<div className="flex flex-col justify-center">
							<h3 className="font-bold text-2xl mb-4 text-[var(--nv-indigo)]">
								{selectedIdentity.name}
							</h3>
							{selectedIdentity.category && (
								<p className="text-base text-[var(--nv-royal-purple)]/80 mb-4">
									<span className="font-semibold">Category:</span>{" "}
									{getIdentityCategoryDisplayName(
										String(selectedIdentity.category),
									)}
								</p>
							)}
							{selectedIdentity.i_am_statement && (
								<p className="text-base text-[var(--nv-royal-purple)]/80 mb-4">
									<span className="font-semibold">I Am:</span>{" "}
									{selectedIdentity.i_am_statement}
								</p>
							)}
							{selectedIdentity.visualization && (
								<p className="text-base text-[var(--nv-royal-purple)]/80">
									<span className="font-semibold">Visualization:</span>{" "}
									{selectedIdentity.visualization}
								</p>
							)}
						</div>
					</div>
				</div>
			)}
		</div>
	);
}
