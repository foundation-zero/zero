<script setup lang="ts">
import { mmath } from "@/modules/common/lib/utils";
import { useRafFn } from "@vueuse/core";
import { computed, ref, watch } from "vue";
import {
  ARC_END_ANGLE,
  ARC_START_ANGLE,
  describeArc,
  GAUGE_CENTER,
  GAUGE_RADIUS,
  getGaugeRootContext,
} from ".";

withDefaults(
  defineProps<{
    arcStrokeWidth?: number;
    rangeStrokeWidth?: number;
    arcColor?: string;
    rangeColor?: string;
  }>(),
  {
    arcStrokeWidth: 1,
    rangeStrokeWidth: 3,
    arcColor: "var(--color-muted)",
    rangeColor: "var(--color-constructive)",
  },
);

const context = getGaugeRootContext();

// Main arc path (background)
const backgroundArcPath = describeArc(
  GAUGE_CENTER.x,
  GAUGE_CENTER.y,
  GAUGE_RADIUS,
  ARC_START_ANGLE,
  ARC_END_ANGLE,
);

const ANIMATION_DURATION = 300; // ms
const CENTER_ANGLE = 270;

const animatedRangeStartAngle = ref(CENTER_ANGLE);
const animatedRangeEndAngle = ref(CENTER_ANGLE);

type AngleRange = { start: number; end: number };

let startTime: number = 0;
let startAngle: AngleRange = { start: CENTER_ANGLE, end: CENTER_ANGLE };
let targetAngle: AngleRange = { start: CENTER_ANGLE, end: CENTER_ANGLE };

const { pause, resume } = useRafFn(() => {
  const elapsed = performance.now() - startTime;
  const progress = Math.min(elapsed / ANIMATION_DURATION, 1);

  const eased = 1 - Math.pow(1 - progress, 3);

  animatedRangeStartAngle.value = startAngle.start + (targetAngle.start - startAngle.start) * eased;
  animatedRangeEndAngle.value = startAngle.end + (targetAngle.end - startAngle.end) * eased;

  if (progress >= 1) {
    pause();
  }
});

watch(
  [context.scale, context.target, context.targetRange],
  ([scale, target, targetRange]) => {
    const [scaleMin, scaleMax] = scale;
    const [targetMin, targetMax] = targetRange;

    const distanceToMin = Math.abs(target - scaleMin);
    const distanceToMax = Math.abs(scaleMax - target);
    const maxDistance = Math.max(distanceToMin, distanceToMax);
    const degreesPerUnit = 90 / maxDistance;

    const targetStartAngle = CENTER_ANGLE + (targetMin - target) * degreesPerUnit;
    const targetEndAngle = CENTER_ANGLE + (targetMax - target) * degreesPerUnit;

    startTime = performance.now();
    startAngle = { start: animatedRangeStartAngle.value, end: animatedRangeEndAngle.value };
    targetAngle = {
      start: mmath.normalizeDegrees(targetStartAngle),
      end: mmath.normalizeDegrees(targetEndAngle),
    };

    resume();
  },
  { deep: true, immediate: true },
);

const animatedRangeArcPath = computed(() =>
  describeArc(
    GAUGE_CENTER.x,
    GAUGE_CENTER.y,
    GAUGE_RADIUS,
    animatedRangeStartAngle.value,
    animatedRangeEndAngle.value,
  ),
);

const hasTargetRange = computed(
  () =>
    context.thresholds?.value?.warningLow !== undefined &&
    context.thresholds?.value?.warningHigh !== undefined,
);
</script>

<template>
  <g>
    <path
      :d="backgroundArcPath"
      fill="none"
      :stroke="arcColor"
      :stroke-width="arcStrokeWidth"
      stroke-linecap="round"
    />

    <path
      v-if="hasTargetRange"
      :d="animatedRangeArcPath"
      fill="none"
      :stroke="rangeColor"
      :stroke-width="rangeStrokeWidth"
      stroke-linecap="round"
    />
  </g>
</template>
