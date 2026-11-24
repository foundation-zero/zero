<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { STALE_AFTER } from "@/modules/thrapp/monitoring/monitoring.consts";
import type { LatestValueRow } from "@/modules/thrapp/monitoring/monitoring.types";
import { useIntervalFn, useNow } from "@vueuse/core";
import { format } from "date-fns";
import { computed } from "vue";
import { formatAge, formatReading } from "./latest-values-table.utils";

/** The newest reading per asset and how long ago it arrived, as Grafana's Live tables. */
const props = defineProps<{
  rows: LatestValueRow[];
  /** Header of the value column, e.g. "Level". */
  valueHeader: string;
  unit?: string | null;
  /** Adds a row with the sum, where adding up makes sense (tank levels). */
  totals?: boolean;
}>();

const t = tScoped("thrapp.monitoring.table");
const now = useNow({ scheduler: (tick) => useIntervalFn(tick, 1000) });

const total = computed(() => {
  const values = props.rows.flatMap((row) => (row.value === null ? [] : [row.value]));
  return values.length ? values.reduce((sum, value) => sum + value, 0) : null;
});
const isStale = (row: LatestValueRow) =>
  row.timestamp !== null && now.value.getTime() - row.timestamp >= STALE_AFTER;
</script>

<template>
  <section class="border-border bg-background font-ui relative min-w-0 rounded-lg border">
    <!-- Beside a chart it takes the chart's height and scrolls, rather than stretching it. -->
    <div class="flex max-h-[290px] flex-col lg:absolute lg:inset-0 lg:max-h-none">
      <h4 class="text-foreground px-4 pt-4 pb-1 text-sm font-semibold">{{ t("title") }}</h4>
      <div class="min-h-0 overflow-y-auto px-3 pb-3">
        <table class="text-foreground w-full table-fixed text-sm">
          <thead class="bg-background sticky top-0">
            <tr class="border-border border-b text-left">
              <th class="text-muted-foreground py-2 pr-3 font-semibold">{{ t("asset") }}</th>
              <th
                class="text-muted-foreground w-[96px] py-2 pr-3 text-right font-semibold whitespace-nowrap"
              >
                {{ props.valueHeader }}
              </th>
              <th
                class="text-muted-foreground w-[72px] py-2 text-right text-xs font-semibold whitespace-nowrap"
              >
                {{ t("lastChange") }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in props.rows"
              :key="row.asset"
              class="border-border-subtle border-b last:border-b-0"
            >
              <td class="py-2 pr-3">
                <span class="flex min-w-0 items-start gap-2">
                  <svg
                    v-if="row.color"
                    width="12"
                    height="4"
                    class="mt-2 shrink-0"
                    aria-hidden="true"
                  >
                    <line
                      x1="0"
                      y1="2"
                      x2="12"
                      y2="2"
                      stroke-width="3"
                      stroke-linecap="round"
                      :stroke="row.color"
                      :stroke-dasharray="row.dashed ? '4 3' : undefined"
                    />
                  </svg>
                  <span
                    class="min-w-0 font-medium break-words"
                    :title="row.asset"
                  >
                    {{ row.shortName ?? row.asset }}
                  </span>
                </span>
              </td>
              <td class="py-2 pr-3 text-right font-medium whitespace-nowrap tabular-nums">
                {{ formatReading(row.value, props.unit) }}
              </td>
              <td
                class="py-2 text-right text-xs whitespace-nowrap tabular-nums"
                :class="isStale(row) ? 'text-warning' : 'text-disabled-foreground'"
                :title="
                  row.timestamp === null ? undefined : format(row.timestamp, 'dd-MM-yyyy HH:mm:ss')
                "
              >
                {{
                  row.timestamp === null
                    ? t("never")
                    : t("ago", { age: formatAge(now.getTime() - row.timestamp) })
                }}
              </td>
            </tr>
          </tbody>
          <tfoot v-if="props.totals">
            <tr class="border-border border-t">
              <td class="py-2 pr-3 font-semibold">{{ t("totals") }}</td>
              <td class="py-2 pr-3 text-right font-semibold whitespace-nowrap tabular-nums">
                {{ formatReading(total, props.unit) }}
              </td>
              <td />
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </section>
</template>
