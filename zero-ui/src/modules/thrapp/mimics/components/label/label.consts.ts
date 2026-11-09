/** The side of its component a label sits on. */
export enum LabelPlacement {
  Above = "above",
  Below = "below",
  Start = "start",
  End = "end",
}

/**
 * Where the visible label sits within the footprint of its full content, so the edge facing its
 * component stays put when the layer filters hide the tag or the value.
 */
export const LABEL_PLACEMENT_ALIGNMENT: Record<LabelPlacement, string> = {
  [LabelPlacement.Above]: "self-end",
  [LabelPlacement.Below]: "self-start",
  [LabelPlacement.Start]: "self-center justify-self-end",
  [LabelPlacement.End]: "self-center justify-self-start",
};
