<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { MODE_COLORS } from "@/modules/thrapp/mimics/components/mode-badge/mode-badge.consts";
import type { StateTotal } from "@/modules/thrapp/monitoring/monitoring.types";
import { useDurationFormat } from "@/modules/thrapp/monitoring/monitoring.utils";
import { computed, ref } from "vue";
import { HoverTooltip } from "../hover-tooltip";
import { donutArcs } from "./state-distribution.utils";

/** Time spent per state as a small donut, with the same numbers in a table beside it. */
const props = defineProps<{
  /** Header of the state column, e.g. "Mode". */
  header: string;
  totals: StateTotal[];
  loading?: boolean;
  error?: string;
}>();

const t = tScoped("thrapp.monitoring");
const formatDuration = useDurationFormat();

const shown = computed(() => props.totals.filter((total) => total.seconds > 0));
const arcs = computed(() => donutArcs(shown.value.map((total) => total.seconds)));
const totalSeconds = computed(() => shown.value.reduce((sum, total) => sum + total.seconds, 0));
const percent = (seconds: number) => Math.round((seconds / totalSeconds.value) * 100);

const hovered = ref<{ total: StateTotal; x: number; y: number } | null>(null);
const hover = (total: StateTotal, event: MouseEvent) => {
  hovered.value = { total, x: event.clientX, y: event.clientY };
};
</script>

<template>
  <p
    v-if="props.error"
    class="text-destructive text-sm"
  >
    {{ t("chart.error", { message: props.error }) }}
  </p>
  <p
    v-else-if="!shown.length"
    class="text-muted-foreground text-sm"
  >
    {{ props.loading ? "…" : t("distribution.empty") }}
  </p>
  <div
    v-else
    class="relative flex items-center gap-4"
    :class="{ 'opacity-60': props.loading }"
    @mouseleave="hovered = null"
  >
    <svg
      viewBox="0 0 100 100"
      class="size-20 shrink-0 -rotate-90"
      role="img"
      :aria-label="props.header"
    >
      <circle
        v-for="(arc, index) in arcs"
        :key="shown[index].state"
        cx="50"
        cy="50"
        r="40"
        fill="none"
        stroke-width="16"
        :stroke-dasharray="arc.dasharray"
        :stroke-dashoffset="arc.dashoffset"
        :style="{ stroke: MODE_COLORS[shown[index].mode] }"
        :class="{ 'opacity-50': hovered && hovered.total.state !== shown[index].state }"
        class="transition-opacity"
        @mousemove="hover(shown[index], $event)"
      />
    </svg>

    <table class="font-ui text-foreground min-w-0 grow table-fixed text-sm">
      <thead>
        <tr class="text-left">
          <th class="text-muted-foreground pb-2 font-semibold">{{ props.header }}</th>
          <th class="text-muted-foreground w-28 pb-2 text-right font-semibold whitespace-nowrap">
            {{ t("distribution.operationTime") }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="total in shown"
          :key="total.state"
          @mousemove="hover(total, $event)"
        >
          <td class="py-1 pr-3 font-medium">
            <span class="flex items-center gap-2">
              <span
                class="size-2.5 shrink-0 rounded-xs"
                :style="{ backgroundColor: MODE_COLORS[total.mode] }"
                aria-hidden="true"
              />
              <span class="truncate">{{ total.label }}</span>
            </span>
          </td>
          <td class="py-1 text-right whitespace-nowrap tabular-nums">
            {{ formatDuration(total.seconds, 2) }}
          </td>
        </tr>
      </tbody>
    </table>

    <HoverTooltip :at="hovered">
      <template v-if="hovered">
        <span class="font-semibold">{{ hovered.total.label }}</span>
        <br />
        {{ formatDuration(hovered.total.seconds) }} · {{ percent(hovered.total.seconds) }}%
      </template>
    </HoverTooltip>
  </div>
</template>
