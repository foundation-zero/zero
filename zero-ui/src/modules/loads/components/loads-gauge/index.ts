import { mmath } from "@/modules/common/lib/utils";
import { createContext } from "reka-ui";
import { computed, toRef, toRefs, ToRefs, type Ref } from "vue";
import { ReferenceThresholds } from "../../types";

export { default as GaugePoint } from "./GaugePoint.vue";
export { default as GaugePoints } from "./GaugePoints.vue";
export { default as GaugeTargetRange } from "./GaugeTargetRange.vue";

export { default as Gauge } from "./Gauge.vue";
export { default as GaugeTarget } from "./GaugeTarget.vue";
export { default as GaugeStep } from "./GaugeTick.vue";
export { default as GaugeTicks } from "./GaugeTicks.vue";

export const TICK_RADIUS = 22;
export const TICK_LENGTH = 5;
export const TICK_OFFSET = 10;
export const GAUGE_WIDTH = 320;
export const GAUGE_PADDING = 18;
export const GAUGE_HEIGHT = GAUGE_WIDTH / 2 + GAUGE_PADDING;
export const GAUGE_CENTER: Coords = { x: GAUGE_WIDTH / 2, y: GAUGE_HEIGHT };

export const GAUGE_RADIUS = 124;
export const POINT_ARC_RADIUS = 136;
export const POINT_RADIUS = 4;
export const START_ANGLE = 180;
export const END_ANGLE = 360;
export const TOTAL_ANGLE = (END_ANGLE - START_ANGLE + 360) % 360;
export const AMOUNT_OF_POINTS_PER_SIDE = 13;
export const TOTAL_AMOUNT_OF_POINTS = AMOUNT_OF_POINTS_PER_SIDE * 2 + 1;
export const ANGLE_STEP = TOTAL_ANGLE / (AMOUNT_OF_POINTS_PER_SIDE * 2);
export const EXTRA_TICK_THRESHOLD = AMOUNT_OF_POINTS_PER_SIDE * 0.5;
export const ARC_START_ANGLE = 166;
export const ARC_END_ANGLE = 14;

export interface Coords {
  x: number;
  y: number;
}

export const coords = (x: number, y: number): Coords => ({ x, y });

export interface CoordsWithRadiansAngle extends Coords {
  angleInRadians: number;
}

// GaugeStep defines the data type for both the ticks and points of the gauge.
// Points are the dots/circles and can be colored individually.
// Ticks are the lines on the gauge and are only visible at specific indices based on the visible range and thresholds.
export interface GaugeStep extends CoordsWithRadiansAngle {
  value: number;
  angle: number;
  color: Colors;
}

export const enum Colors {
  Transparent = "var(--color-muted/0)",
  Empty = "var(--color-muted)",
  Warning = "var(--color-warning)",
  Target = "var(--color-constructive)",
  Destructive = "var(--color-destructive)",
}

export type Range = [start: number, end: number];

export interface GaugeRootProps {
  currentValue?: number; // Current/actual value, optional to allow defaulting to target
  scale: Range; // Scale/range [min, max]
  thresholds?: ReferenceThresholds; // Warning/Alarm thresholds
}

export type GaugeRootContext = ToRefs<GaugeRootProps> & {
  points: Ref<GaugeStep[]>;
  ticks: Ref<GaugeStep[]>;
  target: Ref<number>;
  targetRange: Ref<Range>;
};

// Helper function to convert polar coordinates to cartesian
export const polarToCartesian = (
  radius: number,
  angleInDegrees: number,
  offset: Coords = { x: 0, y: 0 },
): CoordsWithRadiansAngle => {
  const angleInRadians = (angleInDegrees * Math.PI) / 180.0;

  return {
    x: offset.x + radius * Math.cos(angleInRadians),
    y: offset.y + radius * Math.sin(angleInRadians),
    angleInRadians,
  };
};

export const makeRange = (
  low: number | undefined,
  high: number | undefined,
  [scaleLow, scaleHigh]: Range,
): Range => [low ?? scaleLow, high ?? scaleHigh];

export const describeArc = (
  centerX: number,
  centerY: number,
  radius: number,
  startAngle: number,
  endAngle: number,
) => {
  const start = polarToCartesian(radius, endAngle, { x: centerX, y: centerY });
  const end = polarToCartesian(radius, startAngle, { x: centerX, y: centerY });

  const angleDiff = mmath.normalizeDegrees(endAngle - startAngle);

  const largeArcFlag = angleDiff <= 180 ? "0" : "1";

  return ["M", start.x, start.y, "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y].join(" ");
};

const createFallbackPoints = (target: number): GaugeStep[] =>
  Array.from({ length: TOTAL_AMOUNT_OF_POINTS }, (_, i) => ({
    value: target,
    angle: START_ANGLE + ANGLE_STEP * i,
    color: i === AMOUNT_OF_POINTS_PER_SIDE ? Colors.Target : Colors.Empty,
    ...polarToCartesian(POINT_ARC_RADIUS, START_ANGLE + ANGLE_STEP * i, GAUGE_CENTER),
  }));

export const getTickColor =
  (
    ticksLeft: number,
    ticksRight: number,
    [fillLow, fillHigh]: Range,
    [targetLow, targetHigh]: Range,
    [warningLow, warningHigh]: Range,
  ) =>
  (tickIndex: number, tickValue: number) => {
    const tickIsOutsideOfVisibleRange =
      tickIndex < AMOUNT_OF_POINTS_PER_SIDE - ticksLeft ||
      tickIndex > AMOUNT_OF_POINTS_PER_SIDE + ticksRight;
    const tickValueIsWithinFillRange = tickValue >= fillLow && tickValue <= fillHigh;
    const tickValueIsWithinTargetRange = tickValue >= targetLow && tickValue <= targetHigh;
    const tickValueIsWithinWarningRange = tickValue >= warningLow && tickValue <= warningHigh;

    if (tickIsOutsideOfVisibleRange) {
      return Colors.Transparent;
    } else if (!tickValueIsWithinFillRange) {
      return Colors.Empty;
    } else if (tickValueIsWithinTargetRange) {
      return Colors.Target;
    } else if (tickValueIsWithinWarningRange) {
      return Colors.Warning;
    } else {
      return Colors.Destructive;
    }
  };

export const createPoints = (
  [scaleLow, scaleHigh]: Range,
  targetRange: Range,
  warningRange: Range,
  target: number,
  currentValue: Ref<number>,
): GaugeStep[] => {
  const deltaToLow = Math.abs(target - scaleLow);
  const deltaToHigh = Math.abs(scaleHigh - target);
  const scaleBandwidth = scaleHigh - scaleLow;

  const highestDelta = Math.max(deltaToLow, deltaToHigh);

  // When the scale collapses to a single point, show only the target tick at the center.
  if (highestDelta === 0 || scaleBandwidth === 0) {
    return createFallbackPoints(target);
  }

  // Calculate the distribution/visibility of ticks on each side of the target based on the distance to the scale bounds.
  const weightLeft = deltaToLow / highestDelta;
  const weightRight = deltaToHigh / highestDelta;
  const totalTicks = (weightLeft + weightRight) * AMOUNT_OF_POINTS_PER_SIDE;
  const tickStepSize = scaleBandwidth / totalTicks;

  if (!Number.isFinite(tickStepSize)) {
    return createFallbackPoints(target);
  }

  const ticksLeft = Math.ceil(weightLeft * AMOUNT_OF_POINTS_PER_SIDE);
  const ticksRight = Math.ceil(weightRight * AMOUNT_OF_POINTS_PER_SIDE);

  const fillRange: Range = [
    Math.min(currentValue.value, target),
    Math.max(currentValue.value, target),
  ];

  const gaugeLow = target - AMOUNT_OF_POINTS_PER_SIDE * tickStepSize;

  const _getTickColor = getTickColor(ticksLeft, ticksRight, fillRange, targetRange, warningRange);

  return Array.from({ length: AMOUNT_OF_POINTS_PER_SIDE * 2 + 1 }).map<GaugeStep>((_, i) => {
    const angle = START_ANGLE + ANGLE_STEP * i;
    const value = gaugeLow + i * tickStepSize;

    return {
      value,
      angle,
      color: _getTickColor(i, value),
      ...polarToCartesian(POINT_ARC_RADIUS, angle, GAUGE_CENTER),
    };
  });
};

const tickIsNotTransparent = ({ color }: GaugeStep) => color !== Colors.Transparent;
const roundIndexAwayFromMiddle = (index: number) =>
  index < AMOUNT_OF_POINTS_PER_SIDE ? Math.floor(index) : Math.ceil(index);

export const getTicks = (tickValues: GaugeStep[]): GaugeStep[] => {
  const firstVisibleTickIndex = tickValues.findIndex(tickIsNotTransparent);
  const lastVisibleTickIndex = tickValues.findLastIndex(tickIsNotTransparent);

  if (firstVisibleTickIndex === -1 || lastVisibleTickIndex === -1) {
    return [];
  }

  const indices = [firstVisibleTickIndex, lastVisibleTickIndex];

  // In case of an asymmetric gauge determine the short side first and find the center index between the short side and the center.
  // Then find the opposite index of that center index to ensure the opposite tick is placed in a visually balanced way.
  const shortSideOuterIndex =
    firstVisibleTickIndex > 0 ? firstVisibleTickIndex : lastVisibleTickIndex;
  const quarterIndex = mmath.avg(shortSideOuterIndex, AMOUNT_OF_POINTS_PER_SIDE);
  const offsetToMiddle = Math.abs(shortSideOuterIndex - AMOUNT_OF_POINTS_PER_SIDE);

  // If the outer tick is further away from the middle than the threshold, we add another tick in between and the opposite of that tick.
  if (offsetToMiddle > EXTRA_TICK_THRESHOLD) {
    indices.push(quarterIndex);
    indices.push(getOpposite(quarterIndex, AMOUNT_OF_POINTS_PER_SIDE));
  }
  // Otherwise we only add the opposite of the outer tick.
  else {
    indices.push(getOpposite(shortSideOuterIndex, AMOUNT_OF_POINTS_PER_SIDE));
  }

  return Array.from(new Set(indices.map(roundIndexAwayFromMiddle))).map(
    (index) => tickValues[index],
  );
};

export const createGaugeContext = (props: GaugeRootProps): GaugeRootContext => {
  const thresholds = toRef(props, "thresholds");
  const scale = toRef(props, "scale");

  const target = computed(() =>
    thresholds.value?.target === undefined
      ? (scale.value[0] + scale.value[1]) / 2
      : thresholds.value?.target,
  );

  const currentValue = computed(() => props.currentValue ?? target.value);

  const targetRange = computed(() =>
    makeRange(thresholds.value?.warningLow, thresholds.value?.warningHigh, scale.value),
  );

  const warningRange = computed(() =>
    makeRange(thresholds.value?.alarmLow, thresholds.value?.alarmHigh, scale.value),
  );

  const ticks = computed(() =>
    createPoints(scale.value, targetRange.value, warningRange.value, target.value, currentValue),
  );

  const tickLabels = computed(() => getTicks(ticks.value));

  return {
    target,
    targetRange,
    ...toRefs(props),
    points: ticks,
    ticks: tickLabels,
  };
};

export const [getGaugeRootContext, provideGaugeRootContext] =
  createContext<GaugeRootContext>("GaugeRoot");

export const getOpposite = (item: number, mirror: number) => mirror + (mirror - item);
