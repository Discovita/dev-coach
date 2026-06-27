import type React from "react";

/**
 * The coach "thinking" indicator: three dots that bounce in a staggered loop.
 *
 * The bounce is a plain CSS keyframe animation, NOT framer-motion. Framer's
 * JS/WAAPI-driven *infinite* transform animation rendered the dots but did not
 * actually run them in the production build (they sat static on neovita.ai
 * while animating fine under `vite dev`). A CSS animation runs identically
 * across every browser and build mode, which is exactly what a simple looping
 * indicator wants. Keyframes are inlined via a scoped <style> (same pattern as
 * StudioUnlockAnimation) so this component stays self-contained.
 */
export const LoadingBubbles: React.FC = () => {
	const numBubbles = 3;
	const stagger = 0.18; // seconds between each dot

	return (
		<div
			className="flex gap-1.5 py-3 min-w-[60px] items-end"
			aria-label="Loading..."
		>
			<style>{`
				@keyframes lb-bounce {
					0%, 100% { transform: translateY(0); }
					50% { transform: translateY(-8px); }
				}
				.lb-dot { animation: lb-bounce 0.9s ease-in-out infinite; }
			`}</style>
			{Array.from({ length: numBubbles }).map((_, i) => (
				<span
					// biome-ignore lint/suspicious/noArrayIndexKey: fixed-length, never reordered
					key={i}
					className="lb-dot w-2 h-2 rounded-full bg-neutral-500 dark:bg-gold-600"
					style={{ animationDelay: `${i * stagger}s` }}
					aria-hidden="true"
				/>
			))}
		</div>
	);
};
