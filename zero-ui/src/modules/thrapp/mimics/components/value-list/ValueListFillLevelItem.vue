<script setup lang="ts">
import { formatInt } from "@/modules/common/lib/utils";
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { RiWaterPercentLine } from "@remixicon/vue";
import { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import ValueListItem from "./ValueListItem.vue";

const props = defineProps<{ value: number; class?: HTMLAttributes["class"] }>();

const { t } = useI18n();
</script>

<template>
  <ValueListItem :class="props.class">
    <span class="flex items-center gap-0.5">
      <RiWaterPercentLine class="text-brand size-3.5" />
      {{ t("units.level") }}
    </span>
    <span class="text-foreground font-medium">
      <AnimatedNumber
        :to="value"
        :format="formatInt"
      />&percnt;
    </span>
  </ValueListItem>
</template>
