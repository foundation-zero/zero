<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types/index.ts";
import FlowControlLabelInstance from "../../../instances/FlowControlLabelInstance.vue";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";
import HeatExchangerLabelInstance from "../../../instances/HeatExchangerLabelInstance.vue";
import PressureLabelInstance from "../../../instances/PressureLabelInstance.vue";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import TemperatureLabelInstance from "../../../instances/TemperatureLabelInstance.vue";
import { getField } from "../../../providers/index.ts";
</script>

<template>
  <g>
    <TagLabelInstance
      x="598"
      y="19"
      tag-id="1098-01"
    />
    <TagLabelInstance
      x="956"
      y="19"
      tag-id="1098-02"
    />
    <TagLabelInstance
      x="1295"
      y="19"
      tag-id="1098-03"
    />
    <TagLabelInstance
      x="360"
      y="192"
      tag-id="1067-11"
    />
    <TagLabelInstance
      x="416"
      y="192"
      tag-id="1067-12"
    />
    <TagLabelInstance
      x="470"
      y="192"
      tag-id="1067-14"
    />
    <TagLabelInstance
      x="524"
      y="192"
      tag-id="1067-13"
    />
    <TagLabelInstance
      x="713"
      y="192"
      tag-id="1067-07"
    />
    <TagLabelInstance
      x="767"
      y="192"
      tag-id="1067-08"
    />
    <TagLabelInstance
      x="822"
      y="192"
      tag-id="1067-10"
    />
    <TagLabelInstance
      x="875"
      y="192"
      tag-id="1067-09"
    />
    <TagLabelInstance
      x="1051"
      y="192"
      tag-id="1067-03"
    />
    <TagLabelInstance
      x="1105"
      y="192"
      tag-id="1067-04"
    />
    <TagLabelInstance
      x="1160"
      y="192"
      tag-id="1067-06"
    />
    <TagLabelInstance
      x="1217"
      y="192"
      tag-id="1067-05"
    />
    <TagLabelInstance
      x="211"
      y="295"
      tag-id="1174-02"
    />
    <TagLabelInstance
      x="733"
      y="341"
      tag-id="1168-06"
    />
    <TagLabelInstance
      x="389"
      y="370"
      tag-id="1169-01"
    />
    <TagLabelInstance
      x="295"
      y="370"
      tag-id="1169-03"
    />
    <TagLabelInstance
      x="211"
      y="393"
      tag-id="1174-01"
    />
    <TagLabelInstance
      x="236"
      y="432"
      tag-id="1095-14"
    />
    <TagLabelInstance
      x="613"
      y="463"
      tag-id="1168-04"
    />
    <TagLabelInstance
      x="843"
      y="464"
      tag-id="1168-05"
    />
    <TagLabelInstance
      x="91"
      y="505"
      tag-id="1069-17"
    />
    <TagLabelInstance
      x="145"
      y="542"
      tag-id="1067-18"
    />
    <TagLabelInstance
      x="60"
      y="548"
      tag-id="1069-18"
    />
    <TagLabelInstance
      x="249"
      y="563"
      tag-id="1067-16"
    />
    <TagLabelInstance
      x="79"
      y="597"
      tag-id="1069-10"
    />
    <TagLabelInstance
      x="216"
      y="598"
      tag-id="1067-17"
    />
    <TagLabelInstance
      x="802"
      y="625"
      tag-id="1169-02"
    />

    <FlowLabelInstance
      x="1090"
      y="420"
      tag-id="1057-24"
      :flow="getField(SensorComponentType.Flow, 'dhw', 'dhwFlowDrives')"
    />
    <FlowLabelInstance
      x="236"
      y="467"
      tag-id="1058-11"
      :flow="getField(SensorComponentType.Flow, 'dhw', 'dhwFlowBoosting')"
    />
    <FlowLabelInstance
      x="1090"
      y="579"
      tag-id="1057-17"
      :flow="getField(SensorComponentType.Flow, 'dhw', 'dhwFlowDc')"
    />

    <PressureLabelInstance
      x="565"
      y="71"
      tag-id="1056-01"
      :pressure="getField(SensorComponentType.Pressure, 'dhw', 'dhwPressure')"
    />
    <PressureLabelInstance
      x="926"
      y="71"
      tag-id="1056-02"
      :pressure="getField(SensorComponentType.Pressure, 'dhw', 'dhwPressure')"
    />
    <PressureLabelInstance
      x="1266"
      y="71"
      tag-id="1056-03"
      :pressure="getField(SensorComponentType.Pressure, 'dhw', 'dhwPressure')"
    />
    <PressureLabelInstance
      x="277"
      y="186"
      tag-id="1097-11"
      :pressure="getField(SensorComponentType.Pressure, 'dhw', 'dhwPressure')"
    />

    <TemperatureLabelInstance
      x="313"
      y="71"
      tag-id="1038-45"
      :temperature="getField(SensorComponentType.Temperature, 'dhw', 'dhwTemperatureTank1')"
    />
    <TemperatureLabelInstance
      x="676"
      y="71"
      tag-id="1038-44"
      :temperature="getField(SensorComponentType.Temperature, 'dhw', 'dhwTemperatureTank2')"
    />
    <TemperatureLabelInstance
      x="1016"
      y="71"
      tag-id="1038-27"
      :temperature="getField(SensorComponentType.Temperature, 'dhw', 'dhwTemperatureTank3')"
    />
    <TemperatureLabelInstance
      x="180"
      y="158"
      tag-id="1038-65"
      :temperature="
        getField(SensorComponentType.Temperature, 'dhw', 'dhwTemperatureBoostingSupply')
      "
    />
    <TemperatureLabelInstance
      x="395"
      y="423"
      tag-id="1038-26"
      :temperature="getField(SensorComponentType.Temperature, 'dhw', 'dhwTemperatureDcReturn')"
    />
    <TemperatureLabelInstance
      x="553"
      y="420"
      tag-id="1038-25"
      :temperature="
        getField(SensorComponentType.Temperature, 'dhw', 'dhwTemperatureHvacExchangerReturn')
      "
    />
    <TemperatureLabelInstance
      x="1163"
      y="496"
      tag-id="1038-47"
      :temperature="
        getField(SensorComponentType.Temperature, 'dhw', 'dhwTemperatureFreshwaterSupply')
      "
    />
    <TemperatureLabelInstance
      x="910"
      y="507"
      tag-id="1038-51"
      :temperature="
        getField(SensorComponentType.Temperature, 'dhw', 'dhwTemperatureAdsorptionReturn')
      "
    />
    <TemperatureLabelInstance
      x="236"
      y="517"
      tag-id="1038-66"
      :temperature="
        getField(SensorComponentType.Temperature, 'dhw', 'dhwTemperatureBoostingReturn')
      "
    />
    <TemperatureLabelInstance
      x="393"
      y="580"
      tag-id="1038-46"
      :temperature="getField(SensorComponentType.Temperature, 'dhw', 'dhwTemperatureDrivesReturn')"
    />

    <FlowControlLabelInstance
      x="1043"
      y="442"
      tag-id="1064-08"
      :valve="getField(SensorComponentType.Valve, 'dhw', 'dhwFlowcontrolDrives')"
    />
    <FlowControlLabelInstance
      x="1045"
      y="604"
      tag-id="1064-03"
      :valve="getField(SensorComponentType.Valve, 'dhw', 'dhwFlowcontrolDc')"
    />

    // Check this one, field might be wrong
    <FlowControlLabelInstance
      x="220"
      y="329"
      tag-id="1022"
      :valve="getField(SensorComponentType.Valve, 'dhw', 'dhwSwitchHeatpump')"
    />

    <HeatExchangerLabelInstance
      x="23"
      y="379.3"
      tag-id="1007"
      :heat-exchanger="getField(SensorComponentType.HeatExchanger, 'dhw', 'dhwConsumersExchanger')"
    />
    <HeatExchangerLabelInstance
      x="460"
      y="425"
      tag-id="1008"
      :heat-exchanger="getField(SensorComponentType.HeatExchanger, 'dhw', 'dhwDcExchanger')"
    />
    <HeatExchangerLabelInstance
      x="955"
      y="425"
      tag-id="1004"
      :heat-exchanger="getField(SensorComponentType.HeatExchanger, 'dhw', 'dhwFahrenheitExchanger')"
    />
    <HeatExchangerLabelInstance
      x="710"
      y="585"
      tag-id="1009"
      :heat-exchanger="getField(SensorComponentType.HeatExchanger, 'dhw', 'dhwDrivesExchanger')"
    />
  </g>
</template>
