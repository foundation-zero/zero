<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { BypassArea } from "../../../components/bypass-area";
import { PYRANO_METER_WIDTH } from "../../../components/pyrano-meter";
import { getTooltipContexts } from "../../../data";
import { IrradianceLabelInstance, PvtInstance, PyranometerInstance } from "../../../instances";

const pvt = getTooltipContexts(MimicComponentType.Pvt, ["9001-01", "9002-01", "9001-03"]);
const pyranometers = getTooltipContexts(MimicComponentType.Pyranometer, ["9044", "9043"]);
</script>

<template>
  <g>
    <BypassArea
      x="-60"
      y="9"
      :width="301.5"
      :height="448"
    >
      Main bimini
    </BypassArea>

    <BypassArea
      x="0"
      y="478"
      :width="242"
      :height="237"
    >
      Owners bimini
    </BypassArea>

    <IrradianceLabelInstance
      :target-x="-52"
      :target-width="PYRANO_METER_WIDTH"
      :source="pyranometers['9044'].source"
      y="290"
      tag-id="9044"
    />
    <PyranometerInstance
      x="-52"
      y="260"
      v-bind="pyranometers['9044']"
    />
    <IrradianceLabelInstance
      :target-x="-52"
      :source="pyranometers['9043'].source"
      :target-width="PYRANO_METER_WIDTH"
      y="390"
      tag-id="9043"
    />
    <PyranometerInstance
      x="-52"
      y="360"
      v-bind="pyranometers['9043']"
    />

    <PvtInstance
      x="14"
      y="30"
      v-bind="pvt['9001-01']"
    />

    <PvtInstance
      x="14"
      y="241"
      v-bind="pvt['9002-01']"
    />

    <PvtInstance
      x="14"
      y="500"
      v-bind="pvt['9001-03']"
    />
  </g>
</template>
