import type { TotalRow } from "@/modules/thrapp/monitoring/monitoring.types";
import { describe, expect, it } from "vitest";
import { delivered, pieOption, share, treemapOption } from "./heat-distribution.utils";

const ROWS: TotalRow[] = [
  { asset: "[1] dhw-dc-recovery", shortName: "DC recovery", value: 6, color: "orange" },
  { asset: "[2] dhw-ht-boosting", value: 3, color: "yellow" },
  { asset: "[3] dhw-heat-pump", shortName: "Heat pump", value: 0, color: "green" },
  { asset: "[4] dhw-hvac-recovery", shortName: "HVAC recovery", value: 1, color: "pink" },
];

type Series = {
  data: { name: string; value: number; itemStyle: { color: string } }[];
  label?: { formatter?: (params: { name: string; value?: unknown }) => string };
  itemStyle?: { borderColor?: string };
};
type Tooltip = { formatter: (params: unknown) => string };

describe("heat distribution", () => {
  it("leaves out sources that delivered nothing", () => {
    expect(delivered(ROWS).map((row) => row.value)).toEqual([6, 3, 1]);
  });

  it("rounds each source's share of the total", () => {
    expect(share(6, ROWS)).toBe(60);
    expect(share(1, ROWS)).toBe(10);
    expect(share(1, [])).toBe(0);
  });

  it("sizes a tile per delivering source, named by its short name, in its colour", () => {
    const option = treemapOption(ROWS, "kWh", "white");
    const [series] = option.series as Series[];

    expect(series.data).toEqual([
      { name: "DC recovery", value: 6, itemStyle: { color: "orange" } },
      { name: "[2] dhw-ht-boosting", value: 3, itemStyle: { color: "yellow" } },
      { name: "HVAC recovery", value: 1, itemStyle: { color: "pink" } },
    ]);
    expect(series.label!.formatter!({ name: "DC recovery", value: 6 })).toBe(
      "DC recovery\n6 kWh · 60%",
    );
  });

  it("puts a surface gap between the slices of the pie", () => {
    const option = pieOption(ROWS, "kWh", "black");
    const [series] = option.series as Series[];

    expect(series.data.map((slice) => slice.name)).toEqual([
      "DC recovery",
      "[2] dhw-ht-boosting",
      "HVAC recovery",
    ]);
    expect(series.itemStyle!.borderColor).toBe("black");
  });

  it("shows the energy and share of a hovered source in the tooltip", () => {
    const tooltip = pieOption(ROWS, "kWh", "black").tooltip as Tooltip;

    const html = tooltip.formatter({ name: "HVAC recovery", value: 1 });
    expect(html).toContain("HVAC recovery");
    expect(html).toContain("1 kWh · 10%");
  });
});
