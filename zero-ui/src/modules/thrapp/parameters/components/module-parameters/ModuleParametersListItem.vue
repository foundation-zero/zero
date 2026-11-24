<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { provideMultiLineEditor } from "@modules/thrapp/mimics/editors";
import { ModuleField } from "@modules/thrapp/mimics/providers";
import { injectValueForm } from "@modules/thrapp/mimics/providers/forms";
import { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  multiline?: boolean;
  /** The parameter edited here, which a manual's link selects by its field name. */
  source?: ModuleField;
}>();

provideMultiLineEditor(!!props.multiline);

const form = injectValueForm();
</script>

<template>
  <li
    :data-parameter="source?.[2]"
    :class="
      cn('border-border-subtle text-muted-foreground flex border-b py-2 text-sm', props.class, {
        'flex-col items-start gap-1 pt-1': props.multiline,
        'items-center justify-between': !props.multiline,
      })
    "
  >
    <slot />
    <span
      v-if="form?.error.value"
      class="text-destructive text-xs"
    >
      {{ form?.error.value }}
    </span>
  </li>
</template>
