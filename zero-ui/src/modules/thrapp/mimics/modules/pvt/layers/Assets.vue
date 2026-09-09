<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { BypassArea } from "../../../components/bypass-area";
import { PYRANO_METER_WIDTH, PyranoMeter } from "../../../components/pyrano-meter";
import { IrradianceLabelInstance, PvtInstance } from "../../../instances";
import { PVT_MIMIC_DATA } from "../data";

const pvt = PVT_MIMIC_DATA[MimicComponentType.Pvt];
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
      y="290"
      tag-id="9044"
    />
    <PyranoMeter
      x="-52"
      y="260"
    />
    <IrradianceLabelInstance
      :target-x="-52"
      :target-width="PYRANO_METER_WIDTH"
      y="390"
      tag-id="9043"
    />
    <PyranoMeter
      x="-52"
      y="360"
    />

    <PvtInstance
      x="14"
      y="30"
      :tag-id="pvt['9001-01'].tooltip?.yardTag"
      v-bind="pvt['9001-01']"
    />

    <PvtInstance
      x="14"
      y="241"
      :tag-id="pvt['9002-01'].tooltip?.yardTag"
      v-bind="pvt['9002-01']"
    />

    <PvtInstance
      x="14"
      y="500"
      :tag-id="pvt['9001-03'].tooltip?.yardTag"
      v-bind="pvt['9001-03']"
    />
  </g>
</template>
