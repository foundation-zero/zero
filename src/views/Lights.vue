<script setup lang="ts">
import LightGroup from "@/components/ui/lights-list/LightGroup.vue";
import { useRoomStore } from "@/stores/rooms";
import { toRefs } from "vue";

const { currentRoom } = toRefs(useRoomStore());
</script>

<template>
  <section
    class="container grid grid-cols-1 gap-6 px-6 max-md:pb-[96px] md:grid-cols-2 md:pb-[32px] xl:grid-cols-3 landscape:lg:grid-cols-3"
  >
    <LightGroup
      v-for="(group, index) in currentRoom.lights"
      :key="index"
      :name="group.name"
      :lights="group.controls"
    />
  </section>
</template>
