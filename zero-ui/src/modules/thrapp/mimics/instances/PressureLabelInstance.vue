<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { SensorComponentType } from "@/modules/thrs/types";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & {
    pressure: import("../providers").ModuleField<SensorComponentType.Pressure>;
  }
>();

const { getSensorValue } = getMimicDataProvider();
const pressure = getSensorValue(props.pressure);

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
        :to="pressure?.pressure?.value"
        :fraction-digits="0"
      />
      {{ t("units.bar") }}
    </template>
  </Label>
</template>
