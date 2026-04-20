import { useRoomStore } from "@/modules/domestic/stores/rooms";
import { Room } from "@/modules/domestic/types";
import { computed, Ref } from "vue";

export const useToggleableLights = (rooms: Ref<Room[]>) => {
  const groups = computed(() => rooms.value.flatMap((room) => room.lightingGroups));

  const someLightsAreOn = computed(() => groups.value.some((group) => group.level > 0));

  const store = useRoomStore();
  const toggle = () =>
    store.setLightingGroupsLevel(
      groups.value.map((group) => group.id),
      someLightsAreOn.value ? 0 : 1,
    );

  return { toggle, someLightsAreOn, groups };
};
