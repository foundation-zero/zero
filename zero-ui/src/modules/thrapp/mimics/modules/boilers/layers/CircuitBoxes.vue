<script setup lang="ts">
/**
 * Circuit Boxes Layer
 *
 * Displays circuit information boxes for High Temp Loop, Brightloop, Drives, and Fahrenheit.
 * Uses the LoopCircuitInstance component to render each box with real-time temperature and flow data.
 *
 * FIGMA_URL: https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=7149:66096
 */

import { tScoped } from "@/modules/common/lib/utils.ts";
import { SensorComponentType } from "@/modules/thrs/types/index.ts";
import HotWaterCircuitInstance from "../../../instances/HotWaterCircuitInstance.vue";
import { LoopCircuitInstance } from "../../../instances/index.ts";
import { getField } from "../../../providers";

const t = tScoped("thrapp.mimics.boilers.circuitBoxes");
</script>

<template>
  <g>
    <LoopCircuitInstance
      x="0"
      y="25"
      force-height
      :title="t('highTempLoopTitle')"
      :delta-t="getField(SensorComponentType.DeltaT, 'boilers', 'consumersDelta')"
      :flow="getField(SensorComponentType.Flow, 'boilers', 'consumersFlowBoosting')"
      :t-in="
        getField(SensorComponentType.Temperature, 'boilers', 'consumersTemperatureBoostingSupply')
      "
      :t-out="
        getField(SensorComponentType.Temperature, 'boilers', 'consumersTemperatureBoostingReturn')
      "
    />
    <LoopCircuitInstance
      x="397"
      y="730"
      force-height
      :title="t('brightloopTitle')"
      :delta-t="getField(SensorComponentType.DeltaT, 'boilers', 'lt2Delta')"
      :flow="getField(SensorComponentType.Flow, 'boilers', 'boilersFlowLt2')"
      :t-in="getField(SensorComponentType.Temperature, 'boilers', 'lt2TemperatureRecovery')"
      :t-out="getField(SensorComponentType.Temperature, 'boilers', 'lt2TemperatureRecoveryReturn')"
    />
    <LoopCircuitInstance
      x="650"
      y="730"
      force-height
      :title="t('drivesTitle')"
      :delta-t="getField(SensorComponentType.DeltaT, 'boilers', 'lt1Delta')"
      :flow="getField(SensorComponentType.Flow, 'boilers', 'boilersFlowLt1')"
      :t-in="getField(SensorComponentType.Temperature, 'boilers', 'lt1TemperatureRecovery')"
      :t-out="getField(SensorComponentType.Temperature, 'boilers', 'lt1TemperatureRecoveryReturn')"
    />
    <LoopCircuitInstance
      x="903"
      y="730"
      force-height
      :title="t('fahrenheitTitle')"
      :delta-t="getField(SensorComponentType.DeltaT, 'boilers', 'fahrenheitDelta')"
      :flow="getField(SensorComponentType.Flow, 'boilers', 'fahrenheitFlowBoilers')"
      :t-in="
        getField(SensorComponentType.Temperature, 'boilers', 'fahrenheitTemperatureWasteReturn')
      "
      :t-out="
        getField(SensorComponentType.Temperature, 'boilers', 'fahrenheitTemperatureBoilersReturn')
      "
    />
    <HotWaterCircuitInstance
      x="1215"
      y="455"
      force-height
      height="300"
      :title="t('domesticHotWaterTitle')"
      :flow-in="getField(SensorComponentType.CalculatedFlow, 'boilers', 'freshwaterFlowSupply')"
      :flow-out="getField(SensorComponentType.Flow, 'boilers', 'freshwaterHotwaterFlow')"
      :t-in="
        getField(SensorComponentType.Temperature, 'boilers', 'boilersTemperatureFreshwaterSupply')
      "
      :t-out="getField(SensorComponentType.Temperature, 'boilers', 'freshwaterHotwaterTemperature')"
    />
  </g>
</template>
