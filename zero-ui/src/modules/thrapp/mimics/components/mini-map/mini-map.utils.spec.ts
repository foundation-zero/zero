import { describe, expect, it } from "vitest";
import { SolarPanelSize } from "../solar-panel";
import { BiminiString, MimicWithMiniMapProps } from "./mini-map.types";
import { getMiniMapLayout, toBiminiStringProps } from "./mini-map.utils";

describe("toBiminiStringProps", () => {
  const frame = { x: 0, y: 0, width: 10, height: 10 };
  const shape = {
    frame,
    panels: [
      { x: 0, y: 0 },
      { x: 0, y: 0, size: SolarPanelSize.Small },
    ],
  };
  const strings: BiminiString[] = [
    { field: "pvt:aft-string-3", ...shape },
    { field: "pvt:aft-string-3", ...shape },
    { field: "pvt:aft-string-4", frame, panels: [{ x: 0, y: 0 }] },
  ];

  it("gives each shape the peak heat of its whole string", () => {
    const [left, right, single] = toBiminiStringProps(strings);
    const shapePeak = 360 + (360 * 14) / 27;
    expect(left.peakHeat).toBeCloseTo(2 * shapePeak);
    expect(right.peakHeat).toBeCloseTo(2 * shapePeak);
    expect(single.peakHeat).toBe(360);
  });
});

// A wide diagram and a map that is drawn at twice its own size.
const props: MimicWithMiniMapProps = {
  diagram: { x: -20, y: -20, width: 1000, height: 500 },
  map: { x: 0, y: 0, width: 100, height: 200 },
  mapHeight: 400,
  gap: 30,
};

describe("getMiniMapLayout", () => {
  it("puts the map left of the diagram, both centred vertically", () => {
    expect(getMiniMapLayout(props, false)).toEqual({
      width: 1230,
      height: 500,
      map: { x: 0, y: 50, width: 200, height: 400 },
      diagram: { x: 230, y: 0, width: 1000, height: 500 },
    });
  });

  it("puts the map above the diagram, both centred horizontally", () => {
    expect(getMiniMapLayout(props, true)).toEqual({
      width: 1000,
      height: 930,
      map: { x: 400, y: 0, width: 200, height: 400 },
      diagram: { x: 0, y: 430, width: 1000, height: 500 },
    });
  });

  it("centres the diagram on a map that is taller or wider than it", () => {
    const small = { ...props, diagram: { x: 0, y: 0, width: 100, height: 300 } };
    expect(getMiniMapLayout(small, false).diagram).toEqual({
      x: 230,
      y: 50,
      width: 100,
      height: 300,
    });
    expect(getMiniMapLayout(small, true).diagram).toEqual({
      x: 50,
      y: 430,
      width: 100,
      height: 300,
    });
  });

  it("leaves 40 units between them by default", () => {
    const { gap: _, ...withoutGap } = props;
    expect(getMiniMapLayout(withoutGap, false).diagram.x).toBe(240);
  });
});
