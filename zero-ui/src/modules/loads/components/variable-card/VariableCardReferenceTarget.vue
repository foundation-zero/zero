<script setup lang="ts">
import { getContext } from ".";
import ReferenceBox from "../reference-box/ReferenceBox.vue";
import ReferenceBoxValue from "../reference-box/ReferenceBoxValue.vue";

const { thresholds, type } = getContext();

import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <ReferenceBox :class="cn({ invisible: !thresholds?.target }, props.class)">
    <ReferenceBoxValue
      :value="thresholds?.target"
      :type="type"
    />
    <slot />
  </ReferenceBox>
</template>
