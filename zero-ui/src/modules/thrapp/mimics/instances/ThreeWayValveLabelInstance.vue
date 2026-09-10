<script setup lang="ts">
import { formatRatio } from "@/modules/common/lib/utils";
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { getMimicDataProvider, ModuleField } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & { valve: ModuleField<SensorComponentType.Valve> }
>();

const { getSensorValue } = getMimicDataProvider();
const valve = getSensorValue(props.valve);
</script>

<template>
  <Label
    :x="x"
    :y="y"
    :width="60"
    :height="50"
  >
    {{ tagId }}
    <template #value>
      <span>A:</span>
      <AnimatedNumber
        :to="valve?.positionRel?.value"
        :format="formatRatio.default"
      />
    </template>
  </Label>
</template>
