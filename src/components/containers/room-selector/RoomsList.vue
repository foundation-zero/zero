<script setup lang="ts">
import { Room } from "@/@types";
import { useRoomStore } from "@/stores/rooms";
import { toRefs } from "vue";
import List from "@/components/ui/list/List.vue";
import ListItem from "@/components/ui/list/ListItem.vue";
import { CircleArrowRight } from "lucide-vue-next";
import ListHeader from "@/components/ui/list/ListHeader.vue";

const { areas, currentRoom } = toRefs(useRoomStore());
const { setRoom } = useRoomStore();
const emit = defineEmits(["roomSelected"]);

const selectRoom = (room: Room) => {
  emit("roomSelected");
  setRoom(room);
};
</script>

<template>
  <div class="grid grid-cols-1 gap-8">
    <div
      v-for="area in areas"
      :key="area.name"
    >
      <ListHeader>{{ area.name }}</ListHeader>
      <List>
        <ListItem
          v-for="room in area.rooms"
          :key="room.name"
          :selected="currentRoom?.name === room.name"
          @click="selectRoom(room)"
        >
          <span>{{ room.name }}</span>

          <CircleArrowRight v-if="currentRoom?.name === room.name" />
        </ListItem>
      </List>
    </div>
  </div>
</template>
