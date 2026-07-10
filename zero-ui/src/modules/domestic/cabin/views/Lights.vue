<script setup lang="ts">
import { groupLights } from "@/modules/domestic/lib/mappers";
import { useRoomStore } from "@/modules/domestic/stores/rooms";
import LightGroup from "@common/components/lights-list/LightGroup.vue";
import { useUIStore } from "@common/stores/ui";

import { LightingGroup } from "@/modules/domestic/types";
import { computed, provide, Ref, toRefs, watch } from "vue";

const roomStore = useRoomStore();
const { currentRoom, hasPendingRequests } = toRefs(roomStore);
const { breakpoints } = toRefs(useUIStore());

const lights = computed(() => groupLights(currentRoom.value.lightingGroups));

const commit = async (control: LightingGroup, brightness: Ref<number>) => {
  if (hasPendingRequests.value) return;

  await roomStore.setLightingGroupsLevel([control.id], brightness.value);

  if (!hasPendingRequests.value) return;

  watch(hasPendingRequests, () => (brightness.value = control.level), {
    once: true,
  });
};

provide("commit", commit);
</script>

<template>
  <section
    class="grid grid-cols-1 gap-6 px-4 max-md:pb-24 md:grid-cols-2 md:px-6 md:pb-8 xl:grid-cols-3 landscape:lg:grid-cols-3"
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
