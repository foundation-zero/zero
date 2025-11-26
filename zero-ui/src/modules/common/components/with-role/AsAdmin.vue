<script setup lang="ts">
import { Roles } from "@/modules/domestic/types";
import WithRole from "./WithRole.vue";
</script>

<template>
  <WithRole :role="Roles.Admin">
    <slot />
    <template #fallback>
      <slot name="fallback" />
    </template>
  </WithRole>
</template>
