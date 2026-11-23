<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { PANEL_GRID } from "@/modules/thrapp/monitoring/monitoring.consts";
import type {
  ResolvedRange,
  SignalStates,
  StatePanelConfig,
} from "@/modules/thrapp/monitoring/monitoring.types";
import { useStateStyles } from "@/modules/thrapp/monitoring/monitoring.utils";
import { computed } from "vue";
import { MonitoringCard } from "../monitoring-card";
import { StateDistribution } from "../state-distribution";
import { StateTimeline } from "../state-timeline";
import { panelRows, panelTotals } from "./state-panel.utils";

/** The timeline of a panel's signals, with the time per state beside it. */
const props = defineProps<{
  config: StatePanelConfig;
  states: SignalStates[];
  range: ResolvedRange;
  loading?: boolean;
  error?: string;
}>();

const emit = defineEmits<{ zoom: [range: ResolvedRange] }>();

const t = tScoped("thrapp.monitoring");
const styleOf = useStateStyles();

const rows = computed(() =>
  panelRows(props.config, props.states, styleOf, ({ key, params }) =>
    params ? t(`rows.${key}`, params) : t(`rows.${key}`),
  ),
);
const totals = computed(() => panelTotals(props.config, props.states, props.range, styleOf));
</script>

<template>
  <div :class="PANEL_GRID">
    <MonitoringCard class="justify-center">
      <StateTimeline
        :rows="rows"
        :range="props.range"
        :loading="props.loading"
        :error="props.error"
        @zoom="emit('zoom', $event)"
      >
        <template #overlay>
          <slot name="overlay" />
        </template>
      </StateTimeline>
    </MonitoringCard>
    <MonitoringCard class="justify-center">
      <StateDistribution
        :header="t(`distribution.${props.config.header}`)"
        :totals="totals"
        :loading="props.loading"
        :error="props.error"
      />
    </MonitoringCard>
  </div>
</template>
