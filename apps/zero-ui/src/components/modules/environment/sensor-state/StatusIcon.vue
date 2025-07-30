<script setup lang="ts">
import { ValidationStatus } from "@/@types";
import { ExclamationTriangleIcon } from "@radix-icons/vue";
import { CheckCircle2 } from "lucide-vue-next";
import { type Component } from "vue";

defineProps<{ state: ValidationStatus; icon?: Component }>();
</script>

<template>
  <component
    :is="icon"
    v-if="icon"
    :size="16"
    :class="{
      'text-green-500/90': state === ValidationStatus.OK,
      'text-yellow-500/90': state === ValidationStatus.WARN,
      'text-red-500/90': state === ValidationStatus.FAIL,
      'text-primary/20': state === ValidationStatus.UNKNOWN,
    }"
  />
  <template v-else>
    <CheckCircle2
      v-if="state === ValidationStatus.OK"
      :size="16"
      class="text-green-500/90"
    />
    <ExclamationTriangleIcon
      v-else
      :size="16"
      :class="{
        'text-yellow-500/90': state === ValidationStatus.WARN,
        'text-red-500/90': state === ValidationStatus.FAIL,
        'text-primary/20': state === ValidationStatus.UNKNOWN,
      }"
    />
  </template>
</template>
