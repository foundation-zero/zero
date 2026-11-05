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
