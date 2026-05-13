<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps, useRandomizedNumber } from ".";
import { Label } from "../components/label";

defineProps<MimicComponentInstanceProps>();

const { t } = useI18n();

const value = useRandomizedNumber(4, 80);
</script>

<template>
  <Label
    :x="x"
    :y="y"
  >
    {{ tagId }}
    <template #value>
      <AnimatedNumber
        :to="value"
        :fraction-digits="0"
      />
      <span>{{ t("units.celsius") }}</span>
    </template>
  </Label>
</template>
