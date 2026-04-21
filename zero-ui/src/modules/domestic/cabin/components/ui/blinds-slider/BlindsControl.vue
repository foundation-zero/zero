<script setup lang="ts">
import { DomesticBlinds } from "@/modules/domestic/gql/graphql";
import { useRoomStore } from "@/modules/domestic/stores/rooms";
import { cn, writeProtected } from "@common/lib/utils";
import { HTMLAttributes, provide, ref, toRefs, watch } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  editable?: boolean;
  control: DomesticBlinds;
}>();

const { editable, control } = toRefs(props);
const targetLevel = ref(Number(props.control.level));
const { setBlindsLevel } = useRoomStore();
const { hasPendingRequests } = toRefs(useRoomStore());

provide("control", control);
provide("value", writeProtected(targetLevel, editable));
provide("commit", async () => {
  if (!editable.value) return;

  await setBlindsLevel(props.control.id, targetLevel.value);

  if (!hasPendingRequests.value) return;

  watch(hasPendingRequests, () => (targetLevel.value = Number(control.value.level)), {
    once: true,
  });
});
provide("disabled", hasPendingRequests);
provide("editable", editable);

watch(props, ({ control }) => {
  targetLevel.value = Number(control.level);
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
