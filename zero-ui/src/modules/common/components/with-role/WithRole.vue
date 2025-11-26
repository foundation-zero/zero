<script setup lang="ts">
import { useAuthStore } from "@/modules/domestic/stores/auth";
import { Roles } from "@/modules/domestic/types";

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
