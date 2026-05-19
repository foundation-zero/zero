<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { RiArrowDownLine, RiArrowUpLine, RiDropLine, RiTempColdLine } from "@remixicon/vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps, useRandomizedNumber } from ".";
import {
  CircuitBox,
  CircuitBoxList,
  CircuitBoxListHeader,
  CircuitBoxListItem,
  CircuitBoxListSeparator,
  CircuitBoxTitle,
} from "../components/circuit-box";

const { t } = useI18n();
const props = defineProps<MimicComponentInstanceProps & { title: string }>();

const tIn = useRandomizedNumber(40, 90);
const tOut = useRandomizedNumber(40, 90);
const flowIn = useRandomizedNumber(1, 10);
const flowOut = useRandomizedNumber(1, 10);
</script>

<template>
  <CircuitBox v-bind="props">
    <CircuitBoxTitle>{{ title }}</CircuitBoxTitle>
    <CircuitBoxList>
      <CircuitBoxListSeparator />
      <CircuitBoxListHeader>
        <RiArrowUpLine class="text-muted-foreground size-3" />
        In
      </CircuitBoxListHeader>
      <CircuitBoxListItem>
        <span class="flex items-center gap-0.5">
          <RiDropLine class="text-brand size-3.5" />
          Flow
        </span>
        <span class="text-foreground font-medium"
          ><AnimatedNumber :to="flowIn" /> {{ t("units.lpm") }}</span
        >
      </CircuitBoxListItem>
      <CircuitBoxListItem>
        <span class="flex items-center gap-0.5">
          <RiTempColdLine class="text-heating-medium size-3.5" />
          Temp
        </span>
        <span class="text-foreground font-medium"
          ><AnimatedNumber :to="tIn" /> {{ t("units.celsius") }}</span
        >
      </CircuitBoxListItem>
      <CircuitBoxListSeparator />
      <CircuitBoxListHeader>
        <RiArrowDownLine class="text-muted-foreground size-3" />
        Out
      </CircuitBoxListHeader>
      <CircuitBoxListItem>
        <span class="flex items-center gap-0.5">
          <RiDropLine class="text-brand size-3.5" />
          Flow
        </span>
        <span class="text-foreground font-medium"
          ><AnimatedNumber :to="flowOut" /> {{ t("units.lpm") }}</span
        >
      </CircuitBoxListItem>
      <CircuitBoxListItem>
        <span class="flex items-center gap-0.5">
          <RiTempColdLine class="text-heating-medium size-3.5" />
          Temp
        </span>
        <span class="text-foreground font-medium"
          ><AnimatedNumber :to="tOut" /> {{ t("units.celsius") }}</span
        >
      </CircuitBoxListItem>
      <CircuitBoxListSeparator />
    </CircuitBoxList>
  </CircuitBox>
</template>
