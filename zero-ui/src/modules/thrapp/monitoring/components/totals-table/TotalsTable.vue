<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import type { TotalRow } from "@/modules/thrapp/monitoring/monitoring.types";
import { computed } from "vue";
import { formatReading } from "../latest-values-table";

/**
 * What each device delivered or used over the range, with its share and the
 * sum, beside a stacked or bar chart; the swatches match the chart.
 */
const props = withDefaults(
  defineProps<{
    title: string;
    assetHeader: string;
    valueHeader: string;
    unit: string;
    rows: TotalRow[];
    /** Each row's share of the sum; off where the rows don't add up to a whole. */
    shares?: boolean;
    /** A row with the sum of the rows. */
    sum?: boolean;
  }>(),
  { shares: true, sum: true },
);

const t = tScoped("thrapp.monitoring.table");

const counted = computed(() => props.rows.filter((row) => !row.derived));
const total = computed(() => counted.value.reduce((sum, row) => sum + row.value, 0));
const share = (value: number) =>
  total.value > 0 ? `${Math.round((value / total.value) * 100)}%` : "–";
</script>

<template>
  <section class="border-border bg-background font-ui relative min-w-0 rounded-lg border">
    <div class="flex max-h-[290px] flex-col lg:absolute lg:inset-0 lg:max-h-none">
      <h4 class="text-foreground px-4 pt-4 pb-1 text-sm font-semibold">{{ props.title }}</h4>
      <div class="min-h-0 overflow-y-auto px-4 pb-3">
        <table class="text-foreground w-full table-fixed text-sm">
          <thead class="bg-background sticky top-0">
            <tr class="border-border border-b text-left">
              <th class="text-muted-foreground py-2 pr-3 font-semibold">{{ props.assetHeader }}</th>
              <th
                class="text-muted-foreground w-28 py-2 pr-3 text-right font-semibold whitespace-nowrap"
              >
                {{ props.valueHeader }}
              </th>
              <th class="text-muted-foreground w-14 py-2 text-right font-semibold">
                {{ props.shares ? t("share") : "" }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in props.rows"
              :key="row.asset"
              class="border-border-subtle border-b last:border-b-0"
              :class="{ 'border-border text-muted-foreground border-t': row.derived }"
            >
              <td class="py-2.5 pr-3">
                <span class="flex min-w-0 items-start gap-2.5">
                  <span
                    v-if="row.color"
                    class="mt-1 size-3 shrink-0 rounded-xs"
                    :style="{ backgroundColor: row.color }"
                    aria-hidden="true"
                  />
                  <span
                    class="min-w-0 font-medium break-words"
                    :title="row.asset"
                  >
                    {{ row.shortName ?? row.asset }}
                  </span>
                </span>
              </td>
              <td class="py-2.5 pr-3 text-right font-medium whitespace-nowrap tabular-nums">
                {{ formatReading(row.value, props.unit) }}
              </td>
              <td class="text-muted-foreground py-2.5 text-right whitespace-nowrap tabular-nums">
                {{ row.derived || !props.shares ? "" : share(row.value) }}
              </td>
            </tr>
          </tbody>
          <tfoot v-if="props.sum">
            <tr class="border-border border-t">
              <td class="py-2.5 pr-3 font-semibold">{{ t("totals") }}</td>
              <td class="py-2.5 pr-3 text-right font-semibold whitespace-nowrap tabular-nums">
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
