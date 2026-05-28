<script setup lang="ts">
import { formatNumber, toSignedNumber } from "@/modules/common/lib/utils";
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { RiFireLine } from "@remixicon/vue";
import { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import ValueListItem from "./ValueListItem.vue";

const props = defineProps<{ value?: number; class?: HTMLAttributes["class"] }>();

const { t } = useI18n();
</script>

<template>
  <ValueListItem :class="props.class">
    <span class="flex items-center gap-0.5">
      <RiFireLine class="text-heating-medium size-3.5" />
    </span>
    <span class="text-foreground font-medium">
      <AnimatedNumber
        :to="value"
        :format="toSignedNumber(formatNumber(1))"
      />
      {{ t("units.kilowatt") }}
    </span>
  </ValueListItem>
</template>
