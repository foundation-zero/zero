<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { SensorComponentType } from "@/modules/thrs/types";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps, TitleProps } from ".";
import { CircuitBox, CircuitBoxTitle } from "../components/circuit-box";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListFlowItem,
  ValueListItem,
} from "../components/value-list";
import { getMimicDataProvider, ModuleField } from "../providers";

const { t } = useI18n();
const props = defineProps<
  MimicComponentInstanceProps &
    TitleProps & {
      width?: number | string;
      height?: number | string;
      forceHeight?: boolean;
      deltaT: ModuleField<SensorComponentType.DeltaT>;
      flow: ModuleField<SensorComponentType.Flow>;
      tIn: ModuleField<SensorComponentType.Temperature>;
      tOut: ModuleField<SensorComponentType.Temperature>;
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
