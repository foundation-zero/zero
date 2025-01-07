import { LightControl, Room, ShipArea } from "@/@types";
import { defineStore } from "pinia";
import { ref } from "vue";

const toControl = (name: string): LightControl => ({
  name,
  on: true,
  brightness: Math.random() * 100,
});
const createLights = (): LightControl[] => ["Main", "Ambient"].map(toControl);
const createRooms = (...names: string[]): Room[] =>
  names.map((name) => ({ name, lights: createLights() }));

const areas: ShipArea[] = [
  {
    name: "Aftship",
    rooms: createRooms(
      "Owners cabin",
      "Dutch cabin",
      "French cabin",
      "Italian cabin",
      "Californian cabin",
    ),
  },
  {
    name: "Midship",
    rooms: createRooms(
      "Polynesian cabin",
      "Galley",
      "Crew mess",
      "Mission room",
      "Laundry",
      "Engineers office",
    ),
  },
  {
    name: "Foreship",
    rooms: createRooms(
      "Captains cabin",
      "Crew SB AFT cabin",
      "Crew SB MID cabin",
      "Crew SB FWD cabin",
      "Crew PS MID cabin",
      "Crew PS FWD cabin",
    ),
  },
  {
    name: "Upperdeck",
    rooms: createRooms("Owners deckhouse", "Main deckhouse"),
  },
  {
    name: "Hallways",
    rooms: createRooms("Owners stairway", "Guest corridor", "Polynesian corridor"),
  },
];

export const useRoomStore = defineStore("rooms", () => {
  const currentRoom = ref(areas[0].rooms[4]);
  const scrollPosition = ref(0);

  const setRoom = (room: Room) => (currentRoom.value = room);

  const setScrollPosition = (val: number) => (scrollPosition.value = val);

  return { areas, currentRoom, setRoom, scrollPosition, setScrollPosition };
});
