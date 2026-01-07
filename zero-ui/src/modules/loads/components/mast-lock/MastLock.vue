<script setup lang="ts">
import { cn, tScoped } from "@/modules/common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import type { PrimitiveProps } from "reka-ui";
import type { HTMLAttributes } from "vue";
import { MastLockState } from "../../types";
import { Card } from "../card";
import MastLockLabel from "./MastLockLabel.vue";
import MastLockPosition from "./MastLockPosition.vue";

const props = defineProps<
  PrimitiveProps & {
    locked?: MastLockState;
    overhoist?: MastLockState;
    class?: HTMLAttributes["class"];
  }
>();

const $t = tScoped("loads.components.mastLock");

const delegatedProps = reactiveOmit(props, "class");
</script>

<template>
  <Card
    data-slot="mast-lock"
    v-bind="delegatedProps"
    :class="cn('h-[13.375rem] justify-between px-2 py-5', props.class)"
  >
    <MastLockPosition
      class="w-full"
      :state="locked"
    >
      {{ $t("locked") }}
    </MastLockPosition>
    <MastLockPosition
      class="mt-1.5"
      :state="overhoist"
    >
      {{ $t("overhoist") }}
    </MastLockPosition>
    <MastLockLabel>
      <slot />
    </MastLockLabel>
  </Card>
</template>
