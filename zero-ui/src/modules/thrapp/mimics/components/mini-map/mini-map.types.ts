/** A `viewBox` as its four numbers. */
export type ViewBox = { x: number; y: number; width: number; height: number };

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
