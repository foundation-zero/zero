import { BlindsGroup, Room, RoomGroup, ShipArea } from "@/@types";
import { QueryRoot, Rooms } from "@/gql/graphql";
import client from "@/graphql/client";
import { getAll } from "@/graphql/queries/rooms";
import { isDefined } from "@/lib/utils";
import { defineStore } from "pinia";
import { computed, ref, watch } from "vue";

const createArea = (group: RoomGroup, name: string, allRooms: Rooms[]): ShipArea => {
  return {
    name,
    group,
    rooms: allRooms
      .filter((room) => (room.group as unknown) === group)
      .map((room) => {
        return {
          id: room.id,
          name: room.name!,
          blinds: Object.values(Object.groupBy(room.blinds, ({ group }) => group))
            .filter(isDefined)
            .map<BlindsGroup>((blinds) => ({
              name: blinds[0].name!,
              controls: blinds.map((blind) => ({
                ...blind,
                name: blind.opacity === "blind" ? "Blinds" : "Shears",
                level: blind.level ?? 0,
              })),
            })),
          lights: [
            {
              name: "Lights",
              controls: room.lighting_groups.map((light) => ({
                ...light,
                level: light.level ?? 0,
              })),
            },
          ],
        };
      }),
  };
};

type GetAllRoomsQuery = Pick<QueryRoot, "rooms">;

const EMPTY_ROOM: Room = {
  name: "Empty",
  blinds: [],
  lights: [],
  id: "empty",
};

export const useRoomStore = defineStore("rooms", () => {
  const currentRoom = ref<Room>(EMPTY_ROOM);

  const setRoom = (room: Room) => (currentRoom.value = room);
  client.query<GetAllRoomsQuery>(getAll, {});

  const rooms = ref<Rooms[]>([]);

  const init = async () => {
    const response = await client.query<GetAllRoomsQuery>(getAll, {});

    rooms.value = response.data?.rooms ?? [];
  };

  const areas = computed<ShipArea[]>(() => {
    return [
      createArea(RoomGroup.AFT, "Aftship", rooms.value),
      createArea(RoomGroup.MID, "Midship", rooms.value),
      createArea(RoomGroup.FORE, "Foreship", rooms.value),
      createArea(RoomGroup.UPPERDECK, "Upperdeck", rooms.value),
      createArea(RoomGroup.HALLWAYS, "Hallways", rooms.value),
    ];
  });

  watch(areas, () => {
    currentRoom.value = areas.value[0].rooms[4] ?? EMPTY_ROOM;
  });

  init();

  return { areas, rooms, currentRoom, setRoom, init };
});
