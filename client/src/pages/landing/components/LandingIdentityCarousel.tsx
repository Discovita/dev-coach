/**
 * LandingIdentityCarousel
 *
 * Purpose:
 * - Auto-scrolling carousel of identity cards with images and text overlays
 * - Uses responsive images based on screen size (thumbnail, medium, large, original)
 * - Each card features an image background with gradient overlay and white text
 * - Smooth infinite scrolling animation
 */

import { useEffect, useRef } from "react";
import { getResponsiveImageSrc } from "../utils/imageUtils";

interface IdentityImage {
	baseName: string;
	title: string;
}

interface LandingIdentityCarouselProps {
	images: IdentityImage[];
	folder: string;
	alignment?: "left" | "center" | "right";
	autoScroll?: boolean;
	scrollSpeed?: number; // pixels per second
}

export default function LandingIdentityCarousel({
	images,
	folder,
	alignment = "center",
	autoScroll = true,
	scrollSpeed = 30,
}: LandingIdentityCarouselProps) {
	const scrollContainerRef = useRef<HTMLDivElement>(null);

	const alignmentClasses = {
		left: "justify-start",
		center: "justify-center",
		right: "justify-end",
	};

	// Auto-scroll functionality
	useEffect(() => {
		if (!autoScroll || !scrollContainerRef.current) return;

		const container = scrollContainerRef.current;
		let animationId: number;
		let lastTimestamp: number | null = null;
		let scrollPosition = 0;

		const animate = (timestamp: number) => {
			if (lastTimestamp === null) {
				lastTimestamp = timestamp;
			}

			const deltaTime = (timestamp - lastTimestamp) / 1000; // seconds
			lastTimestamp = timestamp;

			const scrollDistance = scrollSpeed * deltaTime;
			scrollPosition += scrollDistance;

			// Calculate the width of one set of images (half of total since we duplicate)
			const singleSetWidth = container.scrollWidth / 2;

			if (scrollPosition >= singleSetWidth) {
				// Reset to start for seamless infinite scroll
				scrollPosition = scrollPosition - singleSetWidth;
			}

			container.scrollLeft = scrollPosition;
			animationId = requestAnimationFrame(animate);
		};

		animationId = requestAnimationFrame(animate);

		return () => {
			if (animationId) {
				cancelAnimationFrame(animationId);
			}
		};
	}, [autoScroll, scrollSpeed]);

	return (
		<div
			className="w-full overflow-x-auto overflow-y-hidden [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
			ref={scrollContainerRef}
		>
			<div
				className={`flex items-center relative shrink-0 w-full min-w-max ${alignmentClasses[alignment]} gap-0`}
			>
				{/* Render images twice for seamless infinite scroll */}
				{[...images, ...images].map((image, index) => {
					const imageSrc = getResponsiveImageSrc(image.baseName, folder);

					return (
						<div
							key={`${image.baseName}-${index}`}
							className="flex flex-col gap-2 sm:gap-[10px] items-start overflow-hidden relative shadow-[0px_1px_4px_0px_rgba(30,30,30,0.25)] shrink-0 w-[280px] sm:w-[400px] md:w-[600px] lg:w-[800px] xl:w-[1080px] h-[200px] sm:h-[300px] md:h-[400px] lg:h-[500px] xl:h-[608px]"
						>
							<img
								alt={image.title}
								className="absolute inset-0 max-w-none object-cover pointer-events-none size-full"
								src={imageSrc.src}
								srcSet={imageSrc.srcSet}
								sizes={imageSrc.sizes}
								loading="lazy"
							/>
							<div className="bg-gradient-to-b flex from-[67.524%] from-[rgba(11,28,74,0)] gap-2 sm:gap-[10px] h-full items-end p-4 sm:p-6 md:p-8 lg:p-10 relative shadow-[2px_2px_10px_0px_rgba(0,0,0,0.8)] shrink-0 to-[rgba(11,28,74,0.7)] w-full">
								<p className="font-bold leading-normal relative shrink-0 text-base sm:text-lg md:text-xl lg:text-2xl xl:text-[30px] text-white text-nowrap tracking-tight sm:tracking-[0.4px] md:tracking-[0.6px] whitespace-pre">
									{image.title}
								</p>
							</div>
						</div>
					);
				})}
			</div>
		</div>
	);
}
