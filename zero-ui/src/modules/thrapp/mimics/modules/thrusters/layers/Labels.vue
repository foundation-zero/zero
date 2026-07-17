<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import FlowControlLabelInstance from "../../../instances/FlowControlLabelInstance.vue";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";
import PressureLabelInstance from "../../../instances/PressureLabelInstance.vue";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import TemperatureLabelInstance from "../../../instances/TemperatureLabelInstance.vue";
import { getField } from "../../../providers";
</script>

<template>
  <g>
    <TagLabelInstance
      x="416"
      y="179"
      tag-id="1091-01"
    />
    <TagLabelInstance
      x="416"
      y="484"
      tag-id="1091-02"
    />
    <TagLabelInstance
      x="575"
      y="332"
      tag-id="1066-03"
    />
    <TagLabelInstance
      x="763"
      y="273"
      tag-id="1214-01"
    />
    <TagLabelInstance
      x="700"
      y="333"
      tag-id="1216"
    />

    <TagLabelInstance
      x="1025.775"
      y="185"
      tag-id="1084-01"
    />
    <TagLabelInstance
      x="1025.775"
      y="136"
      tag-id="1087-08"
    />

    <FlowControlLabelInstance
      x="218"
      y="163"
      tag-id="1215"
      :valve="getField(SensorComponentType.Valve, 'thrusters', 'thrustersFlowcontrolAft')"
    />
    <FlowControlLabelInstance
      x="214"
      y="418"
      tag-id="1064-02"
      :valve="getField(SensorComponentType.Valve, 'thrusters', 'thrustersFlowcontrolFwd')"
    />
    <TagLabelInstance
      x="590.649"
      y="147.576"
      tag-id="1212-01"
    />
    <TagLabelInstance
      x="718.677"
      y="147.576"
      tag-id="1212-02"
    />
    <TagLabelInstance
      x="614.055"
      y="510.724"
      tag-id="1212-03"
    />
    <TagLabelInstance
      x="743.07"
      y="510.724"
      tag-id="1212-04"
    />
    <TagLabelInstance
      x="613.068"
      y="610.72"
      tag-id="1212-05"
    />
    <TagLabelInstance
      x="740.25"
      y="610.72"
      tag-id="1212-06"
    />
    <TagLabelInstance
      x="214.722"
      y="290"
      tag-id="1212-07"
    />
    <TagLabelInstance
      x="214.722"
      y="560.724"
      tag-id="1087-03"
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
      x="836"
      y="386"
      tag-id="1218-01"
      :flow="getField(SensorComponentType.Flow, 'thrusters', 'thrustersFlowRecovery')"
    />
    <FlowLabelInstance
      x="280"
      y="243"
      tag-id="1218-02"
      :flow="getField(SensorComponentType.Flow, 'thrusters', 'thrustersFlowAft')"
    />
    <FlowLabelInstance
      x="280"
      y="513"
      tag-id="1057-22"
      :flow="getField(SensorComponentType.Flow, 'thrusters', 'thrustersFlowFwd')"
    />

    <PressureLabelInstance
      x="453"
      y="515"
      tag-id="1097-01"
      :pressure="getField(SensorComponentType.Pressure, 'thrusters', 'thrustersPressureDischarge')"
    />
    <PressureLabelInstance
      x="934"
      y="193"
      tag-id="1097-02"
      :pressure="getField(SensorComponentType.Pressure, 'thrusters', 'thrustersPressureSystem')"
    />

    <TemperatureLabelInstance
      x="280"
      y="138"
      tag-id="1038-01"
      :temperature="
        getField(SensorComponentType.Temperature, 'thrusters', 'thrustersTemperatureAft')
      "
    />
    <TemperatureLabelInstance
      x="280"
      y="398"
      tag-id="1038-02"
      :temperature="
        getField(SensorComponentType.Temperature, 'thrusters', 'thrustersTemperatureFwd')
      "
    />
    <TemperatureLabelInstance
      x="827"
      y="515"
      tag-id="1038-28"
      :temperature="
        getField(SensorComponentType.Temperature, 'thrusters', 'thrustersTemperatureSupply')
      "
    />
    <TemperatureLabelInstance
      x="631"
      y="293"
      tag-id="1038-30"
      :temperature="
        getField(SensorComponentType.Temperature, 'thrusters', 'thrustersTemperatureRecoveryMix')
      "
    />
  </g>
</template>
