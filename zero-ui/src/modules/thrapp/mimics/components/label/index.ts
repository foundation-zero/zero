export { default as Label } from "./Label.vue";

export type LabelProps = Readonly<{
  width?: number | string;
  height?: number | string;
  x?: number | string;
  y?: number | string;
  targetX?: number | string;
  targetWidth?: number | string;
}>;
