/**
 * Determines whether to use "a" or "an" based on the first letter of the name
 */
export function getArticle(name: string): string {
  const firstLetter = name.trim().toLowerCase()[0];
  const vowels = ["a", "e", "i", "o", "u"];
  return vowels.includes(firstLetter) ? "an" : "a";
}
