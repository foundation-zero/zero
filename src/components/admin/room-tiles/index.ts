import { Room } from "@/@types";
import { useRoomStore } from "@/stores/rooms";
import { computed, Ref } from "vue";

export const useToggleableLights = (rooms: Ref<Room[]>) => {
  const controls = computed(() =>
    rooms.value.flatMap((room) => room.lights.flatMap((group) => group.controls)),
  );
  const someLightsAreOn = computed(() => controls.value.some((control) => control.level > 0));

  const store = useRoomStore();
  const toggle = () =>
    store.setLightingGroupsLevel(
      controls.value.map((control) => control.id),
      someLightsAreOn.value ? 0 : 1,
    );

  return { toggle, someLightsAreOn, controls };
};
