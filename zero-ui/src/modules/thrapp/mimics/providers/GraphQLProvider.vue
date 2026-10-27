<script setup lang="ts">
import { createMimicDataProvider } from ".";
import { useGraphQLDataProvider } from "./provider.graphql";

createMimicDataProvider(useGraphQLDataProvider());
</script>

<template>
  <slot />
</template>
