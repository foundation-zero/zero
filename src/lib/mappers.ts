import { BlindsGroup, Room, RoomGroup, ShipArea } from "@/@types";
import { Rooms } from "@/gql/graphql";
import i18n from "@/i18n";
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
        name:
          blind.opacity === "blind"
            ? i18n.global.t("labels.blinds")
            : i18n.global.t("labels.shears"),
      })),
    }))
    .sort(compareByName),
  lights: [
    {
      name: i18n.global.t("labels.lights"),
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
