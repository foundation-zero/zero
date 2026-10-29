<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { MimicComponentType } from "@/modules/thrapp/types";
import { BypassArea } from "../../../components/bypass-area";
import { PYRANO_METER_WIDTH } from "../../../components/pyrano-meter";
import { getTooltipContexts } from "../../../data";
import { IrradianceLabelInstance, PvtInstance, PyranometerInstance } from "../../../instances";

const pvt = getTooltipContexts(MimicComponentType.Pvt, ["9001-01", "9002-01", "9001-03"]);
const pyranometers = getTooltipContexts(MimicComponentType.Pyranometer, ["9044", "9043"]);

const { t } = useI18n();
</script>

<template>
  <g>
    <BypassArea
      x="-60"
      y="9"
      :width="301.5"
      :height="448"
    >
      {{ t("thrapp.mimics.pvt.sections.mainBimini") }}
    </BypassArea>

    <BypassArea
      x="0"
      y="478"
      :width="242"
      :height="237"
    >
      {{ t("thrapp.mimics.pvt.sections.ownersBimini") }}
    </BypassArea>

    <IrradianceLabelInstance
      :target-x="-46"
      :target-width="PYRANO_METER_WIDTH"
      :source="pyranometers['9044'].source"
      y="287.5"
      tag-id="9044"
    />
    <PyranometerInstance
      x="-44"
      y="257.5"
      v-bind="pyranometers['9044']"
    />
    <IrradianceLabelInstance
      :target-x="-46"
      :source="pyranometers['9043'].source"
      :target-width="PYRANO_METER_WIDTH"
      y="403.5"
      tag-id="9043"
    />
    <PyranometerInstance
      x="-44"
      y="372"
      v-bind="pyranometers['9043']"
    />

    <PvtInstance
      x="22"
      y="30"
      v-bind="pvt['9001-01']"
    />

    <PvtInstance
      x="22"
      y="241"
      v-bind="pvt['9002-01']"
    />

    <PvtInstance
      x="22"
      y="500"
      v-bind="pvt['9001-03']"
    />
  </g>
</template>
