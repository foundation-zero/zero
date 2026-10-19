<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { MimicComponentType } from "@/modules/thrapp/types";
import { RiArrowDownLine, RiArrowRightLine } from "@remixicon/vue";
import { getTooltipContexts } from "../../../data";
import { ConnectingCircuitInstance, SeawaterCircuitInstance } from "../../../instances";

const t = tScoped("labels");

const circuits = getTooltipContexts(MimicComponentType.SeawaterCircuit, ["pvt:seawater"]);
const hotWaterCircuits = getTooltipContexts(MimicComponentType.ConnectingCircuit, ["pvt:pcm"]);
</script>

<template>
  <g>
    <ConnectingCircuitInstance
      x="885"
      y="40"
      height="195"
      v-bind="hotWaterCircuits['pvt:pcm']"
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
      v-bind="circuits['pvt:seawater']"
    />
  </g>
</template>
