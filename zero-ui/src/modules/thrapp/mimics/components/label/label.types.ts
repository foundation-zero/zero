export type LabelProps = Readonly<{
  width?: number | string;
  height?: number | string;
  x?: number | string;
  y?: number | string;
  targetX?: number | string;
  targetWidth?: number | string;
  minWidth?: number | string;
  /** Ignores the layer filters, for labels outside the mimic such as the legend examples. */
  unfiltered?: boolean;
}>;

/** The box of the component a label belongs to, in the coordinates of the label itself. */
export type LabelTarget = Readonly<{
  x: number;
  y: number;
  width: number;
  height: number;
}>;
