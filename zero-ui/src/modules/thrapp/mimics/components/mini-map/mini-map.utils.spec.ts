import { describe, expect, it } from "vitest";
import { MimicWithMiniMapProps } from "./mini-map.types";
import { getMiniMapLayout } from "./mini-map.utils";

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
