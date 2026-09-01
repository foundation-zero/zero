<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/modules/common/lib/utils";
import { RiAlertLine } from "@remixicon/vue";
import { HTMLAttributes, ref, toRefs, watch } from "vue";
import { useI18n } from "vue-i18n";
import { LOAD_UNIT } from "../../lib/consts";
import { formatLoad } from "../../lib/utils";
import { useAlarmsStore } from "../../stores/alarms";
import { VariableUnit } from "../../types";

const { t } = useI18n();

const { status: alarmsStatus, activeAlarms } = toRefs(useAlarmsStore());

const getFormattedValue = (value: number | null, unit: string) =>
  formatLoad(value, unit as VariableUnit);
const getDisplayUnit = (unit: string) => (LOAD_UNIT as Record<string, string>)[unit] ?? unit;

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
            {
              'opacity-0': alarmsStatus === 'ok',
              'alarm-glow opacity-100': alarmsStatus === 'alarm',
            },
            props.class,
          )
        "
        variant="destructive"
      >
        <RiAlertLine class="size-4!" />
        {{ t("loads.dashboard.alarms", { count: activeAlarms.length }) }}
      </Badge>
    </PopoverTrigger>
    <PopoverContent class="mt-3 grid gap-y-2 border-0 bg-transparent p-0">
      <hgroup
        v-for="alarm in activeAlarms"
        :key="alarm.id"
        data-slot="alert"
        class="bg-background border-destructive-dull text-foreground grid gap-2 rounded-md border px-6 py-4"
      >
        <header class="flex items-center gap-3 text-xl font-bold">
          {{ alarm.name }}
        </header>
        <p
          class="text-sm font-normal"
          v-html="
            t('loads.dashboard.alarmActive', {
              alarm: alarm.name,
              actualValue: getFormattedValue(alarm.actualValue, alarm.actual.variable.unit),
              thresholdValue: getFormattedValue(alarm.thresholdValue, alarm.actual.variable.unit),
              unit: getDisplayUnit(alarm.actual.variable.unit),
            })
          "
        ></p>
      </hgroup>
    </PopoverContent>
  </Popover>
</template>

<style scoped>
.alarm-glow {
  /* Match Figma glow state while keeping it subtle in motion. */
  animation: alarmGlowPulse 1.6s ease-in-out infinite;
  box-shadow: 0 0 4px 4px var(--destructive-muted);
}

[data-slot="alert"] {
  background:
    linear-gradient(
      180deg,
      oklch(from var(--color-destructive) l c h / 0),
      oklch(from var(--color-destructive) l c h / 0.1) 100%
    ),
    var(--color-background);
}

@keyframes alarmGlowPulse {
  0%,
  100% {
    box-shadow: 0 0 3px 3px color-mix(in srgb, var(--destructive-muted) 70%, transparent);
  }

  50% {
    box-shadow: 0 0 6px 6px var(--destructive-muted);
  }
}
</style>
