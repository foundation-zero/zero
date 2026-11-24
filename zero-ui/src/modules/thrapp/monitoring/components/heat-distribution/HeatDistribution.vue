<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { PANEL_GRID } from "@/modules/thrapp/monitoring/monitoring.consts";
import type { TotalRow } from "@/modules/thrapp/monitoring/monitoring.types";
import { useCssColors } from "@/modules/thrapp/monitoring/monitoring.utils";
import { PieChart, TreemapChart } from "echarts/charts";
import { TooltipComponent } from "echarts/components";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed, useTemplateRef } from "vue";
import VChart from "vue-echarts";
import { formatReading } from "../latest-values-table/latest-values-table.utils";
import { MonitoringCard } from "../monitoring-card";
import { delivered, pieOption, share, treemapOption } from "./heat-distribution.utils";

use([CanvasRenderer, TreemapChart, PieChart, TooltipComponent]);

/**
 * How the heat of the range splits over the sources: a treemap beside the
 * charts, and a pie with the shares in the narrow column.
 */
const props = defineProps<{
  rows: TotalRow[];
  unit: string;
  loading?: boolean;
  error?: string;
}>();

const t = tScoped("thrapp.monitoring");
const root = useTemplateRef<HTMLElement>("root");
const { colors } = useCssColors<string>(
  () => ({ label: "var(--inverse-foreground)", surface: "var(--background)" }),
  root,
);

const shown = computed(() => delivered(props.rows));
const captured = computed(() => shown.value.reduce((sum, row) => sum + row.value, 0));
const treemap = computed(() => treemapOption(props.rows, props.unit, colors.value.label));
const pie = computed(() => pieOption(props.rows, props.unit, colors.value.surface));
</script>

<template>
  <div
    ref="root"
    :class="PANEL_GRID"
  >
    <MonitoringCard>
      <div class="font-ui flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <h4 class="text-foreground text-sm font-semibold">
          {{ t("distribution.treemap") }}
        </h4>
        <p
          v-if="shown.length"
          class="text-muted-foreground text-sm"
        >
          {{ t("distribution.captured") }}
          <span class="text-foreground ml-1 text-lg font-semibold tabular-nums">
            {{ formatReading(captured, props.unit) }}
          </span>
        </p>
      </div>
      <div class="relative h-64 lg:h-72">
        <VChart
          v-if="shown.length"
          :option="treemap"
          :update-options="{ notMerge: true }"
          :class="{ 'opacity-60': props.loading }"
          autoresize
        />
        <p
          v-else
          class="absolute inset-0 flex items-center justify-center text-sm"
          :class="props.error ? 'text-destructive' : 'text-muted-foreground'"
        >
          {{
            props.error
              ? t("chart.error", { message: props.error })
              : props.loading
                ? "…"
                : t("distribution.noHeat")
          }}
        </p>
      </div>
    </MonitoringCard>
    <MonitoringCard>
      <h4 class="font-ui text-foreground text-sm font-semibold">
        {{ t("distribution.pie") }}
      </h4>
      <div
        v-if="shown.length"
        class="flex items-center gap-4"
        :class="{ 'opacity-60': props.loading }"
      >
        <div class="size-32 shrink-0">
          <VChart
            :option="pie"
            :update-options="{ notMerge: true }"
            autoresize
          />
        </div>
        <table class="font-ui text-foreground min-w-0 grow table-fixed text-sm">
          <tbody>
            <tr
              v-for="row in shown"
              :key="row.asset"
            >
              <td class="py-1 pr-2 font-medium">
                <span class="flex min-w-0 items-center gap-2">
                  <span
                    class="size-2.5 shrink-0 rounded-xs"
                    :style="{ backgroundColor: row.color }"
                    aria-hidden="true"
                  />
                  <span class="truncate">{{ row.shortName ?? row.asset }}</span>
                </span>
              </td>
              <td
                class="w-12 py-1 text-right tabular-nums"
                :title="formatReading(row.value, props.unit)"
              >
                {{ share(row.value, shown) }}%
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </MonitoringCard>
  </div>
</template>
