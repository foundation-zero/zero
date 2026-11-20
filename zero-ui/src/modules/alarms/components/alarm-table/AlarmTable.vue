<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useI18n } from "vue-i18n";
import type { Alarm } from "../../types";
import { PRIORITY_BADGE } from "./alarm-table.consts";
import { formatAlarmTime } from "./alarm-table.utils";

const props = defineProps<{
  alarms: Alarm[];
  /** Alarms that are no longer active are dimmed. */
  ended?: boolean;
}>();

const { t } = useI18n();

const rowKey = (alarm: Alarm) => `${alarm.system}/${alarm.tag}/${alarm.location}`;
</script>

<template>
  <div class="bg-background border-border-subtle w-full rounded-md border">
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead class="px-4">{{ t("alarms.columns.priority") }}</TableHead>
          <TableHead class="w-full px-4">{{ t("alarms.columns.alarm") }}</TableHead>
          <TableHead class="px-4">{{ t("alarms.columns.location") }}</TableHead>
          <TableHead class="px-4">{{ t("alarms.columns.status") }}</TableHead>
          <TableHead class="px-4 text-right whitespace-nowrap">
            {{ t("alarms.columns.activatedAt") }}
          </TableHead>
          <TableHead class="px-4 text-right whitespace-nowrap">
            {{ t("alarms.columns.lastChangeAt") }}
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow
          v-for="alarm in props.alarms"
          :key="rowKey(alarm)"
          data-testid="alarm-row"
          :data-acknowledged="alarm.acknowledged"
          :class="{ 'opacity-60': props.ended }"
        >
          <TableCell>
            <Badge :variant="PRIORITY_BADGE[alarm.priority ?? 'UNKNOWN']">
              {{ t(`alarms.priorities.${alarm.priority ?? "UNKNOWN"}`) }}
            </Badge>
          </TableCell>
          <TableCell class="max-w-0">
            <div class="truncate font-medium">
              {{ alarm.description ?? alarm.tag ?? "—" }}
            </div>
            <div class="text-muted-foreground truncate text-xs">
              {{ [alarm.system, alarm.tag].filter(Boolean).join(" · ") }}
            </div>
          </TableCell>
          <TableCell class="whitespace-nowrap">{{ alarm.location ?? "—" }}</TableCell>
          <TableCell>
            <Badge
              v-if="!alarm.acknowledged"
              variant="destructive"
            >
              {{ t("alarms.status.unacknowledged") }}
            </Badge>
            <Badge
              v-else
              variant="outline"
            >
              {{ t("alarms.status.acknowledged") }}
            </Badge>
          </TableCell>
          <TableCell class="text-right whitespace-nowrap tabular-nums">
            {{ formatAlarmTime(alarm.activatedAt) }}
          </TableCell>
          <TableCell class="text-right whitespace-nowrap tabular-nums">
            {{ formatAlarmTime(alarm.lastChangeAt) }}
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>
