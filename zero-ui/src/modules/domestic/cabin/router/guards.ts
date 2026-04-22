import { BeforeResolveGuard } from "@/modules/domestic/router/guards";
import { useRoomStore } from "@/modules/domestic/stores/rooms";
import { isBlindsControl, isLightControl } from "@common/lib/utils";
import { toRefs, watch } from "vue";

export const waitForRoom: BeforeResolveGuard = (to) => {
  const roomId = to.query.room ?? to.params.room;

  if (roomId) {
    return new Promise((resolve) => {
      const store = useRoomStore();
      const { currentRoom } = toRefs(store);

      watch(
        currentRoom,
        (next) => {
          const invalidRoute =
            (to.name === "cabin:blinds" &&
              next.roomControls.filter(isBlindsControl).length === 0) ||
            (to.name === "cabin:lights" && next.roomControls.filter(isLightControl).length === 0);

          resolve({
            name: invalidRoute ? "cabin:airconditioning" : to.name,
            query: to.query.returnUrl ? { returnUrl: to.query.returnUrl.toString() } : {},
          });
        },
        { once: true },
      );

      useRoomStore().setRoom(String(roomId));
    });
  }
};
