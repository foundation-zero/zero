import { isBlindsControl, isLightControl } from "@/lib/utils";
import { useRoomStore } from "@/stores/rooms";
import { toRefs, watch } from "vue";
import { BeforeResolveGuard } from "../guards";

export const waitForRoom: BeforeResolveGuard = (to) => {
  if (to.query.room) {
    return new Promise((resolve) => {
      const store = useRoomStore();
      const { currentRoom } = toRefs(store);

      watch(
        currentRoom,
        (next) => {
          const invalidRoute =
            (to.name === "cabin:blinds" &&
              next.roomsControls.filter(isBlindsControl).length === 0) ||
            (to.name === "cabin:lights" && next.roomsControls.filter(isLightControl).length === 0);

          resolve({
            name: invalidRoute ? "cabin:airconditioning" : to.name,
            query: {},
          });
        },
        { once: true },
      );

      useRoomStore().setRoom(String(to.query.room));
    });
  }
};
