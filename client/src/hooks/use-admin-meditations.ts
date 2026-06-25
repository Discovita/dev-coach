import {
	type MeditationAssetKind,
	type MeditationDetail,
	type MeditationListItem,
	createMeditationForUser,
	fetchMeditation,
	fetchMeditations,
	generatePart,
	setActiveAsset,
	updateSegment,
} from "@/api/adminMeditations";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

const LIST_KEY = ["admin", "meditations"];
const detailKey = (id: string) => ["admin", "meditation", id];

/** True if any asset is still queued/generating — used to drive polling. */
function hasPendingParts(detail: MeditationDetail | undefined): boolean {
	if (!detail) return false;
	return detail.segments.some((segment) =>
		segment.assets.some(
			(asset) => asset.status === "QUEUED" || asset.status === "GENERATING",
		),
	);
}

export function useMeditationsList(status?: string) {
	return useQuery<MeditationListItem[]>({
		queryKey: [...LIST_KEY, status ?? "all"],
		queryFn: () => fetchMeditations(status),
		staleTime: 1000 * 30,
	});
}

export function useMeditationDetail(id: string | null) {
	return useQuery<MeditationDetail>({
		queryKey: id ? detailKey(id) : ["admin", "meditation", "none"],
		queryFn: () => fetchMeditation(id as string),
		enabled: !!id,
		// Poll while any part is generating so the QC view updates live.
		refetchInterval: (query) =>
			hasPendingParts(query.state.data as MeditationDetail | undefined)
				? 5000
				: false,
	});
}

export function useCreateMeditation() {
	const qc = useQueryClient();
	return useMutation({
		mutationFn: (userId: string) => createMeditationForUser(userId),
		onSuccess: () => qc.invalidateQueries({ queryKey: LIST_KEY }),
	});
}

export function useGeneratePart(meditationId: string) {
	const qc = useQueryClient();
	return useMutation({
		mutationFn: (vars: { segmentId: string; kind: MeditationAssetKind }) =>
			generatePart(vars.segmentId, vars.kind),
		onSuccess: () =>
			qc.invalidateQueries({ queryKey: detailKey(meditationId) }),
	});
}

export function useSetActive(meditationId: string) {
	const qc = useQueryClient();
	return useMutation({
		mutationFn: (assetId: string) => setActiveAsset(assetId),
		onSuccess: (data) => qc.setQueryData(detailKey(meditationId), data),
	});
}

export function useUpdateSegment(meditationId: string) {
	const qc = useQueryClient();
	return useMutation({
		mutationFn: (vars: {
			segmentId: string;
			fields: { video_prompt?: string; audio_script?: string };
		}) => updateSegment(vars.segmentId, vars.fields),
		onSuccess: (data) => qc.setQueryData(detailKey(meditationId), data),
	});
}
