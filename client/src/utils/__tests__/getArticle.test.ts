import { describe, it, expect } from "vitest";
import { getArticle } from "@/utils/getArticle";

describe("getArticle", () => {
  it('returns "an" for names starting with a vowel', () => {
    expect(getArticle("Adventurer")).toBe("an");
    expect(getArticle("explorer")).toBe("an");
    expect(getArticle("Innovator")).toBe("an");
    expect(getArticle("Optimist")).toBe("an");
    expect(getArticle("Underdog")).toBe("an");
  });

  it('returns "a" for names starting with a consonant', () => {
    expect(getArticle("Builder")).toBe("a");
    expect(getArticle("Creator")).toBe("a");
    expect(getArticle("Dreamer")).toBe("a");
    expect(getArticle("Leader")).toBe("a");
  });

  it("handles leading whitespace", () => {
    expect(getArticle("  Artist")).toBe("an");
    expect(getArticle("  Builder")).toBe("a");
  });

  it("is case-insensitive", () => {
    expect(getArticle("ARTIST")).toBe("an");
    expect(getArticle("artist")).toBe("an");
    expect(getArticle("BUILDER")).toBe("a");
  });
});
