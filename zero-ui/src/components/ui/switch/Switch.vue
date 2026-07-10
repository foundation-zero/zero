<script setup lang="ts">
import { cn } from "@common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import {
  SwitchRoot,
  type SwitchRootEmits,
  type SwitchRootProps,
  SwitchThumb,
  useForwardPropsEmits,
} from "reka-ui";
import type { HTMLAttributes } from "vue";

const props = defineProps<SwitchRootProps & { class?: HTMLAttributes["class"] }>();

const emits = defineEmits<SwitchRootEmits>();

const delegatedProps = reactiveOmit(props, "class");

const forwarded = useForwardPropsEmits(delegatedProps, emits);
</script>

<template>
  <SwitchRoot
    data-slot="switch"
    v-bind="forwarded"
    :class="
      cn(
        'peer bg-dull focus-visible:border-ring focus-visible:ring-ring/50 border-border inline-flex h-[1.15rem] w-8 shrink-0 items-center rounded-full border shadow-xs transition-all outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50',
        props.class,
      )
    "
  >
    <slot />
    <SwitchThumb
      data-slot="switch-thumb"
      :class="
        cn(
          'bg-background data-[state=unchecked]:bg-muted-foreground data-[state=checked]:bg-attention pointer-events-none block size-3 rounded-full ring-0 transition-transform data-[state=checked]:translate-x-[calc(100%+3.5px)] data-[state=unchecked]:translate-x-0.5',
        )
      "
    >
      <slot name="thumb" />
    </SwitchThumb>
  </SwitchRoot>
</template>
