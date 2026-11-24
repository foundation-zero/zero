<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { tScoped } from "@/modules/common/lib/utils";
import { ANNOTATION_COLORS, PLOT_INSET } from "@/modules/thrapp/monitoring/monitoring.consts";
import type {
  MonitoringAnnotation,
  ResolvedRange,
} from "@/modules/thrapp/monitoring/monitoring.types";
import { placeAnnotations } from "@/modules/thrapp/monitoring/monitoring.utils";
import { RiAlarmWarningLine, RiChat3Line, RiSettings3Line } from "@remixicon/vue";
import { format } from "date-fns";
import { computed } from "vue";

/**
 * Annotations as a thin line across a timeline or chart, with an icon on top
 * that shows the note on hover. Lies over the plot without taking its clicks.
 */
const props = withDefaults(
  defineProps<{
    annotations: MonitoringAnnotation[];
    /** The kinds to show. */
    shown: ReadonlySet<string>;
    range: ResolvedRange;
    /** Space above and below the plot, in px. */
    top?: number;
    bottom?: number;
  }>(),
  { top: 0, bottom: 0 },
);

const emit = defineEmits<{ delete: [annotation: MonitoringAnnotation] }>();

const t = tScoped("thrapp.monitoring.annotations");

const ICONS = { CREW: RiChat3Line, PARAMETERS: RiSettings3Line, ALARM: RiAlarmWarningLine };

const placed = computed(() => placeAnnotations(props.annotations, props.shown, props.range));
const title = (annotation: MonitoringAnnotation) =>
  annotation.kind === "CREW"
    ? annotation.text
    : annotation.kind === "ALARM"
      ? t(`alarm.${annotation.text}`)
      : t("parametersChanged", { count: annotation.changes.length });
</script>

<template>
  <div
    class="pointer-events-none absolute z-10"
    :style="{
      left: `${PLOT_INSET.left}px`,
      right: `${PLOT_INSET.right}px`,
      top: `${props.top}px`,
      bottom: `${props.bottom}px`,
    }"
  >
    <div
      v-for="{ annotation, left } in placed"
      :key="annotation.id"
      class="absolute inset-y-0"
      :style="{ left: `${left}%` }"
    >
      <div
        class="absolute inset-y-0 -translate-x-1/2 border-l"
        :class="annotation.kind === 'PARAMETERS' ? 'border-dashed' : ''"
        :style="{ borderColor: ANNOTATION_COLORS[annotation.kind] }"
      />
      <HoverCard
        :open-delay="80"
        :close-delay="120"
      >
        <HoverCardTrigger as-child>
          <button
            type="button"
            class="text-inverse-foreground pointer-events-auto absolute top-0 flex size-5 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full shadow-sm ring-2 ring-[var(--background)]"
            :style="{ backgroundColor: ANNOTATION_COLORS[annotation.kind] }"
            :aria-label="title(annotation)"
          >
            <component
              :is="ICONS[annotation.kind]"
              class="size-3"
            />
          </button>
        </HoverCardTrigger>
        <HoverCardContent
          side="top"
          class="font-ui flex w-72 flex-col gap-2 text-sm"
        >
          <p class="text-popover-foreground/70 text-xs">
            {{ t(`kinds.${annotation.kind}`) }} ·
            {{ format(Date.parse(annotation.time), "dd MMM HH:mm:ss") }}
          </p>
          <p class="text-popover-foreground font-medium break-words whitespace-pre-line">
            {{ title(annotation) }}
          </p>
          <ul
            v-if="annotation.changes.length"
            class="text-popover-foreground/80 flex flex-col gap-0.5 text-xs"
          >
            <li
              v-for="change in annotation.changes"
              :key="change.name"
              class="flex justify-between gap-3"
            >
              <span class="truncate">{{ change.name }}</span>
              <span class="shrink-0 tabular-nums">
                {{ change.previous ?? "–" }} → {{ change.value ?? "–" }}
              </span>
            </li>
          </ul>
          <p
            v-if="annotation.author"
            class="text-popover-foreground/70 text-xs"
          >
            {{ t("by", { author: annotation.author }) }}
          </p>
          <Button
            v-if="annotation.canDelete"
            size="sm"
            variant="secondary"
            class="self-start"
            @click="emit('delete', annotation)"
          >
            {{ t("delete") }}
          </Button>
        </HoverCardContent>
      </HoverCard>
    </div>
  </div>
</template>
