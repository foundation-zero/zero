<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { useI18n } from "vue-i18n";
import { ComponentOrientation } from "../../../components";
import Pump from "../../../components/pump/Pump.vue";
import { getTooltipContexts } from "../../../data";
import {
  CircuitLabelInstance,
  FahrenheitInstance,
  PortTemperatureLabelInstance,
} from "../../../instances";

const chillers = getTooltipContexts(MimicComponentType.AdsorptionChiller, ["1034"]);
const { sensors } = chillers["1034"];

const { t } = useI18n();
</script>

<template>
  <!-- Children are positioned in the coordinates of the Fahrenheit unit. -->
  <FahrenheitInstance
    x="782"
    y="49"
    v-bind="chillers['1034']"
  >
    <Pump
      x="20"
      y="141.96"
      :width="34"
      :height="34"
      :orientation="ComponentOrientation.Up"
    />
    <Pump
      x="253"
      y="276.42"
      :width="34"
      :height="34"
      :orientation="ComponentOrientation.Up"
    />
    <Pump
      x="13"
      y="411.13"
      :width="34"
      :height="34"
      :orientation="ComponentOrientation.Up"
    />

    <CircuitLabelInstance
      x="66"
      y="107"
      width="161"
      :title="t('thrapp.mimics.adsorption.chiller.circuits.highTemperature')"
      :heat-transfer="sensors.highTemperature"
    />
    <CircuitLabelInstance
      x="64.5"
      y="242"
      :title="t('thrapp.mimics.adsorption.chiller.circuits.mediumTemperature')"
      :heat-transfer="sensors.mediumTemperature"
    />
    <CircuitLabelInstance
      x="64.5"
      y="377"
      :title="t('thrapp.mimics.adsorption.chiller.circuits.lowTemperature')"
      :heat-transfer="sensors.lowTemperature"
    />

    <PortTemperatureLabelInstance
      x="241.34"
      y="94.51"
      port="out"
      field="temperatureReturn"
      :temperature="sensors.highTemperature"
    />
    <PortTemperatureLabelInstance
      x="240.34"
      y="188.51"
      port="in"
      field="temperatureSupply"
      :temperature="sensors.highTemperature"
    />
    <PortTemperatureLabelInstance
      x="6.64"
      y="228.05"
      port="out"
      side="left"
      field="temperatureReturn"
      :temperature="sensors.mediumTemperature"
    />
    <PortTemperatureLabelInstance
      x="6.64"
      y="323.05"
      port="in"
      side="left"
      field="temperatureSupply"
      :temperature="sensors.mediumTemperature"
    />
    <PortTemperatureLabelInstance
      x="241.34"
      y="363.51"
      port="out"
      field="temperatureReturn"
      :temperature="sensors.lowTemperature"
    />
    <PortTemperatureLabelInstance
      x="240.34"
      y="457.51"
      port="in"
      field="temperatureSupply"
      :temperature="sensors.lowTemperature"
    />
  </FahrenheitInstance>
</template>
