import { describe, expect, it } from "vitest";
import { findTooltipContext } from ".";

describe("findTooltipContext", () => {
  it("returns every context of a shared yard tag with its index", () => {
    const contexts = findTooltipContext("1003");

    expect(contexts.map(({ index, source }) => [index, source?.[1]])).toEqual([
      [0, "adsorption"],
      [1, "consumers"],
    ]);
  });

  it("returns nothing for an unknown key", () => {
    expect(findTooltipContext("unknown")).toEqual([]);
  });
});
