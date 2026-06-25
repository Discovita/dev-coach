import type {
	MeditationAsset,
	MeditationAssetKind,
} from "@/api/adminMeditations";

/** Human-friendly label from an ENUM_VALUE. */
export function formatStatus(value: string): string {
	return value
		.toLowerCase()
		.replace(/_/g, " ")
		.replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Badge variant for a meditation/asset status. */
export function statusVariant(
	status: string,
): "default" | "secondary" | "outline" | "destructive" {
	if (status === "FAILED") return "destructive";
	if (status === "COMPLETE" || status === "READY") return "default";
	if (status === "READY_FOR_QC") return "secondary";
	return "outline";
}

/** Assets of one kind, newest version first. */
export function assetsOfKind(
	assets: MeditationAsset[],
	kind: MeditationAssetKind,
): MeditationAsset[] {
	return assets
		.filter((a) => a.kind === kind)
		.sort((a, b) => b.version - a.version);
}

export const MEDITATION_STATUSES = [
	"PENDING",
	"GENERATING_PARTS",
	"READY_FOR_QC",
	"ASSEMBLING",
	"COMPLETE",
	"FAILED",
] as const;
