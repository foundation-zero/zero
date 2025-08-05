<script setup lang="ts">
import { Component } from "@/@types/thrs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/shadcn/table";
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
        <TableHead>{{ t("components.thrs.valueTable.component") }}</TableHead>
        <TableHead>{{ t("components.thrs.valueTable.property") }}</TableHead>
        <TableHead>{{ t("components.thrs.valueTable.value") }}</TableHead>
        <TableHead>{{ t("components.thrs.valueTable.lastChange") }}</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <template
        v-for="(field, component) in values"
        :key="component"
      >
        <TableRow
          v-for="(value, property) in field"
          :key="property"
        >
          <TableCell class="p-2">{{ component }}</TableCell>
          <TableCell class="p-2">{{ property }}</TableCell>
          <TableCell class="p-2">{{
            Number.isFinite(value.value) ? format(value.value) : value.value
          }}</TableCell>
          <TableCell class="p-2">{{ value.timestamp }}</TableCell>
        </TableRow>
      </template>
    </TableBody>
  </Table>
</template>
