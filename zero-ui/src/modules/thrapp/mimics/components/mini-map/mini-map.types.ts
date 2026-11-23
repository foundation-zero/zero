import { MimicComponentType } from "@/modules/thrapp/types";
import { RegisterField } from "../../data";
import { SolarPanelStringProps } from "../solar-panel-string";

/** A `viewBox` as its four numbers. */
export type ViewBox = { x: number; y: number; width: number; height: number };

/** Position and size of a nested SVG within its parent's `viewBox`. */
export type Placement = { x: number; y: number; width: number; height: number };

export type MimicWithMiniMapProps = {
  /** `viewBox` of the diagram, in its own coordinates. */
  diagram: ViewBox;
  /** `viewBox` of the mini map, in its own coordinates. */
  map: ViewBox;
  /** Height the mini map is drawn at, in the diagram's units. */
  mapHeight: number;
  /** Space between the mini map and the diagram, in the diagram's units. */
  gap?: number;
};

/** Size of the whole mimic and the placement of the mini map and the diagram within it. */
export type MiniMapLayout = {
  width: number;
  height: number;
  map: Placement;
  diagram: Placement;
};

/** A string of the bimini on a mini map, with the tooltip key of its PVT string. */
export type BiminiString = Omit<SolarPanelStringProps, "yieldRatio"> & {
  field: RegisterField<MimicComponentType.PvtString>;
};
