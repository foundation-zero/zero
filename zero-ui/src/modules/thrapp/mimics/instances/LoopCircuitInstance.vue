<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { SensorComponentType } from "@/modules/thrs/types";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps, ModuleProp, TitleProps } from ".";
import { CircuitBox, CircuitBoxTitle } from "../components/circuit-box";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListFlowItem,
  ValueListItem,
} from "../components/value-list";
import { getMimicDataProvider } from "../providers";

const { t } = useI18n();
const props = defineProps<
  MimicComponentInstanceProps &
    TitleProps & {
      deltaT: ModuleProp<SensorComponentType.DeltaT>;
      flow: ModuleProp<SensorComponentType.Flow>;
      tIn: ModuleProp<SensorComponentType.Temperature>;
      tOut: ModuleProp<SensorComponentType.Temperature>;
    }
>();

const { getSensorValue } = getMimicDataProvider();

const deltaT = getSensorValue(props.deltaT);
const tIn = getSensorValue(props.tIn);
const tOut = getSensorValue(props.tOut);
const flow = getSensorValue(props.flow);
</script>

<template>
  <CircuitBox v-bind="props">
    <CircuitBoxTitle>{{ title }}</CircuitBoxTitle>
    <ValueList>
      <ValueListDeltaTItem :value="deltaT?.deltaT?.value" />
      <ValueListItem>
        <span class="text-muted-foreground text-2xs">{{ t("units.Tin") }}</span>
        <span class="text-muted-foreground text-xs">
          <AnimatedNumber :to="tIn?.temperature?.value" />{{ t("units.celsius") }}
        </span>
      </ValueListItem>
      <ValueListItem>
        <span class="text-muted-foreground text-2xs">{{ t("units.Tout") }}</span>
        <span class="text-muted-foreground text-xs">
          <AnimatedNumber :to="tOut?.temperature?.value" />{{ t("units.celsius") }}
        </span>
      </ValueListItem>
      <ValueListFlowItem :value="flow?.flow?.value" />
    </ValueList>
  </CircuitBox>
</template>
