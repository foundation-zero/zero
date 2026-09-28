import { ComponentOrientation } from "..";

export { default as PvtString } from "./PvtString.vue";
export { default as PvtStringElement } from "./PvtStringElement.vue";

export const PVT_STRING_WIDTH = 30;
export const PVT_STRING_HEIGHT = 54;
export const PVT_BASE_ORIENTATION = ComponentOrientation.Up;
export type PvtStringProps = {
  width?: number;
  height?: number;
};
