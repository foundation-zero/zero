<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { TEMPERATURE_SENSOR_WIDTH } from "../../../components/temperature-sensor";
import { TemperatureSensorInstance } from "../../../instances";
import TemperatureLabelInstance from "../../../instances/TemperatureLabelInstance.vue";
import { PCM_MIMIC_DATA } from "../data";

const temperatureSensors = PCM_MIMIC_DATA[MimicComponentType.TemperatureSensor];
</script>

<template>
  <g>
    <TemperatureSensorInstance
      x="464"
      y="143"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-60']"
    >
      <TemperatureLabelInstance
        target-x="464"
        :target-width="TEMPERATURE_SENSOR_WIDTH"
        y="103"
        :tag-id="temperatureSensors['1038-60'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-60'].source"
      />
    </TemperatureSensorInstance>

    <TemperatureSensorInstance
      x="464"
      y="353"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-33']"
    >
      <TemperatureLabelInstance
        target-x="464"
        :target-width="TEMPERATURE_SENSOR_WIDTH"
        y="313"
        :tag-id="temperatureSensors['1038-33'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-33'].source"
      />
    </TemperatureSensorInstance>

    <TemperatureSensorInstance
      x="464"
      y="549"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-34']"
    >
      <TemperatureLabelInstance
        target-x="464"
        :target-width="TEMPERATURE_SENSOR_WIDTH"
        y="510"
        :tag-id="temperatureSensors['1038-34'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-34'].source"
      />
    </TemperatureSensorInstance>

    <TemperatureSensorInstance
      x="464"
      y="745"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-35']"
    >
      <TemperatureLabelInstance
        target-x="464"
        :target-width="TEMPERATURE_SENSOR_WIDTH"
        y="705"
        :tag-id="temperatureSensors['1038-35'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-35'].source"
      />
    </TemperatureSensorInstance>

    <TemperatureSensorInstance
      x="1105"
      y="640"
      :orientation="ComponentOrientation.Right"
      v-bind="temperatureSensors['1038-48']"
    >
      <TemperatureLabelInstance
        target-x="1105"
        y="630"
        :tag-id="temperatureSensors['1038-48'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-48'].source"
      />
    </TemperatureSensorInstance>

    <TemperatureSensorInstance
      x="1229"
      y="640"
      :orientation="ComponentOrientation.Right"
      v-bind="temperatureSensors['1038-49']"
    >
      <TemperatureLabelInstance
        target-x="1229"
        y="630"
        :tag-id="temperatureSensors['1038-49'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-49'].source"
      />
    </TemperatureSensorInstance>

    <TemperatureSensorInstance
      x="1105"
      y="20"
      :orientation="ComponentOrientation.Right"
      v-bind="temperatureSensors['1038-53']"
    >
      <TemperatureLabelInstance
        target-x="1105"
        y="10"
        :tag-id="temperatureSensors['1038-53'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-53'].source"
      />
    </TemperatureSensorInstance>

    <TemperatureSensorInstance
      x="1229"
      y="20"
      :orientation="ComponentOrientation.Right"
      v-bind="temperatureSensors['1038-54']"
    >
      <TemperatureLabelInstance
        target-x="1229"
        y="10"
        :tag-id="temperatureSensors['1038-54'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-54'].source"
      />
    </TemperatureSensorInstance>

    <TemperatureSensorInstance
      x="76"
      y="200"
      :orientation="ComponentOrientation.Right"
      v-bind="temperatureSensors['1038-31']"
    >
      <TemperatureLabelInstance
        target-x="80"
        y="190"
        :tag-id="temperatureSensors['1038-31'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-31'].source"
      />
    </TemperatureSensorInstance>

    <TemperatureSensorInstance
      x="76"
      y="645"
      :orientation="ComponentOrientation.Right"
      v-bind="temperatureSensors['1038-55']"
    >
      <TemperatureLabelInstance
        target-x="80"
        y="635"
        :tag-id="temperatureSensors['1038-55'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-55'].source"
      />
    </TemperatureSensorInstance>
  </g>
</template>
