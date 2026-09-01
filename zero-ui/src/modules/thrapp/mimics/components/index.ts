import { mmath, refValue } from "@/modules/common/lib/utils";
import { Ratio } from "@/modules/thrsim/types";
import { createContext } from "reka-ui";
import { computed, MaybeRef, Ref } from "vue";

export const enum ComponentOrientation {
  Up = 0,
  UpRight = 45,
  Right = 90,
  DownRight = 135,
  Down = 180,
  DownLeft = 225,
  Left = 270,
  UpLeft = 315,
}

export const enum HeatingState {
  HeatingHigh = "heating-high",
  HeatingMedium = "heating-medium",
  HeatingLow = "heating-low",
  CoolingHigh = "cooling-high",
  CoolingMedium = "cooling-medium",
  CoolingLow = "cooling-low",
  Active = "active",
  Inactive = "inactive",
  Idle = "idle",
}

export const HEATING_STATE_COLORS: Record<HeatingState, string> = {
  [HeatingState.HeatingHigh]: "var(--heating-high)",
  [HeatingState.HeatingMedium]: "var(--heating-medium)",
  [HeatingState.HeatingLow]: "var(--heating-low)",
  [HeatingState.CoolingHigh]: "var(--cooling-high)",
  [HeatingState.CoolingMedium]: "var(--cooling-medium)",
  [HeatingState.CoolingLow]: "var(--cooling-low)",
  [HeatingState.Active]: "var(--attention)",
  [HeatingState.Inactive]: "var(--attention-dull)",
  [HeatingState.Idle]: "var(--disabled)",
};

export const CLOCKWISE_ORIENTATIONS = [
  ComponentOrientation.Up,
  ComponentOrientation.UpRight,
  ComponentOrientation.Right,
  ComponentOrientation.DownRight,
  ComponentOrientation.Down,
  ComponentOrientation.DownLeft,
  ComponentOrientation.Left,
  ComponentOrientation.UpLeft,
];

export interface MimicComponentBaseProps {
  orientation?: ComponentOrientation;
  rotation?: Ratio;
  state?: MimicComponentState;
}

export const enum MimicComponentState {
  Normal = "normal",
  Alarm = "alarm",
  Manual = "manual",
}

export interface MimicComponentProps {
  baseOrientation?: ComponentOrientation;
  id?: string;
  width: number;
  height: number;
}

export const stateColorMap: Record<MimicComponentState, string> = {
  [MimicComponentState.Normal]: "var(--attention)",
  [MimicComponentState.Alarm]: "var(--destructive)",
  [MimicComponentState.Manual]: "var(--warning)",
};

export interface MimicComponentContext {
  stateColor: Ref<string>;
  state: Ref<MimicComponentState | undefined>;
  strokeWidth: Ref<number>;
  rotationDegrees: Ref<number>;
}

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
