import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { describe, expect, it } from "vitest";
import { findTooltipContext } from ".";
import { getField } from "../providers";

describe("findTooltipContext", () => {
  it("returns every context of a shared yard tag with its index", () => {
    const contexts = findTooltipContext("1003");

    expect(contexts.map(({ index, source }) => [index, source?.[1]])).toEqual([
      [0, "adsorption"],
      [1, "consumers"],
    ]);
  });

  it("finds a field by the module it is read from, not the mimic data that shows it", () => {
    // The dc data shows the U-Grids, but they are read from the dcAcConverter module.
    const contexts = findTooltipContext(
      getField(SensorComponentType.Ugrid, "dcAcConverter", "_5_11U101"),
    );

    expect(contexts.map(({ type, registerField }) => [type, registerField])).toEqual([
      ["PowerConverter", "dc:ugrid-1"],
    ]);
  });

  it("returns nothing for an unknown key", () => {
    expect(findTooltipContext("unknown")).toEqual([]);
  });
});
