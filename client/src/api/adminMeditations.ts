import { COACH_BASE_URL } from "@/constants/api";
import { authFetch } from "@/utils/authFetch";

/**
 * Admin Meditations API
 * ---------------------
 * Admin-only endpoints driving the meditations QC pipeline.
 * Base: /api/v1/admin/meditations  (Permission: IsAdminUser)
 */

export type MeditationAssetKind = "VIDEO" | "AUDIO";

export type MeditationAssetStatus =
	| "QUEUED"
	| "GENERATING"
	| "READY"
	| "FAILED";

export type MeditationStatus =
	| "PENDING"
	| "GENERATING_PARTS"
	| "READY_FOR_QC"
	| "ASSEMBLING"
	| "COMPLETE"
	| "FAILED";

export interface MeditationAsset {
	id: string;
	kind: MeditationAssetKind;
	version: number;
	status: MeditationAssetStatus;
	is_active: boolean;
	s3_key: string;
	url: string | null;
	prompt_snapshot: string;
	error_code: string;
	created_at: string;
	updated_at: string;
}

export interface MeditationSegment {
	id: string;
	identity: string;
	identity_name: string | null;
	order: number;
	current_video_prompt: string;
	current_audio_script: string;
	assets: MeditationAsset[];
}

export interface MeditationDetail {
	id: string;
	user: string;
	user_email: string;
	status: MeditationStatus;
	final_video_s3_key: string;
	segments: MeditationSegment[];
	created_at: string;
	updated_at: string;
}

export interface MeditationListItem {
	id: string;
	user: string;
	user_email: string;
	status: MeditationStatus;
	segment_count: number;
	created_at: string;
	updated_at: string;
}

const BASE = `${COACH_BASE_URL}/admin/meditations`;

export async function fetchMeditations(
	status?: string,
): Promise<MeditationListItem[]> {
	const query = status ? `?status=${encodeURIComponent(status)}` : "";
	const response = await authFetch(`${BASE}${query}`);
	if (!response.ok) throw new Error("Failed to fetch meditations");
	return response.json();
}

export async function fetchMeditation(id: string): Promise<MeditationDetail> {
	const response = await authFetch(`${BASE}/${id}`);
	if (!response.ok) throw new Error("Failed to fetch meditation");
	return response.json();
}

export async function createMeditationForUser(
	userId: string,
): Promise<MeditationDetail> {
	const response = await authFetch(`${BASE}/create-for-user`, {
		method: "POST",
		body: JSON.stringify({ user_id: userId }),
	});
	if (!response.ok) throw new Error("Failed to create meditation");
	return response.json();
}

export async function generatePart(
	segmentId: string,
	kind: MeditationAssetKind,
): Promise<void> {
	const response = await authFetch(`${BASE}/generate-part`, {
		method: "POST",
		body: JSON.stringify({ segment_id: segmentId, kind }),
	});
	if (!response.ok) throw new Error("Failed to start generation");
}

export async function setActiveAsset(
	assetId: string,
): Promise<MeditationDetail> {
	const response = await authFetch(`${BASE}/set-active`, {
		method: "POST",
		body: JSON.stringify({ asset_id: assetId }),
	});
	if (!response.ok) throw new Error("Failed to set active version");
	return response.json();
}

export async function updateSegment(
	segmentId: string,
	fields: { video_prompt?: string; audio_script?: string },
): Promise<MeditationDetail> {
	const response = await authFetch(`${BASE}/update-segment`, {
		method: "PATCH",
		body: JSON.stringify({ segment_id: segmentId, ...fields }),
	});
	if (!response.ok) throw new Error("Failed to update segment");
	return response.json();
}
