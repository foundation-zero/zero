<script setup lang="ts">
import { cn, tScoped } from "@/modules/common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import type { PrimitiveProps } from "reka-ui";
import type { HTMLAttributes } from "vue";
import type { MastLockState } from "../../types";
import { Card } from "../card";
import MastLockLabel from "../mast-lock/MastLockLabel.vue";
import MastLockCompactPosition from "./MastLockCompactPosition.vue";

const props = defineProps<
  PrimitiveProps & {
    locked?: MastLockState;
    overhoist?: MastLockState;
    class?: HTMLAttributes["class"];
  }
>();

const t = tScoped("loads.components.mastLock");

const delegatedProps = reactiveOmit(props, "class");
</script>

<template>
  <Card
    data-slot="mast-lock-compact"
    v-bind="delegatedProps"
    :class="cn('h-33.25 w-37 max-w-full justify-between px-2 py-2', props.class)"
  >
    <MastLockLabel class="text-foreground w-full">
      <slot />
    </MastLockLabel>

    <div class="flex w-full flex-col pb-1">
      <MastLockCompactPosition
        :state="overhoist"
        :class="{ invisible: overhoist == undefined }"
      >
        {{ t("overhoist") }}
      </MastLockCompactPosition>

      <hr class="border-border-subtle my-2 w-full" />

      <MastLockCompactPosition :state="locked">
        {{ t("locked") }}
      </MastLockCompactPosition>
    </div>
  </Card>
</template>
