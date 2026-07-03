<script setup lang="ts">
import { useAutomaticMode } from "../../state";
import { injectControlValueForm } from "../providers/forms";

const isAutomaticMode = useAutomaticMode();
const form = injectControlValueForm();
</script>

<template>
  <slot
    v-if="!isAutomaticMode && form?.editable.value"
    name="editor"
  />
  <slot v-else />
</template>
