<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { SensorComponentType } from "@/modules/thrs/types";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { getMimicDataProvider, ModuleField } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & { temperature: ModuleField<SensorComponentType.Temperature> }
>();

const { getSensorValue } = getMimicDataProvider();
const temperature = getSensorValue(props.temperature);

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
        :to="temperature?.temperature?.value"
        :fraction-digits="0"
      />
      <span>{{ t("units.celsius") }}</span>
    </template>
  </Label>
</template>
