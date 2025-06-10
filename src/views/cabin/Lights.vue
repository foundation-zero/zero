<script setup lang="ts">
import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";
import LightGroup from "@components/shared/lights-list/LightGroup.vue";
import { toRefs } from "vue";

const roomStore = useRoomStore();
const { currentRoom } = toRefs(roomStore);
const { breakpoints } = toRefs(useUIStore());
const { setLightLevel } = roomStore;
</script>

<template>
  <section
    class="grid grid-cols-1 gap-6 px-4 max-md:pb-[96px] md:grid-cols-2 md:px-6 md:pb-[32px] xl:grid-cols-3 landscape:lg:grid-cols-3"
    :class="{
      'xl:container max-xl:w-full xl:px-0': !breakpoints.touch,
      'w-full': breakpoints.touch,
    }"
  >
    <LightGroup
      v-for="(group, index) in currentRoom.lights"
      :key="index"
      :name="group.name"
      :lights="group.controls"
      @update:level="setLightLevel"
    />
  </section>
</template>
