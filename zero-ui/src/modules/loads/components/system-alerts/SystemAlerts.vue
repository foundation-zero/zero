<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/modules/common/lib/utils";
import { RiAlertLine } from "@remixicon/vue";
import { HTMLAttributes, ref, toRefs, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useAlarmsStore } from "../../stores/alarms";

const { t } = useI18n();

const { status: alarmsStatus, activeAlarms } = toRefs(useAlarmsStore());

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
const isOpen = ref(false);

watch(alarmsStatus, (newStatus) => {
  isOpen.value = isOpen.value && newStatus === "alarm";
});
</script>

<template>
  <!-- eslint-disable vue/no-v-html -->
  <Popover v-model:open="isOpen">
    <PopoverTrigger>
      <Badge
        :class="
          cn(
            'gap-2 text-sm transition-opacity duration-300',
            { 'opacity-100': alarmsStatus === 'alarm', 'opacity-0': alarmsStatus !== 'alarm' },
            props.class,
          )
        "
        variant="destructive"
      >
        <RiAlertLine />
        {{ t("loads.dashboard.alarms", { count: activeAlarms.length }) }}
      </Badge>
    </PopoverTrigger>
    <PopoverContent class="grid gap-y-2 border-0 bg-transparent p-0">
      <hgroup
        v-for="alarm in activeAlarms"
        :key="alarm.id"
        class="bg-popover grid gap-2 rounded-md px-6 py-4"
      >
        <header class="flex items-center gap-3 text-lg font-semibold">
          <RiAlertLine class="text-destructive-dull inline size-5 flex-shrink-0" />{{ alarm.name }}
        </header>
        <p
          v-html="
            t('loads.dashboard.alarmActive', {
              alarm: alarm.name,
              actualValue: alarm.actualValue,
              thresholdValue: alarm.thresholdValue,
              unit: alarm.actual.variable.unit,
            })
          "
        ></p>
      </hgroup>
    </PopoverContent>
  </Popover>
</template>

<style scoped>
hgroup p :deep(strong) {
  color: var(--destructive-muted);
}
</style>
