import { mmath, refValue } from "@/modules/common/lib/utils";
import { Ratio } from "@/modules/thrapp/types/thrs";
import { createContext } from "reka-ui";
import { computed, MaybeRef, Ref } from "vue";
import {
  CLOCKWISE_ORIENTATIONS,
  ComponentOrientation,
  MimicComponentState,
  stateColorMap,
} from "./components.consts";
import { MimicComponentContext } from "./components.types";

export const createMimicComponentContext = (
  state: Ref<MimicComponentState | undefined>,
  rotationDegrees: MaybeRef<number> = 0,
  strokeWidth: number = 2,
): MimicComponentContext => ({
  stateColor: computed(() => stateColorMap[state.value!]),
  state,
  strokeWidth: computed(() => (state.value === MimicComponentState.Normal ? 1 : strokeWidth)),
  rotationDegrees: computed(() => refValue(rotationDegrees)),
});

export const [getMimicComponentContext, provideMimicComponentContext] =
  createContext<MimicComponentContext>("MimicComponentContext");

export const getNextOrientation = (orientation: ComponentOrientation, stepSize = 1) => {
  const nextOrientationIndex =
    (CLOCKWISE_ORIENTATIONS.indexOf(orientation) + stepSize + CLOCKWISE_ORIENTATIONS.length) %
    CLOCKWISE_ORIENTATIONS.length;

  return CLOCKWISE_ORIENTATIONS[nextOrientationIndex];
};

export const useRotationDegrees = (
  orientation: MaybeRef<ComponentOrientation>,
  baseOrientation: MaybeRef<ComponentOrientation>,
  rotation: MaybeRef<Ratio> = 0,
) =>
  computed(() =>
    mmath.normalizeDegrees(
      refValue(orientation) - refValue(baseOrientation) - 90 * refValue(rotation),
    ),
  );

export const useOrientation = (
  orientation: MaybeRef<ComponentOrientation>,
  baseOrientation: MaybeRef<ComponentOrientation>,
  rotation: MaybeRef<Ratio> = 0,
) => {
  const degrees = useRotationDegrees(orientation, baseOrientation, rotation);

  return computed(() => ({ transform: `rotate(${degrees.value}deg)` }));
};

export const createSizeAndViewbox = (
  width: number | string,
  height: number | string,
  forceHeight = true,
) => ({
  width,
  height: forceHeight ? height : undefined,
  viewBox: `0 0 ${width} ${height}`,
});
