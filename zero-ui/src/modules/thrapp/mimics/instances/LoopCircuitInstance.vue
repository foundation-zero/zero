<script setup lang="ts">
import { formatNumber, toSignedNumber } from "@/modules/common/lib/utils";
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { RiDropLine } from "@remixicon/vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps, useDeltaT, useRandomizedNumber } from ".";
import {
  CircuitBox,
  CircuitBoxList,
  CircuitBoxListItem,
  CircuitBoxTitle,
} from "../components/circuit-box";

const { t } = useI18n();
const props = defineProps<MimicComponentInstanceProps & { title: string }>();

const tIn = useRandomizedNumber(40, 90);
const tOut = useRandomizedNumber(40, 90);
const deltaT = useDeltaT(tIn, tOut);
</script>

<template>
  <CircuitBox v-bind="props">
    <CircuitBoxTitle>{{ title }}</CircuitBoxTitle>
    <CircuitBoxList>
      <CircuitBoxListItem>
        <span class="text-brand text-sm">{{ t("units.deltaT") }}</span>
        <span class="text-foreground font-medium">
          <AnimatedNumber
            :to="deltaT"
            :format="toSignedNumber(formatNumber(1))"
          />{{ t("units.celsius") }}</span
        >
      </CircuitBoxListItem>
      <CircuitBoxListItem>
        <span class="text-muted-foreground text-2xs">{{ t("units.Tin") }}</span>
        <span class="text-muted-foreground text-xs">
          <AnimatedNumber :to="tIn" />{{ t("units.celsius") }}
        </span>
      </CircuitBoxListItem>
      <CircuitBoxListItem>
        <span class="text-muted-foreground text-2xs">{{ t("units.Tout") }}</span>
        <span class="text-muted-foreground text-xs">
          <AnimatedNumber :to="tOut" />{{ t("units.celsius") }}
        </span>
      </CircuitBoxListItem>
      <CircuitBoxListItem>
        <span class="flex items-center gap-0.5">
          <RiDropLine class="text-brand size-3.5" />
          Flow
        </span>
        <span class="text-foreground font-medium"
          ><AnimatedNumber :to="tOut" /> {{ t("units.lpm") }}</span
        >
      </CircuitBoxListItem>
    </CircuitBoxList>
  </CircuitBox>
</template>
