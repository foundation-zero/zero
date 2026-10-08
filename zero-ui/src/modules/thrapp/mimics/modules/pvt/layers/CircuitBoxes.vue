<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { MimicComponentType } from "@/modules/thrapp/types";
import { RiArrowDownLine, RiArrowRightLine } from "@remixicon/vue";
import { ConnectingCircuitInstance, SeawaterCircuitInstance } from "../../../instances";
import { PVT_MIMIC_DATA } from "../data";

const circuits = PVT_MIMIC_DATA[MimicComponentType.SeawaterCircuit];
const hotWaterCircuits = PVT_MIMIC_DATA[MimicComponentType.ConnectingCircuit];

const t = tScoped("labels");
</script>

<template>
  <g>
    <ConnectingCircuitInstance
      x="885"
      y="40"
      height="195"
      v-bind="hotWaterCircuits?.['pcm']"
    >
      <template #from>
        <RiArrowRightLine class="text-muted-foreground size-3" />
        {{ t("in") }}
      </template>
      <template #to>
        <RiArrowDownLine class="text-muted-foreground size-3" />
        {{ t("out") }}
      </template>
    </ConnectingCircuitInstance>

    <SeawaterCircuitInstance
      x="1110"
      y="355"
      width="194"
      height="90"
      v-bind="circuits?.['seawater']"
    />
  </g>
</template>
