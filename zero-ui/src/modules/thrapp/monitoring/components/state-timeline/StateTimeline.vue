<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { MODE_COLORS } from "@/modules/thrapp/mimics/components/mode-badge/mode-badge.consts";
import { PLOT_INSET } from "@/modules/thrapp/monitoring/monitoring.consts";
import type {
  ResolvedRange,
  StyledSegment,
  TimelineRow,
} from "@/modules/thrapp/monitoring/monitoring.types";
import {
  timeTicks,
  tickLabel,
  useDurationFormat,
  usePlotDrag,
} from "@/modules/thrapp/monitoring/monitoring.utils";
import { useElementSize } from "@vueuse/core";
import { format } from "date-fns";
import { computed, ref, useTemplateRef } from "vue";
import { HoverTooltip } from "../hover-tooltip";
import { fitsLabel, placeSegments } from "./state-timeline.utils";

/**
 * One bar per signal, split into the states it was in, over a shared time axis.
 * The labels take the same width as a chart's value axis, so the time axes of
 * timelines and charts line up; drag across the bars to zoom.
 */
const props = defineProps<{
  rows: TimelineRow[];
  range: ResolvedRange;
  loading?: boolean;
  error?: string;
}>();

const emit = defineEmits<{ zoom: [range: ResolvedRange] }>();

const t = tScoped("thrapp.monitoring");
const formatDuration = useDurationFormat();

const root = useTemplateRef<HTMLElement>("root");
const { width: rootWidth } = useElementSize(root);
const trackWidth = computed(() => rootWidth.value - PLOT_INSET.left - PLOT_INSET.right);

const placed = computed(() =>
  props.rows.map((row) => ({ ...row, segments: placeSegments(row.segments, props.range) })),
);
const ticks = computed(() =>
  timeTicks(props.range).map((tick) => ({
    left: ((tick - props.range.start) / (props.range.end - props.range.start)) * 100,
    label: tickLabel(tick, props.range),
  })),
);

const { selection, dragging } = usePlotDrag(
  root,
  () => props.range,
  PLOT_INSET,
  (range) => emit("zoom", range),
);

const hovered = ref<{ segment: StyledSegment; x: number; y: number } | null>(null);
const hover = (segment: StyledSegment, event: MouseEvent) => {
  if (dragging.value) return;
  hovered.value = { segment, x: event.clientX, y: event.clientY };
};
const spanLabel = ({ start, end }: StyledSegment) =>
  `${format(start, "dd MMM HH:mm")} – ${format(end, "HH:mm")}`;
</script>

<template>
  <p
    v-if="props.error"
    class="text-destructive text-sm"
  >
    {{ t("chart.error", { message: props.error }) }}
  </p>
  <div
    v-else
    ref="root"
    class="font-ui text-foreground relative grid cursor-crosshair items-center gap-y-3 select-none"
    :class="{ 'opacity-60': props.loading }"
    :style="{
      gridTemplateColumns: `${PLOT_INSET.left}px minmax(0, 1fr)`,
      paddingRight: `${PLOT_INSET.right}px`,
    }"
    @mouseleave="hovered = null"
  >
    <template
      v-for="row in placed"
      :key="row.label"
    >
      <span class="truncate pr-3 text-sm font-medium">{{ row.label }}</span>
      <div class="bg-muted relative h-7.5 overflow-hidden rounded-xs">
        <div
          v-for="segment in row.segments"
          :key="segment.start"
          class="text-inverse-foreground absolute inset-y-0 flex items-center justify-center overflow-hidden border-x border-transparent bg-clip-padding text-sm font-medium transition-opacity"
          :class="{ 'opacity-70': hovered?.segment === segment }"
          :style="{
            left: `${segment.left}%`,
            width: `${segment.width}%`,
            backgroundColor: MODE_COLORS[segment.mode],
          }"
          @mousemove="hover(segment, $event)"
          @mouseleave="hovered = null"
        >
          <span
            v-if="fitsLabel(segment.label, (segment.width / 100) * trackWidth)"
            class="truncate px-2"
          >
            {{ segment.label }}
          </span>
        </div>
        <span
          v-if="!row.segments.length"
          class="text-muted-foreground absolute inset-0 flex items-center px-2 text-sm"
        >
          {{ props.loading ? "…" : t("chart.empty") }}
        </span>
      </div>
    </template>

    <span />
    <div
      class="border-border relative h-6 border-t"
      aria-hidden="true"
    >
      <span
        v-for="tick in ticks"
        :key="tick.left"
        class="text-muted-foreground absolute top-0 -translate-x-1/2 pt-2 text-[10px] leading-[10px] before:absolute before:top-0 before:left-1/2 before:h-1.5 before:border-l before:border-current"
        :style="{ left: `${tick.left}%` }"
      >
        {{ tick.label }}
      </span>
    </div>

    <slot
      name="overlay"
      :track-width="trackWidth"
    />

    <div
      v-if="selection"
      class="bg-primary/10 border-primary/50 pointer-events-none absolute inset-y-0 border-x"
      :style="{ left: `${selection.left}px`, width: `${selection.width}px` }"
    />

    <HoverTooltip :at="hovered">
      <template v-if="hovered">
        <span class="font-semibold">{{ hovered.segment.label }}</span>
        <br />
        {{ spanLabel(hovered.segment) }} ·
        {{ formatDuration((hovered.segment.end - hovered.segment.start) / 1000) }}
      </template>
    </HoverTooltip>
  </div>
</template>
