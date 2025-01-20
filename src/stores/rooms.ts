import { BlindsGroup, LightGroup, Room, ShipArea } from "@/@types";
import { toBlindsGroup, toLightGroup } from "@/lib/mappers";
import { defineStore } from "pinia";
import { ref } from "vue";

const defaultLightsFn = (groupNames = ["Main"]): LightGroup[] =>
  groupNames.map(toLightGroup("Main", "Ambient"));
const defaultBlindsFn = (groupNames: string[] = ["Main"]): BlindsGroup[] =>
  groupNames.map(toBlindsGroup("Blinds"));
const blindsAndSheersFn = (...groupNames: string[]): BlindsGroup[] =>
  groupNames.map(toBlindsGroup("Blinds", "Sheers"));

type RoomDef = [name: string, lightGroups?: LightGroup[], blindsGroups?: BlindsGroup[]];

const createRooms = (...defs: RoomDef[]): Room[] =>
  defs.map(([name, lights = defaultLightsFn(), blinds = defaultBlindsFn()]) => ({
    name,
    lights,
    blinds,
  }));

const areas: ShipArea[] = [
  {
    name: "Aftship",
    rooms: createRooms(
      [
        "Owners cabin",
        defaultLightsFn(),
        blindsAndSheersFn(
          "Main",
          "Skyline (main)",
          "Port",
          "Skyline (port)",
          "Starboard",
          "Skyline (starboard)",
        ),
      ],
      ["Dutch cabin"],
      ["French cabin"],
      ["Italian cabin"],
      ["Californian cabin"],
    ),
  },
  {
    name: "Midship",
    rooms: createRooms(
      ["Polynesian cabin"],
      ["Galley"],
      ["Crew mess"],
      ["Mission room"],
      ["Laundry"],
      ["Engineers office"],
    ),
  },
  {
    name: "Foreship",
    rooms: createRooms(
      ["Captains cabin"],
      ["Crew SB AFT cabin"],
      ["Crew SB MID cabin"],
      ["Crew SB FWD cabin"],
      ["Crew PS MID cabin"],
      ["Crew PS FWD cabin"],
    ),
  },
  {
    name: "Upperdeck",
    rooms: createRooms(
      ["Owners deckhouse", defaultLightsFn(), [toBlindsGroup("Port", "Starboard")("Blinds")]],
      ["Main deckhouse", defaultLightsFn(), [toBlindsGroup("Port", "Starboard")("Blinds")]],
    ),
  },
  {
    name: "Hallways",
    rooms: createRooms(["Owners stairway"], ["Guest corridor"], ["Polynesian corridor"]),
  },
];

export const useRoomStore = defineStore("rooms", () => {
  const currentRoom = ref(areas[0].rooms[4]);

  const setRoom = (room: Room) => (currentRoom.value = room);

  return { areas, currentRoom, setRoom };
});
