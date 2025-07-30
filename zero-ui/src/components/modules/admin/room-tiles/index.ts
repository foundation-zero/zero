import { Room } from "@/@types";
import { isLightControl } from "@/lib/utils";
import { useRoomStore } from "@/stores/rooms";
import { computed, Ref } from "vue";

export const useToggleableLights = (rooms: Ref<Room[]>) => {
  const controls = computed(() =>
    rooms.value.flatMap((room) => room.roomsControls.filter(isLightControl)),
  );

  const someLightsAreOn = computed(() => controls.value.some((control) => control.value > 0));

  const store = useRoomStore();
  const toggle = () =>
    store.setLightingGroupsLevel(
      controls.value.map((control) => control.id),
      someLightsAreOn.value ? 0 : 1,
    );

  return { toggle, someLightsAreOn, controls };
};
