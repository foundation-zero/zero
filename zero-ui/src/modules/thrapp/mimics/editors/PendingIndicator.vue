<script setup lang="ts">
import { RiLoader2Line } from "@remixicon/vue";
import { injectValueForm } from "../providers/forms";

const form = injectValueForm();
</script>

<template>
  <RiLoader2Line
    v-if="form?.isPending.value"
    class="size-4 animate-spin"
  />
</template>
