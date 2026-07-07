<script setup lang="ts">
import { injectHideEditorIfNotEditable, injectValueForm } from "../providers/forms";

const form = injectValueForm();
const hideEditorIfNotEditable = injectHideEditorIfNotEditable();
</script>

<template>
  <slot
    v-if="form?.isEditable.value || !hideEditorIfNotEditable"
    name="editor"
  />
  <slot v-else />
</template>
