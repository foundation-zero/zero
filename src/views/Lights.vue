<script setup lang="ts">
import { LightControl, Room } from "@/@types";
import LightGroup from "@/components/LightGroup.vue";
import { ref } from "vue";

const toDef = (name: string): LightControl => ({ name, on: true, brightness: Math.random() * 100 });

const rooms = ref<Room[]>([
  { name: "Bathroom", lights: ["Main light", "Ambient"].map(toDef) },
  { name: "Cabin", lights: ["Main light", "Ambient"].map(toDef) },
  { name: "Deck", lights: ["Main light", "Ambient"].map(toDef) },
]);
</script>

<template>
  <section class="container px-6 max-sm:pb-[96px] md:pb-[32px]">
    <div class="grid grid-cols-1 md:grid-cols-2 landscape:lg:grid-cols-3 xl:grid-cols-3 gap-6">
      <LightGroup
        v-for="(room, index) in rooms"
        :key="index"
        class="columns-1"
        :name="room.name"
        :lights="room.lights"
      />
    </div>
  </section>
</template>
