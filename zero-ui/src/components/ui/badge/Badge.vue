<script setup lang="ts">
import { cn } from "@common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import type { PrimitiveProps } from "reka-ui";
import { Primitive } from "reka-ui";
import type { HTMLAttributes } from "vue";
import type { BadgeTypes, BadgeVariants } from ".";
import { badgeTypes, badgeVariants } from ".";

const props = defineProps<
  PrimitiveProps & {
    variant?: BadgeVariants["variant"];
    class?: HTMLAttributes["class"];
    type?: BadgeTypes["variant"];
  }
>();

const delegatedProps = reactiveOmit(props, "class");
</script>

<template>
  <Primitive
    data-slot="badge"
    :class="cn(badgeVariants({ variant }), badgeTypes({ variant: type }), props.class)"
    v-bind="delegatedProps"
  >
    <slot />
  </Primitive>
</template>
