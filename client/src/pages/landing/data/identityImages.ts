/**
 * Identity Images Data
 *
 * Purpose:
 * - Loads and processes image data from JSON files
 * - Converts image filenames to display titles
 * - Provides image sets for each person (jason, latriza, leigh-ann)
 */

export interface IdentityImage {
	baseName: string;
	title: string;
}

/**
 * Convert image filename to display title
 * Example: "financial_alchemist" -> "I am a Financial Alchemist"
 */
function filenameToTitle(filename: string): string {
	// Remove any size suffixes if present
	const cleanName = filename
		.replace("_original", "")
		.replace("_thumbnail", "")
		.replace("_medium", "")
		.replace("_large", "")
		.replace(".jpg", "");

	// Convert snake_case to Title Case
	const words = cleanName.split("_");
	const titleCase = words
		.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
		.join(" ");

	return `I am a ${titleCase}`;
}

/**
 * Jason's identity images
 */
export const jasonImages: IdentityImage[] = [
	{
		baseName: "financial_alchemist",
		title: filenameToTitle("financial_alchemist"),
	},
	{
		baseName: "tactical_mastermind",
		title: filenameToTitle("tactical_mastermind"),
	},
	{
		baseName: "financial_brick_mason",
		title: filenameToTitle("financial_brick_mason"),
	},
	{ baseName: "swimmer", title: filenameToTitle("swimmer") },
	{ baseName: "master_of_time", title: filenameToTitle("master_of_time") },
	{ baseName: "big_wave_phenom", title: filenameToTitle("big_wave_phenom") },
	{ baseName: "big_brother", title: filenameToTitle("big_brother") },
	{
		baseName: "manifestation_king",
		title: filenameToTitle("manifestation_king"),
	},
	{ baseName: "castle_builder", title: filenameToTitle("castle_builder") },
	{ baseName: "dream_chaser", title: filenameToTitle("dream_chaser") },
];

/**
 * Latriza's identity images
 */
export const latrizaImages: IdentityImage[] = [
	{ baseName: "joy_seeker", title: filenameToTitle("joy_seeker") },
	{ baseName: "agile_lioness", title: filenameToTitle("agile_lioness") },
	{
		baseName: "beautiful_goddess",
		title: filenameToTitle("beautiful_goddess"),
	},
	{ baseName: "grounded_mother", title: filenameToTitle("grounded_mother") },
	{ baseName: "money_lover", title: filenameToTitle("money_lover") },
	{
		baseName: "captain_of_my_life",
		title: filenameToTitle("captain_of_my_life"),
	},
	{
		baseName: "open_hearted_lover",
		title: filenameToTitle("open_hearted_lover"),
	},
	{
		baseName: "talented_innovator",
		title: filenameToTitle("talented_innovator"),
	},
	{ baseName: "alchemist", title: filenameToTitle("alchemist") },
];

/**
 * Leigh-Ann's identity images
 */
export const leighAnnImages: IdentityImage[] = [
	{ baseName: "magical_healer", title: filenameToTitle("magical_healer") },
	{
		baseName: "successful_entrepenuer",
		title: filenameToTitle("successful_entrepenuer"),
	},
	{ baseName: "power_banker", title: filenameToTitle("power_banker") },
	{ baseName: "creator", title: filenameToTitle("creator") },
	{ baseName: "elegant_icon", title: filenameToTitle("elegant_icon") },
	{ baseName: "adventurer", title: filenameToTitle("adventurer") },
	{ baseName: "acrobat", title: filenameToTitle("acrobat") },
	{ baseName: "princess_wife", title: filenameToTitle("princess_wife") },
	{ baseName: "empowered_mother", title: filenameToTitle("empowered_mother") },
	{
		baseName: "captain_of_my_life",
		title: filenameToTitle("captain_of_my_life"),
	},
];
