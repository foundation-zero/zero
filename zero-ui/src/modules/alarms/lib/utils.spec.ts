import { describe, expect, it } from "vitest";
import { isActive } from "./utils";

describe("isActive", () => {
  it.each([
    [{ active: true }, true],
    [{ active: false }, false],
    [{ active: null }, false],
    [null, false],
  ])("%o is active: %s", (alarm, expected) => {
    expect(isActive(alarm)).toBe(expected);
  });
});
