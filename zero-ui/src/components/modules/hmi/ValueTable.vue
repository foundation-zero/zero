<script setup lang="ts">
import { ChartDataType } from "@/@types";
import { Stamped } from "@/@types/thrs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/shadcn/table";
import { formatDistanceToNow, isValid } from "date-fns";
import { useI18n } from "vue-i18n";

type FieldEntry = [componentName: string, value: Stamped<ChartDataType>];

const { t } = useI18n();

defineProps<{
  values: FieldEntry[];
  format: (value: number) => string;
}>();
</script>
<template>
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead class="pl-3">{{ t("components.thrs.valueTable.property") }}</TableHead>
        <TableHead>{{ t("components.thrs.valueTable.value") }}</TableHead>
        <TableHead>{{ t("components.thrs.valueTable.lastChange") }}</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow
        v-for="[componentName, value] in values"
        :key="componentName"
      >
        <TableCell class="w-1/2 p-2 pl-3">{{ componentName }}</TableCell>
        <TableCell class="w-1/4 p-2 font-mono text-xs">{{
          Number.isFinite(value.value) ? format(Number(value.value)) : value.value
        }}</TableCell>
        <TableCell class="text-muted-foreground w-1/4 p-2 text-xs">{{
          isValid(new Date(value.timestamp))
            ? formatDistanceToNow(value.timestamp, { addSuffix: true })
            : "N/A"
        }}</TableCell>
      </TableRow>
    </TableBody>
  </Table>
</template>
