<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { computed, HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import TooltipListItemValue from "./TooltipListItemValue.vue";

const props = defineProps<{
  value?: number;
  class?: HTMLAttributes["class"];
}>();
const seconds = computed(() => (props.value == undefined ? undefined : props.value % 60));
const minutes = computed(() =>
  props.value == undefined ? undefined : Math.floor(props.value / 60),
);

const { t } = useI18n();
</script>

<template>
  <TooltipListItemValue :class="props.class">
    <AnimatedNumber
      :to="minutes"
      :fraction-digits="0"
    />
    {{ t("units.minutes") }}
    <AnimatedNumber
      :to="seconds"
      :fraction-digits="0"
    />
    {{ t("units.seconds") }}
  </TooltipListItemValue>
</template>
