<script setup lang="ts">
import { cn, tScoped } from "@/modules/common/lib/utils";
import { RiInfinityLine } from "@remixicon/vue";
import type { HTMLAttributes } from "vue";

const t = tScoped("thrapp.mimics.boilerTankController.modes");

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <div
    :class="
      cn(
        'text-inverse-foreground bg-attention inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-sm font-medium',
        props.class,
      )
    "
  >
    <RiInfinityLine class="size-4" />
    {{ t("ALWAYS") }}
  </div>
</template>
