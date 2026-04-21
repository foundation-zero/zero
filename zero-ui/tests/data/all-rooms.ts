import { DomesticRooms } from "@/modules/domestic/graphql/types.generated";
import { Room, RoomGroup } from "../../src/modules/domestic/types";
import allRooms from "./all-rooms.json" with { type: "json" };

const toRoom = (room: DomesticRooms): Room => ({
  ...room,
  group: room.group as RoomGroup,
});

export const rooms: Room[] = (allRooms.rooms as DomesticRooms[]).map(toRoom);

export default { rooms };
