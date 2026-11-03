<script setup lang="ts">
import { SimpleInfoTooltip } from "@/modules/common/components/info-tooltip";
import { formatNumber } from "@/modules/common/lib/utils";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { useTranslations } from "..";
import { ModuleField, SensorValue } from "../../providers";
import { FieldRenderer } from "../../renderers";
import * as Partials from "./";
import { computed } from "vue";

const { items, sources, units } = useTranslations();

// Fixed values: the DHW circuits use fresh water, all other circuits a 20% glycol mix.
const HEAT_CAPACITY = {
  freshWater: 4.18,
  glycolMix: 3.93,
} as const;

const props = withDefaults(
  defineProps<{
    source: ModuleField<SensorComponentType.HeatTransferDevice>;
    heatExchange?: boolean;
  }>(),
  {
    heatExchange: true,
  },
);

const medium = computed(() => (props.source[1] === "dhw" ? "freshWater" : "glycolMix"));
</script>

<template>
  <SensorValue
    v-if="heatExchange"
    :source="source"
    field="heat"
  >
    <Partials.ListItem>
      {{ items("heatExchange") }}
      <template #source>
        <FieldRenderer.Source no-link>{{ sources("calculated") }}</FieldRenderer.Source>
        <SimpleInfoTooltip description="heatExchange" />
      </template>
    </Partials.ListItem>
  </SensorValue>

  <SensorValue
    :source="source"
    field="deltaT"
  >
    <Partials.ListItem no-source>
      {{ items("deltaTemperature") }}
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    :source="source"
    field="temperatureSupply"
  >
    <Partials.ListItem size="sm">
      {{ items("incomingTemperature") }}
      <template #source>
        <FieldRenderer.Source api-only />
      </template>
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    :source="source"
    field="temperatureReturn"
  >
    <Partials.ListItem size="sm">
      {{ items("outgoingTemperature") }}
      <template #source>
        <FieldRenderer.Source api-only />
      </template>
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    :source="source"
    field="flow"
  >
    <Partials.ListItem>
      {{ items("flow") }}
      <template #source>
        <FieldRenderer.Source api-only />
      </template>
    </Partials.ListItem>
  </SensorValue>

  <Partials.ListItem>
    {{ items("heatCapacity") }}
    <template #source>
      <FieldRenderer.Source no-link>{{ sources(medium) }}</FieldRenderer.Source>
    </template>
    <template #renderer>
      <FieldRenderer.Number
        class="gap-1"
        :value="HEAT_CAPACITY[medium]"
        :format="formatNumber(2)"
        :unit="units('heatCapacity')"
      />
    </template>
  </Partials.ListItem>
</template>
