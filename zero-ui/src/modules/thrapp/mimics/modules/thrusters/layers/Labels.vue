<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";
import PressureLabelInstance from "../../../instances/PressureLabelInstance.vue";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import TemperatureLabelInstance from "../../../instances/TemperatureLabelInstance.vue";
import { getField } from "../../../providers";
</script>

<template>
  <g>
    <TagLabelInstance
      x="314"
      y="129"
      tag-id="1038-01"
    />
    <TagLabelInstance
      x="314"
      y="339"
      tag-id="1038-02"
    />
    <TagLabelInstance
      x="827"
      y="413"
      tag-id="1038-28"
    />
    <TagLabelInstance
      x="611"
      y="238"
      tag-id="1038-30"
    />

    <TagLabelInstance
      x="333"
      y="431"
      tag-id="1057-22"
    />
    <TagLabelInstance
      x="334"
      y="216"
      tag-id="1218-02"
    />
    <TagLabelInstance
      x="816"
      y="316"
      tag-id="1218-01"
    />

    <TagLabelInstance
      x="453"
      y="415"
      tag-id="1097-01"
    />
    <TagLabelInstance
      x="927"
      y="154"
      tag-id="1097-02"
    />

    <TagLabelInstance
      x="403"
      y="146"
      tag-id="1091-01"
    />
    <TagLabelInstance
      x="402"
      y="392"
      tag-id="1091-02"
    />
    <TagLabelInstance
      x="560"
      y="271"
      tag-id="1066-03"
    />
    <TagLabelInstance
      x="214"
      y="159"
      tag-id="1215"
    />
    <TagLabelInstance
      x="748"
      y="199"
      tag-id="1214-01"
    />
    <TagLabelInstance
      x="683"
      y="283"
      tag-id="1216"
    />
    <TagLabelInstance
      x="214"
      y="418"
      tag-id="1064-02"
    />
    <TagLabelInstance
      x="590.649"
      y="147.576"
      tag-id="1212-1"
    />
    <TagLabelInstance
      x="718.677"
      y="147.576"
      tag-id="1212-2"
    />
    <TagLabelInstance
      x="614.055"
      y="416.724"
      tag-id="1212-3"
    />
    <TagLabelInstance
      x="743.07"
      y="416.724"
      tag-id="1212-4"
    />
    <TagLabelInstance
      x="613.068"
      y="489.72"
      tag-id="1212-5"
    />
    <TagLabelInstance
      x="740.25"
      y="489.72"
      tag-id="1212-6"
    />
    <TagLabelInstance
      x="541.722"
      y="416.724"
      tag-id="1213-1"
    />

    <TagLabelInstance
      x="696"
      y="489"
      tag-id="1194"
    />
    <TagLabelInstance
      x="696"
      y="581"
      tag-id="1195"
    />

    <FlowLabelInstance
      x="333"
      y="431"
      tag-id="1057-22"
      :flow="getField(SensorComponentType.Flow, 'thrusters', 'thrustersFlowFwd')"
    />
    <FlowLabelInstance
      x="816"
      y="316"
      tag-id="1218-01"
      :flow="getField(SensorComponentType.Flow, 'thrusters', 'thrustersFlowRecovery')"
    />
    <FlowLabelInstance
      x="334"
      y="216"
      tag-id="1218-02"
      :flow="getField(SensorComponentType.Flow, 'thrusters', 'thrustersFlowAft')"
    />

    <PressureLabelInstance
      x="453"
      y="415"
      tag-id="1097-01"
      :pressure="getField(SensorComponentType.Pressure, 'thrusters', 'thrustersPressureDischarge')"
    />
    <PressureLabelInstance
      x="927"
      y="154"
      tag-id="1097-02"
      :pressure="getField(SensorComponentType.Pressure, 'thrusters', 'thrustersPressureSystem')"
    />

    <TemperatureLabelInstance
      x="314"
      y="129"
      tag-id="1038-01"
      :temperature="
        getField(SensorComponentType.Temperature, 'thrusters', 'thrustersTemperatureAft')
      "
    />
    <TemperatureLabelInstance
      x="314"
      y="339"
      tag-id="1038-02"
      :temperature="
        getField(SensorComponentType.Temperature, 'thrusters', 'thrustersTemperatureFwd')
      "
    />
    <TemperatureLabelInstance
      x="827"
      y="413"
      tag-id="1038-28"
      :temperature="
        getField(SensorComponentType.Temperature, 'thrusters', 'thrustersTemperatureSupply')
      "
    />
    <TemperatureLabelInstance
      x="611"
      y="238"
      tag-id="1038-30"
      :temperature="
        getField(SensorComponentType.Temperature, 'thrusters', 'thrustersTemperatureRecoveryMix')
      "
    />
  </g>
</template>
