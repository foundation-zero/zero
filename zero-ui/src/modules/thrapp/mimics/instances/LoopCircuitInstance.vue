<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps, useDeltaT, useRandomizedNumber } from ".";
import { CircuitBox, CircuitBoxTitle } from "../components/circuit-box";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListFlowItem,
  ValueListItem,
} from "../components/value-list";

const { t } = useI18n();
const props = defineProps<MimicComponentInstanceProps & { title: string }>();

const tIn = useRandomizedNumber(40, 90);
const tOut = useRandomizedNumber(40, 90);
const deltaT = useDeltaT(tIn, tOut);
</script>

<template>
  <CircuitBox v-bind="props">
    <CircuitBoxTitle>{{ title }}</CircuitBoxTitle>
    <ValueList>
      <ValueListDeltaTItem :value="deltaT" />
      <ValueListItem>
        <span class="text-muted-foreground text-2xs">{{ t("units.Tin") }}</span>
        <span class="text-muted-foreground text-xs">
          <AnimatedNumber :to="tIn" />{{ t("units.celsius") }}
        </span>
      </ValueListItem>
      <ValueListItem>
        <span class="text-muted-foreground text-2xs">{{ t("units.Tout") }}</span>
        <span class="text-muted-foreground text-xs">
          <AnimatedNumber :to="tOut" />{{ t("units.celsius") }}
        </span>
      </ValueListItem>
      <ValueListFlowItem :value="tOut" />
    </ValueList>
  </CircuitBox>
</template>
