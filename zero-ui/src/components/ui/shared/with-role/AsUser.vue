<script setup lang="ts">
import { Roles } from "@/@types";
import WithRole from "./WithRole.vue";
</script>

<template>
  <WithRole :role="Roles.User">
    <slot />
    <template #fallback>
      <slot name="fallback" />
    </template>
  </WithRole>
</template>
