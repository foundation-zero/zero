import { BlindsGroup, Room, RoomGroup, ShipArea } from "@/@types";
import { Rooms } from "@/gql/graphql";
import { compareByName, isDefined } from "./utils";

export const toRoom = (room: Rooms): Room => ({
  ...room,
  group: room.group as RoomGroup,
  blinds: Object.values(Object.groupBy(room.blinds ?? [], ({ group }) => group))
    .filter(isDefined)
    .map<BlindsGroup>((blinds) => ({
      name: blinds[0].name!,
      controls: blinds.map((blind) => ({
        ...blind,
        name: blind.opacity === "blind" ? "Blinds" : "Shears",
      })),
    }))
    .sort(compareByName),
  lights: [
    {
      name: "Lights",
      controls: (room.lightingGroups ?? []).sort(compareByName),
    },
  ],
});

export const createArea = (group: RoomGroup, name: string, allRooms: Room[]): ShipArea => {
  return {
    name,
    group,
    rooms: allRooms.filter((room) => room.group === group).sort(compareByName),
  };
};
