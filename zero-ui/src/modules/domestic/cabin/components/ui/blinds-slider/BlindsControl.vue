<script setup lang="ts">
import { useRoomStore } from "@/modules/domestic/stores/rooms";
import { BlindsControl } from "@/modules/domestic/types";
import { cn, writeProtected } from "@common/lib/utils";
import { HTMLAttributes, provide, ref, toRefs, watch } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  editable?: boolean;
  control: BlindsControl;
}>();

const { editable, control } = toRefs(props);
const targetLevel = ref(Number(props.control.value));
const { setBlindsLevel } = useRoomStore();
const { hasPendingRequests } = toRefs(useRoomStore());

provide("control", control);
provide("value", writeProtected(targetLevel, editable));
provide("commit", async () => {
  if (!editable.value) return;

  await setBlindsLevel(props.control.id, targetLevel.value);

  if (!hasPendingRequests.value) return;

  watch(hasPendingRequests, () => (targetLevel.value = Number(control.value.value)), {
    once: true,
  });
});
provide("disabled", hasPendingRequests);
provide("editable", editable);

watch(props, ({ control }) => {
  targetLevel.value = Number(control.value);
});
</script>

<template>
  <div
    data-testid="blinds-control"
    :class="cn('flex flex-col items-center', $props.class)"
  >
    <slot />
  </div>
</template>
