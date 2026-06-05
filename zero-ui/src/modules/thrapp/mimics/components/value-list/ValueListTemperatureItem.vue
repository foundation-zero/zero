<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { RiTempColdLine } from "@remixicon/vue";
import { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import ValueListItem from "./ValueListItem.vue";

const props = defineProps<{
  temperature?: number;
  setpoint?: number;
  class?: HTMLAttributes["class"];
}>();

const { t } = useI18n();
</script>

<template>
  <ValueListItem :class="props.class">
    <span class="flex items-center gap-0.5">
      <slot>
        <RiTempColdLine class="text-heating-medium size-3.5" />
        {{ t("units.temperature") }}
      </slot>
    </span>
    <span class="text-foreground font-medium">
      <AnimatedNumber :to="temperature" />
      <span v-if="temperature != undefined && setpoint != undefined">/</span>
      <AnimatedNumber
        v-if="setpoint != undefined"
        :to="setpoint"
      />
      {{ t("units.celsius") }}
    </span>
  </ValueListItem>
</template>
