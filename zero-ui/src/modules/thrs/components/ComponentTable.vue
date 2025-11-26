<script setup lang="ts">
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Component } from "@common/types";
import { formatDistanceToNow } from "date-fns";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

defineProps<{
  values: Component;
  format: (value: number) => string;
}>();
</script>
<template>
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead class="pl-3">{{ t("components.thrs.valueTable.component") }}</TableHead>
        <TableHead class="pl-3">{{ t("components.thrs.valueTable.property") }}</TableHead>
        <TableHead>{{ t("components.thrs.valueTable.value") }}</TableHead>
        <TableHead>{{ t("components.thrs.valueTable.lastChange") }}</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <template
        v-for="(component, componentName) in values"
        :key="componentName"
      >
        <TableRow
          v-for="(value, property) in component"
          :key="property"
        >
          <TableCell class="w-1/2 p-2 pl-3">{{ componentName }}</TableCell>
          <TableCell class="w-1/2 p-2 pl-3">{{ property }}</TableCell>
          <TableCell class="w-1/4 p-2 font-mono text-xs">{{
            Number.isFinite(value.value) ? format(Number(value.value)) : value.value
          }}</TableCell>
          <TableCell class="text-muted-foreground w-1/4 p-2 text-xs">{{
            formatDistanceToNow(value.timestamp, { addSuffix: true })
          }}</TableCell>
        </TableRow>
      </template>
    </TableBody>
  </Table>
</template>
