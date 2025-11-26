<script setup lang="ts">
import { ValidationStatus } from "@/modules/domestic/types";
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
      'text-constructive': state === ValidationStatus.OK,
      'text-warning': state === ValidationStatus.WARN,
      'text-destructive': state === ValidationStatus.FAIL,
      'text-foreground-disabled': state === ValidationStatus.UNKNOWN,
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
        'text-warning': state === ValidationStatus.WARN,
        'text-destructive': state === ValidationStatus.FAIL,
        'text-foreground-disabled': state === ValidationStatus.UNKNOWN,
      }"
    />
  </template>
</template>
