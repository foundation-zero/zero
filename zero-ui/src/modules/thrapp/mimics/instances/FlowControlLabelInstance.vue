<script setup lang="ts">
import { ratioAsPercentage } from "@/modules/common/lib/utils";
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { SensorComponentType } from "@/modules/thrsim/types";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { getMimicDataProvider, ModuleField } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & { valve: ModuleField<SensorComponentType.Valve> }
>();

const { getSensorValue } = getMimicDataProvider();
const valve = getSensorValue(props.valve);
const position = computed(() => valve.value?.positionRel?.value);
const positionPercentage = ratioAsPercentage(position);
const { t } = useI18n();
</script>

<template>
  <Label
    :x="x"
    :y="y"
    width="50"
    height="50"
  >
    {{ tagId }}
    <template #value>
      <AnimatedNumber
        :to="positionPercentage"
        :fraction-digits="0"
      />
      <span>{{ t("units.percent") }}</span>
    </template>
  </Label>
</template>
