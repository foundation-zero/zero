<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { RiDropLine } from "@remixicon/vue";
import { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import ValueListItem from "./ValueListItem.vue";

const props = defineProps<{ value?: number; class?: HTMLAttributes["class"] }>();

const { t } = useI18n();
</script>

<template>
  <ValueListItem :class="props.class">
    <span class="flex items-center gap-0.5">
      <RiDropLine class="text-brand size-3.5" />
      {{ t("units.flow") }}
    </span>
    <span class="text-foreground font-medium">
      <AnimatedNumber :to="value" /> {{ t("units.lpm") }}
    </span>
  </ValueListItem>
</template>
