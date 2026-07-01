<script setup lang="ts">
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@common/lib/utils";
import type { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <Textarea
    data-slot="input-group-control"
    :class="
      cn(
        'bg-muted flex-1 resize-none rounded-none border-0 py-3 shadow-none ring-offset-transparent focus-visible:ring-0 focus-visible:ring-transparent',
        props.class,
      )
    "
  />
</template>
