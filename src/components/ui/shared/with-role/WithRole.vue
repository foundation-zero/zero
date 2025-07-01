<script setup lang="ts">
import { Roles } from "@/@types";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();

const props = defineProps<{ role: Roles }>();

const hasRole = auth.hasRole(props.role);
</script>

<template>
  <slot v-if="hasRole" />
  <slot
    v-else
    name="fallback"
  />
</template>
