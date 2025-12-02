<script setup lang="ts">
import { cn, tScoped } from "@/modules/common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import type { PrimitiveProps } from "reka-ui";
import type { HTMLAttributes } from "vue";
import { type IndicatorLightVariants } from "../indicator-light";
import MastLockLabel from "./MastLockLabel.vue";
import MastLockPosition from "./MastLockPosition.vue";

const props = defineProps<
  PrimitiveProps & {
    locked?: IndicatorLightVariants["variant"];
    overhoist?: IndicatorLightVariants["variant"];
    class?: HTMLAttributes["class"];
  }
>();

const $t = tScoped("loads.components.mastLock");

const delegatedProps = reactiveOmit(props, "class");
</script>

<template>
  <div
    data-slot="mast-lock"
    v-bind="delegatedProps"
    :class="
      cn(
        'bg-background border-border-subtle flex h-60 w-24 flex-col items-center justify-center rounded-xs border px-2 py-5',
        props.class,
      )
    "
  >
    <MastLockPosition :status="locked">
      {{ $t("locked") }}
    </MastLockPosition>
    <MastLockPosition :status="overhoist">
      {{ $t("overhoist") }}
    </MastLockPosition>
    <MastLockLabel>
      <slot />
    </MastLockLabel>
  </div>
</template>
