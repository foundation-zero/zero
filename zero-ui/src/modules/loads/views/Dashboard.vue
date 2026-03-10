<script setup lang="ts">
import { onMounted, onUnmounted, toRefs } from "vue";
import {
  VariableGrid,
  VariableGridGroup,
  VariableGridHeader,
  VariableGridItem,
} from "../components/variable-grid";

import Badge from "@/components/ui/badge/Badge.vue";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useI18n } from "vue-i18n";
import { useAlarmsStore } from "../stores/alarms";
import { useVariablesStore } from "../stores/variables";

const { selectedDashboard, selectedCardType } = toRefs(useVariablesStore());
const { startPolling: startPollingVariables, stopPolling: stopPollingVariables } =
  useVariablesStore();
const { startPolling: startPollingAlarms, stopPolling: stopPollingAlarms } = useAlarmsStore();
const { status: alarmsStatus, activeAlarms } = toRefs(useAlarmsStore());
const { t } = useI18n();

onMounted(startPollingVariables);
onMounted(startPollingAlarms);
onUnmounted(stopPollingVariables);
onUnmounted(stopPollingAlarms);
</script>

<template>
  <article class="flex flex-col gap-6 pb-4">
    <div class="flex flex-row items-center gap-6">
      <h2 class="text-foreground text-2xl font-semibold">
        {{ t("loads.dashboard.status") }}
      </h2>
      <Badge :variant="alarmsStatus === 'ok' ? 'constructive' : 'destructive'">
        {{ t("loads.dashboard.alarms", { count: activeAlarms.length }) }}
        <Popover v-if="activeAlarms.length > 0">
          <PopoverTrigger as-child>
            <Button class="ml-2">{{ t("loads.dashboard.showAlarms") }}</Button>
          </PopoverTrigger>
          <PopoverContent>
            <ul class="space-y-2">
              <li
                v-for="alarm in activeAlarms"
                :key="alarm.id"
                class="flex items-center justify-between rounded-md border p-4"
              >
                <span>{{
                  t("loads.dashboard.alarmActive", {
                    alarm: alarm.name,
                    actualValue: alarm.actualValue,
                    thresholdValue: alarm.thresholdValue,
                    unit: alarm.actual.variable.unit,
                  })
                }}</span>
              </li>
            </ul>
          </PopoverContent>
        </Popover>
      </Badge>
    </div>
    <VariableGrid :type="selectedCardType">
      <VariableGridGroup
        v-for="group in selectedDashboard.groups"
        :key="group.name"
        :items="group.variables"
      >
        <VariableGridHeader>
          {{ group.name }}
        </VariableGridHeader>

        <template #item="{ variable }">
          <VariableGridItem
            :id="variable.id"
            :variable="variable"
          />
        </template>
      </VariableGridGroup>
    </VariableGrid>
  </article>
</template>
