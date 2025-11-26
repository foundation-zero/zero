<script setup lang="ts">
import { groupLights } from "@/modules/domestic/lib/mappers";
import { useRoomStore } from "@/modules/domestic/stores/rooms";
import { LightingControl } from "@/modules/domestic/types";
import LightGroup from "@common/components/lights-list/LightGroup.vue";
import { isLightControl } from "@common/lib/utils";
import { useUIStore } from "@common/stores/ui";

import { computed, provide, Ref, toRefs, watch } from "vue";

const roomStore = useRoomStore();
const { currentRoom, hasPendingRequests } = toRefs(roomStore);
const { breakpoints } = toRefs(useUIStore());

const lights = computed(() => groupLights(currentRoom.value.roomsControls.filter(isLightControl)));

const commit = async (control: LightingControl, brightness: Ref<number>) => {
  if (hasPendingRequests.value) return;

  await roomStore.setLightLevel(control.id, brightness.value);

  if (!hasPendingRequests.value) return;

  watch(hasPendingRequests, () => (brightness.value = control.value), {
    once: true,
  });
};

provide("commit", commit);
</script>

<template>
  <section
    class="grid grid-cols-1 gap-6 px-4 max-md:pb-[96px] md:grid-cols-2 md:px-6 md:pb-[32px] xl:grid-cols-3 landscape:lg:grid-cols-3"
    :class="{
      'max-xl:w-full xl:container xl:px-0': !breakpoints.touch,
      'w-full': breakpoints.touch,
    }"
  >
    <LightGroup
      v-for="(group, index) in lights"
      :key="index"
      :group="group"
    />
  </section>
</template>
