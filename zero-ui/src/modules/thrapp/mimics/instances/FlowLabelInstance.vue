<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { SensorComponentType } from "@/modules/thrs/types";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { getMimicDataProvider, ModuleField } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & { flow: ModuleField<SensorComponentType.Flow> }
>();

const { getSensorValue } = getMimicDataProvider();
const flow = getSensorValue(props.flow);

const { t } = useI18n();
</script>

<template>
  <Label
    :x="x"
    :y="y"
  >
    {{ tagId }}
    <template #value>
      <AnimatedNumber
        :to="flow?.flow?.value"
        :fraction-digits="0"
      />
      {{ t("units.lpm") }}
    </template>
  </Label>
</template>
