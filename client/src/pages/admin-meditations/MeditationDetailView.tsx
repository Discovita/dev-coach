import type {
	MeditationAsset,
	MeditationAssetKind,
	MeditationSegment,
} from "@/api/adminMeditations";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
	useGeneratePart,
	useMeditationDetail,
	useSetActive,
	useUpdateSegment,
} from "@/hooks/use-admin-meditations";
import { ArrowLeft, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import {
	assetsOfKind,
	formatStatus,
	statusVariant,
} from "./meditation-helpers";

interface Props {
	meditationId: string;
	onBack: () => void;
}

export default function MeditationDetailView({ meditationId, onBack }: Props) {
	const {
		data: meditation,
		isLoading,
		isError,
	} = useMeditationDetail(meditationId);

	if (isLoading) {
		return (
			<div className="flex items-center justify-center h-64">
				<Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
			</div>
		);
	}

	if (isError || !meditation) {
		return (
			<div className="flex flex-col items-center gap-4 py-12">
				<p className="text-destructive">Failed to load meditation.</p>
				<Button variant="outline" onClick={onBack}>
					Back
				</Button>
			</div>
		);
	}

	return (
		<div className="max-w-4xl mx-auto">
			<div className="flex items-center justify-between mb-6">
				<div className="flex items-center gap-3">
					<Button
						variant="ghost"
						size="sm"
						onClick={onBack}
						className="gap-1.5"
					>
						<ArrowLeft className="w-4 h-4" />
						Back
					</Button>
					<div>
						<h1 className="text-xl font-bold">{meditation.user_email}</h1>
						<p className="text-xs text-muted-foreground">
							{meditation.segments.length} segments
						</p>
					</div>
				</div>
				<Badge variant={statusVariant(meditation.status)}>
					{formatStatus(meditation.status)}
				</Badge>
			</div>

			<div className="flex flex-col gap-4">
				{meditation.segments.map((segment) => (
					<SegmentCard
						key={segment.id}
						segment={segment}
						meditationId={meditationId}
					/>
				))}
				{meditation.segments.length === 0 && (
					<p className="text-center text-muted-foreground py-8">
						No segments — this user had no identities with both an image and an
						I Am statement.
					</p>
				)}
			</div>
		</div>
	);
}

function SegmentCard({
	segment,
	meditationId,
}: {
	segment: MeditationSegment;
	meditationId: string;
}) {
	return (
		<Card>
			<CardHeader>
				<CardTitle className="text-base">
					{segment.order + 1}. {segment.identity_name ?? "Identity"}
				</CardTitle>
			</CardHeader>
			<CardContent className="grid gap-6 md:grid-cols-2">
				<AssetPanel
					segment={segment}
					meditationId={meditationId}
					kind="VIDEO"
				/>
				<AssetPanel
					segment={segment}
					meditationId={meditationId}
					kind="AUDIO"
				/>
			</CardContent>
		</Card>
	);
}

function AssetPanel({
	segment,
	meditationId,
	kind,
}: {
	segment: MeditationSegment;
	meditationId: string;
	kind: MeditationAssetKind;
}) {
	const isVideo = kind === "VIDEO";
	const generate = useGeneratePart(meditationId);
	const setActive = useSetActive(meditationId);
	const updateSegment = useUpdateSegment(meditationId);

	const initialScript = isVideo
		? segment.current_video_prompt
		: segment.current_audio_script;
	const [script, setScript] = useState(initialScript);
	useEffect(() => setScript(initialScript), [initialScript]);

	const versions = assetsOfKind(segment.assets, kind);
	const latest = versions[0];
	const active = versions.find((a) => a.is_active);
	const pending =
		latest && (latest.status === "QUEUED" || latest.status === "GENERATING");
	const failed = latest?.status === "FAILED";

	const onGenerate = () => generate.mutate({ segmentId: segment.id, kind });
	const onSave = () =>
		updateSegment.mutate({
			segmentId: segment.id,
			fields: isVideo ? { video_prompt: script } : { audio_script: script },
		});

	return (
		<div className="flex flex-col gap-3">
			<div className="flex items-center justify-between">
				<span className="text-sm font-medium">
					{isVideo ? "Video" : "Audio"}
				</span>
				<Button
					size="sm"
					variant="outline"
					onClick={onGenerate}
					disabled={pending || generate.isPending}
				>
					{pending ? (
						<>
							<Loader2 className="w-3.5 h-3.5 animate-spin" /> Generating…
						</>
					) : versions.length ? (
						"Regenerate"
					) : (
						"Generate"
					)}
				</Button>
			</div>

			{failed && (
				<p className="text-xs text-destructive">
					Generation failed{latest?.error_code ? `: ${latest.error_code}` : ""}.
					Try again.
				</p>
			)}

			{active?.url ? (
				<AssetPlayer url={active.url} isVideo={isVideo} />
			) : (
				!pending && (
					<p className="text-xs text-muted-foreground">No version yet.</p>
				)
			)}

			{versions.length > 1 && (
				<div className="flex gap-2">
					{versions.slice(0, 2).map((asset) => (
						<VersionChip
							key={asset.id}
							asset={asset}
							onUse={() => setActive.mutate(asset.id)}
							disabled={asset.is_active || setActive.isPending}
						/>
					))}
				</div>
			)}

			<div className="flex flex-col gap-1.5">
				<label className="text-xs text-muted-foreground">
					{isVideo ? "Video prompt" : "Audio script"}
				</label>
				<Textarea
					value={script}
					onChange={(e) => setScript(e.target.value)}
					rows={4}
					className="text-xs"
				/>
				<Button
					size="sm"
					variant="ghost"
					onClick={onSave}
					disabled={script === initialScript || updateSegment.isPending}
					className="self-end"
				>
					Save
				</Button>
			</div>
		</div>
	);
}

function AssetPlayer({ url, isVideo }: { url: string; isVideo: boolean }) {
	// Streams directly from S3; never proxied through the backend.
	return isVideo ? (
		// biome-ignore lint/a11y/useMediaCaption: QC preview of generated clip
		<video key={url} src={url} controls className="w-full rounded-md border" />
	) : (
		// biome-ignore lint/a11y/useMediaCaption: QC preview of generated narration
		<audio key={url} src={url} controls className="w-full" />
	);
}

function VersionChip({
	asset,
	onUse,
	disabled,
}: {
	asset: MeditationAsset;
	onUse: () => void;
	disabled: boolean;
}) {
	return (
		<Button
			size="sm"
			variant={asset.is_active ? "default" : "outline"}
			onClick={onUse}
			disabled={disabled}
			className="text-xs"
		>
			v{asset.version}
			{asset.is_active ? " (active)" : " · Use"}
		</Button>
	);
}
