import { BeforeResolveGuard } from "@/modules/domestic/router/guards";
import { useRoomStore } from "@/modules/domestic/stores/rooms";
import { toRefs, watch } from "vue";

export const waitForRoom: BeforeResolveGuard = (to) => {
  const roomId = to.query.room ?? to.params.room;

  if (roomId) {
    return new Promise((resolve) => {
      const store = useRoomStore();
      const { currentRoom } = toRefs(store);

      if (currentRoom.value.id === to.query.room) {
        resolve();
        return;
      } else {
        watch(
          currentRoom,
          (next) => {
            const invalidRoute =
              (to.name === "cabin:blinds" && next.blinds.length === 0) ||
              (to.name === "cabin:lights" && next.lightingGroups.length === 0);

            resolve({
              name: invalidRoute ? "cabin:air-conditioning" : to.name,
              query: to.query.returnUrl ? { returnUrl: to.query.returnUrl.toString() } : {},
            });
          },
          { once: true },
        );

        useRoomStore().setRoom(String(roomId));
      }
    });
  }
};
