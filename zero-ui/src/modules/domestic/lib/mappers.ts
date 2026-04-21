import i18n from "@/i18n";
import { BlindsGroup, LightGroup, Room, RoomGroup, ShipArea } from "@/modules/domestic/types";
import { compareByName, isDefined } from "../../common/lib/utils";
import { DomesticBlinds, DomesticLightingGroups } from "../gql/graphql";

export const createArea = (group: RoomGroup, name: string, allRooms: Room[]): ShipArea => {
  return {
    name,
    group,
    rooms: allRooms.filter((room) => room.group === group).sort(compareByName),
  };
};

export const groupBlindsByGroup = (blinds: DomesticBlinds[]): BlindsGroup[] =>
  Object.values(Object.groupBy(blinds ?? [], ({ name }) => (blinds.length > 2 ? name! : "blinds")))
    .filter(isDefined)
    .map<BlindsGroup>((blinds) => ({
      name: blinds[0].name!,
      controls: blinds.map((blind) => ({
        ...blind,
        value: Number(blind.level ?? 0),
        name: blind.id.includes("blind")
          ? i18n.global.t("labels.blinds")
          : i18n.global.t("labels.shears"),
      })),
    }));

export const groupLights = (lights: DomesticLightingGroups[]): LightGroup[] => [
  {
    name: i18n.global.t("labels.lights"),
    controls: lights.sort(compareByName),
  },
];

export const boolToInt = (value: boolean): number => (value ? 1 : 0);
