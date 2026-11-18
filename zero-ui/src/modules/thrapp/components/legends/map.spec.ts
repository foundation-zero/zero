import { describe, expect, it } from "vitest";
import { ManualValveType } from "../../mimics/components/manual-valve";
import { MimicComponentType } from "../../types";
import { isInLegend, LegendFeature, LegendMap, MIMIC_LEGEND_MAP } from "./map";

describe("isInLegend", () => {
  const legend: LegendMap = {
    [MimicComponentType.Pump]: true,
    [MimicComponentType.ManualValve]: [ManualValveType.Switch],
  };

  it("includes an entry, and any of its sub types, when it is set to true", () => {
    expect(isInLegend(legend, MimicComponentType.Pump)).toBe(true);
  });

  it("includes only the listed sub types", () => {
    expect(isInLegend(legend, MimicComponentType.ManualValve, ManualValveType.Switch)).toBe(true);
    expect(isInLegend(legend, MimicComponentType.ManualValve, ManualValveType.Flow)).toBe(false);
  });

  it("leaves out an entry that is not set", () => {
    expect(isInLegend(legend, MimicComponentType.CheckValve)).toBe(false);
    expect(isInLegend(legend, LegendFeature.SectionArea)).toBe(false);
  });
});

describe("MIMIC_LEGEND_MAP", () => {
  it.each(["dc-aft", "dc-ugrid", "dc-fwd"] as const)(
    "explains the components of the %s converter group",
    (mimic) => {
      const legend = MIMIC_LEGEND_MAP[mimic]!;

      expect(isInLegend(legend, MimicComponentType.ConnectingCircuit)).toBe(true);
      expect(isInLegend(legend, MimicComponentType.SwitchValve)).toBe(true);
      expect(isInLegend(legend, MimicComponentType.TemperatureSensor)).toBe(true);
      expect(isInLegend(legend, MimicComponentType.FlowSensor)).toBe(true);
      expect(isInLegend(legend, MimicComponentType.ManualValve, ManualValveType.Switch)).toBe(true);
      expect(isInLegend(legend, MimicComponentType.ManualValve, ManualValveType.Flow)).toBe(false);
    },
  );
});
