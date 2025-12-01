<script setup lang="ts">
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { tScoped } from "@/modules/common/lib/utils";
import { ChartDataType, SeriesChart } from "@common/types";
import { formatDistanceToNow, isValid } from "date-fns";
import { computed, inject, Ref } from "vue";
import { ChartCard, ChartCardContent, ChartCardTitle } from "../chart-card";

const t = tScoped("thrs.components.valueTable");

type FieldEntry = { name: string; value: string; timestamp: string };

const props = defineProps<{
  format: (value: number) => string;
}>();

const series = inject<Ref<SeriesChart<ChartDataType>[]>>("fieldSeries")!;
const field = inject<Ref<string>>("field")!;

const lastEntries = computed<FieldEntry[]>(() =>
  series.value
    .filter((entry) => entry.data.length > 0)
    .map((entry) => {
      const [timestamp, value] = entry.data[entry.data.length - 1];

      return {
        name: entry.name,
        value: Number.isFinite(value) ? props.format(Number(value)) : String(value),
        timestamp: isValid(new Date(timestamp))
          ? formatDistanceToNow(new Date(timestamp), { addSuffix: true })
          : "N/A",
      };
    }),
);
</script>
<template>
  <ChartCard
    v-if="lastEntries.length"
    class="px-0"
  >
    <ChartCardTitle class="px-3">{{ field }}</ChartCardTitle>
    <ChartCardContent>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead class="pl-3">{{ t("property") }}</TableHead>
            <TableHead>{{ t("value") }}</TableHead>
            <TableHead class="pr-3">{{ t("lastChange") }}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow
            v-for="{ name, value, timestamp } in lastEntries"
            :key="name"
          >
            <TableCell class="w-1/2 p-2 pl-3">{{ name }}</TableCell>
            <TableCell class="w-1/4 p-2 font-mono text-xs">{{ value }}</TableCell>
            <TableCell class="text-muted-foreground w-1/4 p-2 pr-3 text-xs">{{
              timestamp
            }}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </ChartCardContent>
  </ChartCard>
</template>
