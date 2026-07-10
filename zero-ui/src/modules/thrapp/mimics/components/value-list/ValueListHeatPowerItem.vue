<script setup lang="ts">
import { formatNumber, toSignedNumber } from "@/modules/common/lib/utils";
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { RiFireLine } from "@remixicon/vue";
import { computed, HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import ValueListItem from "./ValueListItem.vue";

const props = defineProps<{ value?: number; class?: HTMLAttributes["class"] }>();

const valueInKilowatts = computed(() => {
  if (props.value === undefined) return undefined;
  return props.value / 1000;
});
const { t } = useI18n();
</script>

<template>
  <ValueListItem :class="props.class">
    <span class="flex items-center gap-0.5">
      <RiFireLine class="text-heating-medium size-3.5" />
    </span>
    <span class="text-foreground font-medium">
      <AnimatedNumber
        :to="valueInKilowatts"
        :format="toSignedNumber(formatNumber(1))"
      />
      {{ t("units.kilowatt") }}
    </span>
  </ValueListItem>
</template>
