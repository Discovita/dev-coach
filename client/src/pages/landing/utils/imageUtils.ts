/**
 * Image utilities for landing page
 *
 * Purpose:
 * - Provides responsive image source selection based on screen size
 * - Converts image names to proper file paths
 */

export interface ImageSizes {
	thumbnail: string;
	medium: string;
	large: string;
	original: string;
}

/**
 * Get responsive image source based on screen size
 * Uses srcset and sizes for optimal image loading
 */
export function getResponsiveImageSrc(
	baseName: string,
	folder: string,
): { src: string; srcSet: string; sizes: string } {
	const basePath = `/landing/${folder}/${baseName}`;

	return {
		src: `${basePath}_medium.jpg`, // Default/fallback
		srcSet: [
			`${basePath}_thumbnail.jpg 100w`,
			`${basePath}_medium.jpg 300w`,
			`${basePath}_large.jpg 600w`,
			`${basePath}_original.jpg 1080w`,
		].join(", "),
		sizes:
			"(max-width: 640px) 280px, (max-width: 768px) 400px, (max-width: 1024px) 600px, (max-width: 1280px) 800px, 1080px",
	};
}

/**
 * Extract base name from image URL or path
 */
export function extractImageBaseName(imageUrl: string): string {
	const fileName = imageUrl.split("/").pop() || "";
	return fileName
		.replace(".jpg", "")
		.replace("_original", "")
		.replace("_thumbnail", "")
		.replace("_medium", "")
		.replace("_large", "");
}
