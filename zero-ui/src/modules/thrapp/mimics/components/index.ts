import { refValue } from "@/modules/common/lib/utils";
import { computed, MaybeRef } from "vue";

export const enum ComponentOrientation {
  Up = 0,
  Right = 90,
  Down = 180,
  Left = 270,
}

export const CLOCKWISE_ORIENTATIONS = [
  ComponentOrientation.Up,
  ComponentOrientation.Right,
  ComponentOrientation.Down,
  ComponentOrientation.Left,
];

export const getNextOrientation = (orientation: ComponentOrientation) => {
  const nextOrientationIndex =
    (CLOCKWISE_ORIENTATIONS.indexOf(orientation) + 1) % CLOCKWISE_ORIENTATIONS.length;

  return CLOCKWISE_ORIENTATIONS[nextOrientationIndex];
};

export const useOrientation = (
  orientation: MaybeRef<ComponentOrientation>,
  baseOrientation: MaybeRef<ComponentOrientation>,
) =>
  computed(() => ({
    transform: `rotate(${(refValue(orientation) + refValue(baseOrientation)) % 360}deg)`,
  }));

export const createSizeAndViewbox = (width: number, height: number) => ({
  width,
  height,
  viewBox: `0 0 ${width} ${height}`,
});
